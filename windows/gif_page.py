# windows/gif_page.py
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
from .ui_gif_page import Ui_GifPage

class GifGenerateThread(QThread):
    progress_update = pyqtSignal(int)
    log_msg = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, video_path, out_path, start_frame, end_frame, fps, scale, loop, speed):
        super().__init__()
        self.video_path = video_path
        self.out_path = out_path
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = fps
        self.scale = scale
        self.loop = loop
        self.speed = speed
        self.is_stop = False

    def run(self):
        try:
            import imageio

            cap = cv2.VideoCapture(self.video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

            total_frames = self.end_frame - self.start_frame

            frames = []
            idx = 0

            self.log_msg.emit(f"开始读取视频，总片段帧数：{total_frames}")

            while cap.isOpened():
                if self.is_stop:
                    self.log_msg.emit("任务已取消")
                    cap.release()
                    self.finished_signal.emit(False)
                    return

                ret, frame = cap.read()
                if not ret or idx >= total_frames:
                    break

                h, w = frame.shape[:2]
                new_w = int(w * self.scale)
                new_h = int(h * self.scale)

                frame = cv2.resize(frame, (new_w, new_h))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frames.append(frame_rgb)

                idx += 1

                progress = int(idx / total_frames * 95)
                self.progress_update.emit(progress)

            cap.release()

            if self.is_stop:
                self.log_msg.emit("任务已取消")
                self.finished_signal.emit(False)
                return

            self.log_msg.emit("正在编码GIF...")
            self.progress_update.emit(95)

            # ========== 关键修复：用跳帧实现真实加速 ==========
            if self.speed > 1.0:
                step = int(round(self.speed))
                self.log_msg.emit(f"检测到加速 {self.speed}x，将每 {step} 帧保留 1 帧")
                frames = frames[::step]

                # 防止 frames 变空
                if not frames:
                    frames = [frame_rgb]

            elif self.speed < 1.0:
                # 慢放暂时不做插帧，只保留原帧
                self.log_msg.emit(f"当前倍速 {self.speed}x，慢放建议配合更低GIF帧率")

            # duration 也同步改，避免有些播放器太慢
            duration = 1.0 / (self.fps * self.speed)

            self.log_msg.emit(f"最终写入帧数：{len(frames)}")
            self.log_msg.emit(f"单帧时长：{duration:.3f}秒")

            imageio.mimsave(
                self.out_path,
                frames,
                duration=duration,
                loop=self.loop
            )

            self.progress_update.emit(100)
            self.log_msg.emit(f"GIF生成成功！保存路径：{self.out_path}")
            self.finished_signal.emit(True)

        except Exception as e:
            self.log_msg.emit(f"生成失败：{str(e)}")
            self.finished_signal.emit(False)

    def stop_task(self):
        self.is_stop = True

class GifPage(QWidget):
    back_home = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_GifPage()
        self.ui.setupUi(self)
        self.video_path = None
        self.total_video_frames = 0
        self.current_preview_frame = 0
        self.gen_thread = None
        # 绑定信号槽
        self.ui.btn_back.clicked.connect(self.back_home.emit)
        self.ui.btn_select_video.clicked.connect(self.select_video)
        self.ui.btn_del_video.clicked.connect(self.unload_video)
        self.ui.btn_prev_frame.clicked.connect(self.prev_frame)
        self.ui.btn_next_frame.clicked.connect(self.next_frame)
        self.ui.btn_select_out.clicked.connect(self.select_output_path)
        self.ui.btn_start.clicked.connect(self.start_generate)
        self.ui.btn_cancel.clicked.connect(self.cancel_task)
        # 设置spin参数范围和默认值
        self.ui.spin_fps.setRange(1, 30)
        self.ui.spin_fps.setValue(10)
        self.ui.spin_scale.setRange(0.1, 2.0)
        self.ui.spin_scale.setSingleStep(0.1)
        self.ui.spin_scale.setValue(1.0)
        self.ui.spin_loop.setRange(0, 100)
        self.ui.spin_loop.setValue(0)
        # 动画倍速初始化
        self.ui.spin_speed.setRange(0.2, 4.0)
        self.ui.spin_speed.setSingleStep(0.1)
        self.ui.spin_speed.setValue(1.0)
    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "视频文件(*.mp4 *.mov *.avi *.mkv)")
        if not path:
            return

        self.video_path = path
        cap = cv2.VideoCapture(path)
        self.total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.ui.spin_start_frame.setMinimum(0)
        self.ui.spin_start_frame.setMaximum(self.total_video_frames - 1)
        self.ui.spin_start_frame.setValue(0)

        self.ui.spin_end_frame.setMinimum(0)
        self.ui.spin_end_frame.setMaximum(self.total_video_frames - 1)
        self.ui.spin_end_frame.setValue(min(50, self.total_video_frames - 1))

        self.current_preview_frame = 0
        self.show_preview_frame(self.current_preview_frame)

        self.ui.btn_prev_frame.setEnabled(True)
        self.ui.btn_next_frame.setEnabled(True)

        self.append_log(f"已加载视频：{path}，总帧数：{self.total_video_frames}")

        cap.release()

    def unload_video(self):
        self.video_path = None
        self.total_video_frames = 0
        self.ui.label_preview.clear()
        self.ui.spin_start_frame.setValue(0)
        self.ui.spin_end_frame.setValue(0)
        self.ui.btn_prev_frame.setEnabled(False)
        self.ui.btn_next_frame.setEnabled(False)
        self.append_log("已卸载视频")
    def show_preview_frame(self, frame_idx):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            self.ui.label_preview.setPixmap(pix.scaled(self.ui.label_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        cap.release()
    def prev_frame(self):
        if self.current_preview_frame > 0:
            self.current_preview_frame -= 1
            self.show_preview_frame(self.current_preview_frame)
    def next_frame(self):
        if self.current_preview_frame < self.total_video_frames - 1:
            self.current_preview_frame += 1
            self.show_preview_frame(self.current_preview_frame)
    def select_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存GIF", "", "GIF动图(*.gif)")
        if path:
            self.ui.edit_out_path.setText(path)
    def append_log(self, msg):
        self.ui.log_text.append(msg)
    def start_generate(self):
        if not self.video_path:
            QMessageBox.warning(self, "提示", "请先选择视频")
            return

        out_path = self.ui.edit_out_path.text()
        if not out_path:
            QMessageBox.warning(self, "提示", "请选择输出保存路径")
            return

        start = self.ui.spin_start_frame.value()
        end = self.ui.spin_end_frame.value()

        if end <= start:
            QMessageBox.warning(self, "提示", "结束帧必须大于起始帧")
            return

        fps = self.ui.spin_fps.value()
        scale = self.ui.spin_scale.value()
        loop = self.ui.spin_loop.value()
        speed = self.ui.spin_speed.value()

        self.ui.btn_start.setEnabled(False)
        self.ui.btn_cancel.setEnabled(True)

        self.gen_thread = GifGenerateThread(
            self.video_path,
            out_path,
            start,
            end,
            fps,
            scale,
            loop,
            speed
        )

        self.gen_thread.progress_update.connect(self.ui.progress_bar.setValue)
        self.gen_thread.log_msg.connect(self.append_log)
        self.gen_thread.finished_signal.connect(self.on_gen_finish)
        self.gen_thread.start()

        self.append_log("=====开始生成GIF=====")
        self.append_log(f"起始帧：{start}")
        self.append_log(f"结束帧：{end}")
        self.append_log(f"GIF帧率：{fps}")
        self.append_log(f"缩放比例：{scale}")
        self.append_log(f"循环次数：{loop}")
        self.append_log(f"动画倍速：{speed}x")
        self.append_log(f"单帧时长：{1.0/(fps*speed):.3f}秒")

    def cancel_task(self):
        if self.gen_thread and self.gen_thread.isRunning():
            self.gen_thread.stop_task()
    def on_gen_finish(self, success):
        self.ui.btn_start.setEnabled(True)
        self.ui.btn_cancel.setEnabled(False)
        if success:
            self.ui.progress_bar.setValue(100)
            self.append_log("===== GIF生成任务全部完成 =====")
        else:
            self.ui.progress_bar.setValue(0)
            self.append_log("===== GIF生成任务异常结束 =====")

