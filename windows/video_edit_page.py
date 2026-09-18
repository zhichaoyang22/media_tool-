from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import av
from .ui_video_edit_page import Ui_VideoEditPage

from fractions import Fraction



class ExportThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, input_path, save_path, start_frame, end_frame, brightness, contrast, saturation, speed):
        super().__init__()
        self.input_path = input_path
        self.save_path = save_path
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.speed = speed

    def run(self):
        try:
            container = av.open(self.input_path)
            stream = container.streams.video[0]

            # 固定输出24fps，彻底抛弃av.rational，不再处理帧率对象BUG
            out_fps = 24
            total_frames = max(1, self.end_frame - self.start_frame)
            out_container = av.open(self.save_path, mode='w')
            out_stream = out_container.add_stream('libx264', rate=out_fps)
            out_stream.width = stream.width
            out_stream.height = stream.height
            out_stream.pix_fmt = "yuv420p"

            frame_idx = 0
            write_frame_count = 0
            # 帧采样：speed=3，每3帧拿1帧写入，实现倍速
            sample_step = self.speed

            for packet in container.demux(stream):
                for frame in packet.decode():
                    if frame_idx < self.start_frame:
                        frame_idx += 1
                        continue
                    if frame_idx > self.end_frame:
                        break

                    # 帧采样，实现倍速
                    if (frame_idx - self.start_frame) % sample_step == 0:
                        img = frame.to_ndarray(format="rgb24")
                        img = self.apply_color(img, self.brightness, self.contrast, self.saturation)

                        new_frame = av.VideoFrame.from_ndarray(img, format="rgb24")
                        for pkt in out_stream.encode(new_frame):
                            out_container.mux(pkt)
                        write_frame_count +=1

                    progress = int(((frame_idx - self.start_frame) / total_frames) * 100)
                    self.progress_signal.emit(progress)
                    frame_idx += 1

            # 刷剩余编码缓存
            for pkt in out_stream.encode():
                out_container.mux(pkt)

            out_container.close()
            container.close()
            self.finished_signal.emit(True, "导出成功")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

    @staticmethod
    def apply_color(img, brightness, contrast, saturation):
        """
        统一调色逻辑：预览和导出共用
        brightness: -100 ~ 100
        contrast:   -100 ~ 100
        saturation: -100 ~ 100
        """
        img = img.astype(np.float32)

        # 对比度
        contrast_k = 1.0 + contrast / 100.0
        img = img * contrast_k

        # 亮度
        img = img + brightness * 1.2

        img = np.clip(img, 0, 255).astype(np.uint8)

        # 饱和度
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
        sat_k = 1.0 + saturation / 100.0
        hsv[..., 1] = np.clip(hsv[..., 1] * sat_k, 0, 255)
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        return img




