import av
import threading
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class VideoDecoder(QThread):
    # 播放相关信号
    frame_ready = pyqtSignal(np.ndarray)
    frame_index_changed = pyqtSignal(int)
    log_msg = pyqtSignal(str)
    # 新增导出信号
    export_progress = pyqtSignal(int)
    export_finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.container = None
        self.stream = None
        self.total_frames = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        self.current_frame_idx = 0
        self._frame_generator = None  # 顺序解码迭代器
        self._is_playing = False
        self.play_speed = 1.0
        self._lock = threading.Lock()

    def open(self, file_path: str) -> bool:
        """打开视频文件，读取元信息"""
        try:
            self.container = av.open(file_path)
            self.stream = self.container.streams.video[0]
            # 读取基础信息
            self.fps = float(self.stream.average_rate)
            self.width = self.stream.codec_context.width
            self.height = self.stream.codec_context.height
            # 估算总帧数
            if self.stream.frames > 0:
                self.total_frames = self.stream.frames
            else:
                # 部分容器不存帧数量，粗略估算
                duration = self.container.duration / av.time_base
                self.total_frames = int(duration * self.fps)
            self.current_frame_idx = 0
            self._frame_generator = self.container.decode(video=0)
            self.log_msg.emit("视频元数据读取成功")
            return True
        except Exception as e:
            err_text = f"视频打开失败: {e}"
            print(err_text)
            self.log_msg.emit(err_text)
            self.close()
            return False

    def _reset_generator(self):
        """重置解码迭代器，seek到当前帧位置"""
        self.container.seek(int(self.current_frame_idx / self.fps * av.time_base), stream=self.stream)
        self._frame_generator = self.container.decode(video=0)

    def get_frame_by_index(self, target_idx: int) -> tuple[np.ndarray | None, int]:
        """
        跳到指定帧号（独立临时容器，不和播放generator争抢，修复generator already executing）
        返回RGB numpy帧 + 当前帧索引
        """
        if self.container is None or self.stream is None:
            return None, self.current_frame_idx
        if target_idx < 0 or target_idx >= self.total_frames:
            return None, self.current_frame_idx
        try:
            # 独立临时流，完全隔离播放线程的解码生成器
            temp_container = av.open(self.container.name)
            temp_stream = temp_container.streams.video[0]
            temp_container.seek(target_idx, stream=temp_stream)
            for idx, frame in enumerate(temp_container.decode(temp_stream)):
                if idx >= target_idx:
                    rgb_arr = frame.to_ndarray(format="rgb24")
                    temp_container.close()
                    self.current_frame_idx = target_idx
                    return rgb_arr.copy(), self.current_frame_idx
            temp_container.close()
            return None, self.current_frame_idx
        except Exception as e:
            self.log_msg.emit(f"跳转帧异常:{str(e)}")
            return None, self.current_frame_idx

    def get_next_frame(self) -> tuple[np.ndarray | None, int]:
        """下一帧，顺序读取，不seek"""
        if self.container is None or self.stream is None:
            return None, self.current_frame_idx
        if self.current_frame_idx >= self.total_frames - 1:
            return None, self.current_frame_idx
        try:
            frame = next(self._frame_generator)
            self.current_frame_idx += 1
            rgb_frame = frame.to_ndarray(format="rgb24")
            return rgb_frame.copy(), self.current_frame_idx
        except StopIteration:
            # 迭代器读完了，重置生成器再试一次
            self._reset_generator()
            try:
                frame = next(self._frame_generator)
                self.current_frame_idx += 1
                rgb_frame = frame.to_ndarray(format="rgb24")
                return rgb_frame.copy(), self.current_frame_idx
            except:
                return None, self.current_frame_idx

    def get_prev_frame(self) -> tuple[np.ndarray | None, int]:
        """上一帧：不支持回退迭代器，直接调用按帧号跳转"""
        if self.container is None or self.stream is None:
            return None, self.current_frame_idx
        if self.current_frame_idx <= 0:
            return None, self.current_frame_idx
        self.current_frame_idx -= 1
        return self.get_frame_by_index(self.current_frame_idx)

    # ===== 播放控制接口（给video_edit_page调用）=====
    def set_speed(self, speed):
        self.play_speed = speed

    def pause(self):
        with self._lock:
            self._is_playing = False

    def play(self):
        with self._lock:
            self._is_playing = True
            if not self.isRunning():
                self.start()

    def run(self):
        # QThread运行循环，播放时自动取帧，发射信号
        while self._is_playing:
            frame_np, idx = self.get_next_frame()
            if frame_np is None:
                self._is_playing = False
                self.log_msg.emit("播放到视频末尾，已暂停")
                break
            self.frame_ready.emit(frame_np)
            self.frame_index_changed.emit(idx)
            # 控制播放延时
            delay_ms = int(1000 / (self.fps * self.play_speed))
            self.msleep(delay_ms)

    def adjust_color(self, img, brightness, contrast, saturation):
        import cv2
        img = cv2.convertScaleAbs(img, alpha=1 + contrast/100, beta=brightness)
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[...,1] = hsv[...,1] * (1 + saturation / 100)
        hsv[...,1] = np.clip(hsv[...,1], 0, 255)
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        return img

    def export_clip(self, save_path, start_frame, end_frame, brightness=0, contrast=0, saturation=0, speed=1.0) -> bool:
        if self.container is None:
            self.log_msg.emit("❌ 没有加载视频")
            self.export_finished.emit(False)
            return False
        try:
            in_stream = self.container.streams.video[0]
            out_fps = self.fps / speed
            out_container = av.open(save_path, mode="w")
            out_stream = out_container.add_stream("libx264", rate=out_fps)
            out_stream.width = self.width
            out_stream.height = self.height
            out_stream.pix_fmt = "yuv420p"

            self.container.seek(start_frame, stream=in_stream)
            current = start_frame
            total = end_frame - start_frame
            self.log_msg.emit(f"⏳ 开始导出，总帧数：{total}")

            for packet in self.container.demux(in_stream):
                for frame in packet.decode():
                    if current < start_frame:
                        current +=1
                        continue
                    if current > end_frame:
                        break
                    # 调色
                    frame_np = frame.to_ndarray("rgb24")
                    frame_np = self.adjust_color(frame_np, brightness, contrast, saturation)
                    av_frame = av.VideoFrame.from_ndarray(frame_np, format="rgb24")
                    for pkt in out_stream.encode(av_frame):
                        out_container.mux(pkt)
                    # 进度百分比
                    progress = int(((current - start_frame)/total)*100)
                    self.export_progress.emit(progress)
                    self.log_msg.emit(f"PROGRESS:{progress}")
                    current +=1
                if current > end_frame:
                    break
            # 刷剩余缓存
            for pkt in out_stream.encode():
                out_container.mux(pkt)
            out_container.close()
            self.log_msg.emit("✅ 剪辑导出完成")
            self.export_finished.emit(True)
            return True
        except Exception as e:
            self.log_msg.emit(f"❌ 导出失败：{str(e)}")
            self.export_finished.emit(False)
            return False

    def close(self):
        """释放资源"""
        with self._lock:
            self._is_playing = False
        self.wait()
        if self.container is not None:
            self.container.close()
        self.container = None
        self.stream = None
        self._frame_generator = None
