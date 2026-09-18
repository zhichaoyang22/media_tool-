import av
import numpy as np
from PySide6.QtCore import QThread, Signal


class VideoProcessor(QThread):
    # 信号：进度值、日志文本、当前处理帧
    signal_progress = Signal(int)
    signal_log = Signal(str)
    signal_frame_preview = Signal(np.ndarray)
    signal_finished = Signal(bool)

    def __init__(self):
        super().__init__()
        self.in_path = ""
        self.out_path = ""
        self.watermark_rect = None  # 原图坐标 (x,y,w,h)
        self.is_running = False

    def set_task(self, in_path: str, out_path: str, watermark_rect: tuple):
        """设置任务参数"""
        self.in_path = in_path
        self.out_path = out_path
        self.watermark_rect = watermark_rect

    def run(self):
        self.is_running = True
        try:
            self._process_video()
            self.signal_finished.emit(True)
        except Exception as err:
            self.signal_log.emit(f"任务异常：{err}")
            self.signal_finished.emit(False)
        self.is_running = False

    def stop_task(self):
        self.is_running = False

    def _erase_watermark(self, frame: np.ndarray) -> np.ndarray:
        """
        水印擦除逻辑，这里先用简单填充，你后续替换成inpaint算法
        frame: RGB numpy数组
        """
        if self.watermark_rect is None:
            return frame
        x, y, w, h = self.watermark_rect
        # 边界保护
        h_img, w_img = frame.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + w)
        y2 = min(h_img, y + h)
        # 简单均值填充，后续替换成cv2.inpaint
        frame[y1:y2, x1:x2] = np.mean(frame, axis=(0, 1)).astype(np.uint8)
        return frame

    def _process_video(self):
        self.signal_log.emit("打开源视频")
        input_container = av.open(self.in_path)
        input_stream = input_container.streams.video[0]
        fps = float(input_stream.average_rate)

        out_container = av.open(self.out_path, mode="w")
        out_stream = out_container.add_stream("libx264", rate=fps)
        out_stream.width = input_stream.width
        out_stream.height = input_stream.height
        out_stream.pix_fmt = "yuv420p"

        total_frames = input_stream.frames if input_stream.frames else 0
        count = 0

        for frame in input_container.decode(video=0):
            if not self.is_running:
                self.signal_log.emit("任务已取消")
                break
            rgb_arr = frame.to_ndarray(format="rgb24")
            # 擦水印
            rgb_arr = self._erase_watermark(rgb_arr)
            # 转回av帧编码
            av_frame = av.VideoFrame.from_ndarray(rgb_arr, format="rgb24")
            pkt = out_stream.encode(av_frame)
            if pkt:
                out_container.mux(pkt)

            count += 1
            if total_frames > 0:
                progress = int(count / total_frames * 100)
                self.signal_progress.emit(progress)
            self.signal_frame_preview.emit(rgb_arr)
            self.signal_log.emit(f"处理帧 {count}/{total_frames}")

        # 刷剩余缓存
        for pkt in out_stream.encode():
            out_container.mux(pkt)

        # 音频复制
        self.signal_log.emit("开始合并音频")
        for in_audio in input_container.decode(audio=0):
            out_audio_stream = out_container.add_stream(template=in_audio.stream)
            out_container.mux(out_audio_stream.encode(in_audio))

        input_container.close()
        out_container.close()
        self.signal_log.emit("全部完成！")