class VideoEditPage(QWidget):
    back_to_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_VideoEditPage()
        self.ui.setupUi(self)

        self.video_path = None
        self.av_container = None
        self.video_stream = None
        self.total_frame_count = 0
        self.fps = 0
        self.current_frame_idx = 0
        self.start_frame = 0
        self.end_frame = 0
        self.export_thread = None

        self.frame_iter = None
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.play_next)
        self.is_playing = False

        # 把UI范围改成更直观的 -100 ~ 100
        self.ui.double_bright.setRange(-100.0, 100.0)
        self.ui.double_bright.setSingleStep(1.0)
        self.ui.double_bright.setValue(0.0)

        self.ui.double_contrast.setRange(-100.0, 100.0)
        self.ui.double_contrast.setSingleStep(1.0)
        self.ui.double_contrast.setValue(0.0)

        self.ui.double_saturation.setRange(-100.0, 100.0)
        self.ui.double_saturation.setSingleStep(1.0)
        self.ui.double_saturation.setValue(0.0)

        self.ui.btn_open.clicked.connect(self.open_video)
        self.ui.btn_play.clicked.connect(self.play_pause)
        self.ui.btn_set_start.clicked.connect(self.set_start_point)
        self.ui.btn_set_end.clicked.connect(self.set_end_point)
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_export.clicked.connect(self.export_video)
        self.ui.btn_back_home.clicked.connect(self.back_to_home.emit)
        self.ui.slider_progress.sliderMoved.connect(self.seek_frame)

        # 参数变化时，立即刷新当前帧预览
        self.ui.double_bright.valueChanged.connect(self.refresh_current_frame)
        self.ui.double_contrast.valueChanged.connect(self.refresh_current_frame)
        self.ui.double_saturation.valueChanged.connect(self.refresh_current_frame)

    def append_log(self, msg):
        self.ui.log_text.append(msg)

    def open_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "", "视频文件 (*.mp4 *.mov *.avi *.mkv)"
        )
        if not file_path:
            return

        self.video_path = file_path
        try:
            self.av_container = av.open(file_path)
            self.video_stream = self.av_container.streams.video[0]
            self.total_frame_count = self.video_stream.frames
            self.fps = float(self.video_stream.average_rate)

            self.ui.slider_progress.setRange(0, max(self.total_frame_count - 1, 0))
            self.start_frame = 0
            self.end_frame = self.total_frame_count - 1

            self.append_log(f"✅ 打开视频成功，总帧数：{self.total_frame_count}, FPS:{self.fps:.2f}")
            self.reset_frame_iter()
            self.seek_frame(0)
        except Exception as e:
            QMessageBox.critical(self, "打开失败", str(e))
            self.append_log(f"❌ 打开视频失败: {e}")

    def reset_frame_iter(self):
        if self.av_container is not None:
            self.frame_iter = self.av_container.decode(video=0)

    def seek_frame(self, frame_num):
        if self.av_container is None:
            return

        frame_num = max(0, min(frame_num, self.total_frame_count - 1))
        self.av_container.seek(frame_num, stream=self.video_stream)
        self.reset_frame_iter()

        try:
            for frame in self.frame_iter:
                self.current_frame_idx = frame_num
                self.ui.slider_progress.setValue(frame_num)
                self.show_frame(frame.to_ndarray(format="rgb24"))
                break
        except (av.error.EOFError, StopIteration):
            pass

    def show_frame(self, rgb_img):
        # 这里实时应用调色
        rgb_img = self.apply_current_color(rgb_img)

        h, w, c = rgb_img.shape
        qimg = QImage(rgb_img.data, w, h, w * c, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        label_size = self.ui.label_preview.size()
        scaled_pix = pix.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label_preview.setPixmap(scaled_pix)

    def apply_current_color(self, img):
        brightness = self.ui.double_bright.value()
        contrast = self.ui.double_contrast.value()
        saturation = self.ui.double_saturation.value()
        return ExportThread.apply_color(img, brightness, contrast, saturation)

    def refresh_current_frame(self):
        """拖动调色参数时，立即重绘当前画面，不需要重新seek"""
        pix = self.ui.label_preview.pixmap()
        if pix is None or pix.isNull():
            return

        label_size = self.ui.label_preview.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            return

        # 重新取当前帧并应用调色
        self.av_container.seek(self.current_frame_idx, stream=self.video_stream)
        self.reset_frame_iter()
        try:
            for frame in self.frame_iter:
                self.show_frame(frame.to_ndarray(format="rgb24"))
                break
        except (av.error.EOFError, StopIteration):
            pass

    def play_pause(self):
        if self.av_container is None:
            QMessageBox.warning(self, "提示", "请先打开视频")
            return

        if self.is_playing:
            self.is_playing = False
            self.play_timer.stop()
            self.ui.btn_play.setText("播放 / 暂停")
        else:
            if self.current_frame_idx >= self.total_frame_count - 1:
                self.seek_frame(0)

            self.is_playing = True
            self.ui.btn_play.setText("暂停")

            speed = self.ui.double_speed.value()
            interval = max(1, int(1000 / (self.fps * speed)))
            self.play_timer.setInterval(interval)
            self.play_timer.start()

    def play_next(self):
        speed = self.ui.double_speed.value()
        skip_frames = max(1, int(speed))

        try:
            frame = None
            for _ in range(skip_frames):
                frame = next(self.frame_iter)
                self.current_frame_idx += 1

            if frame is not None:
                self.ui.slider_progress.setValue(self.current_frame_idx)
                self.show_frame(frame.to_ndarray(format="rgb24"))

        except StopIteration:
            self.is_playing = False
            self.play_timer.stop()
            self.ui.btn_play.setText("播放 / 暂停")
            self.append_log("📺 播放到视频末尾")
        except av.error.EOFError:
            self.is_playing = False
            self.play_timer.stop()
            self.ui.btn_play.setText("播放 / 暂停")
            self.append_log("📺 播放到视频末尾")

    def set_start_point(self):
        self.start_frame = self.current_frame_idx
        self.append_log(f"📌 设置起始帧：{self.start_frame}")

    def set_end_point(self):
        self.end_frame = self.current_frame_idx
        self.append_log(f"📌 设置结束帧：{self.end_frame}")

    def clear_all(self):
        if self.play_timer.isActive():
            self.play_timer.stop()

        self.is_playing = False
        self.av_container = None
        self.frame_iter = None
        self.video_path = None

        self.ui.label_preview.clear()
        self.ui.slider_progress.setValue(0)
        self.ui.log_text.clear()
        self.append_log("🗑️ 已清空")

    def export_video(self):
        if self.video_path is None:
            QMessageBox.warning(self, "提示", "请先打开视频")
            return

        if self.start_frame >= self.end_frame:
            QMessageBox.warning(self, "提示", "结束帧必须大于起始帧")
            return

        if self.export_thread is not None and self.export_thread.isRunning():
            QMessageBox.warning(self, "提示", "正在导出，请等待")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存剪辑视频", "clip.mp4", "MP4 (*.mp4)"
        )
        if not save_path:
            return

        bright = self.ui.double_bright.value()
        cont = self.ui.double_contrast.value()
        sat = self.ui.double_saturation.value()
        speed = self.ui.double_speed.value()

        self.ui.btn_export.setEnabled(False)
        self.ui.progress_bar.setVisible(True)
        self.ui.progress_bar.setValue(0)
        self.append_log("⏳ 开始导出视频片段...")

        self.export_thread = ExportThread(
            input_path=self.video_path,
            save_path=save_path,
            start_frame=self.start_frame,
            end_frame=self.end_frame,
            brightness=bright,
            contrast=cont,
            saturation=sat,
            speed=speed
        )
        self.export_thread.progress_signal.connect(self.ui.progress_bar.setValue)
        self.export_thread.finished_signal.connect(self.on_export_done)
        self.export_thread.start()

    def on_export_done(self, ok, msg):
        self.ui.btn_export.setEnabled(True)

        if ok:
            self.append_log(f"✅ {msg}")
    
        else:
            self.append_log(f"❌ {msg}")
            

        self.export_thread = None

    def closeEvent(self, event):
        if self.play_timer.isActive():
            self.play_timer.stop()

        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.wait()

        event.accept()
