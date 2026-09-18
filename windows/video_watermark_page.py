from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from .ui_video_watermark import Ui_VideoWatermarkPage
from .video_preview_canvas import VideoPreviewCanvas
import cv2
import numpy as np

# ====================== 视频处理后台线程（去水印核心）======================
class WatermarkRemoverWorker(QObject):
    progress_update = pyqtSignal(int)
    log_msg = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, video_path, out_path, mark_rects):
        super().__init__()
        self.video_path = video_path
        self.out_path = out_path
        self.mark_rects = mark_rects
        self.stop_flag = False

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.log_msg.emit("❌ 后台线程：打开视频失败")
            self.finished_signal.emit(False)
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(self.out_path, fourcc, fps, (w, h))

        # 创建掩码：所有水印区域置255
        mask = np.zeros((h, w), dtype=np.uint8)
        for (x, y, bw, bh) in self.mark_rects:
            cv2.rectangle(mask, (x, y), (x+bw, y+bh), 255, -1)

        frame_idx = 0
        self.log_msg.emit(f"🎬 开始处理，总帧数：{total_frames}")
        while True:
            if self.stop_flag:
                self.log_msg.emit("🛑 任务被手动取消")
                break
            ret, frame = cap.read()
            if not ret:
                break

            # OpenCV图像修复去水印
            inpainted = cv2.inpaint(frame, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
            writer.write(inpainted)

            frame_idx += 1
            pct = int((frame_idx / total_frames) * 100)
            self.progress_update.emit(pct)

        cap.release()
        writer.release()
        if self.stop_flag:
            self.finished_signal.emit(False)
        else:
            self.log_msg.emit(f"✅ 处理完成，输出文件：{self.out_path}")
            self.finished_signal.emit(True)

    def stop(self):
        self.stop_flag = True

# ====================== 页面主类 ======================
class VideoWatermarkPage(QWidget):
    back_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_VideoWatermarkPage()
        self.ui.setup_ui(self)

        self.canvas = VideoPreviewCanvas()
        self.canvas.setParent(self.ui.label_preview)
        self.canvas.setGeometry(self.ui.label_preview.rect())

        def on_label_resize(evt):
            self.canvas.setGeometry(0, 0, evt.size().width(), evt.size().height())
        self.ui.label_preview.resizeEvent = on_label_resize

        # 绑定全部按钮
        self.ui.btn_back.clicked.connect(self.back_home.emit)
        self.ui.btn_select_video.clicked.connect(self.on_select_video)
        self.ui.btn_frame_prev.clicked.connect(self.on_prev_frame)
        self.ui.btn_frame_next.clicked.connect(self.on_next_frame)
        self.ui.btn_del_video.clicked.connect(self.on_delete_video)
        self.ui.btn_out_select.clicked.connect(self.on_select_output)
        self.ui.btn_auto_detect.clicked.connect(self.on_auto_detect)
        self.ui.btn_clear.clicked.connect(self.on_clear_rect)
        self.ui.btn_start.clicked.connect(self.on_start_process)
        self.ui.btn_cancel.clicked.connect(self.on_cancel)

        self.canvas.on_rect_selected = self.on_canvas_rect_selected

        # 视频状态
        self.video_path: str | None = None
        self.cap: cv2.VideoCapture | None = None
        self.current_frame_idx = 0
        self.total_frames = 0
        self.fps = 30
        self.output_path = ""

        # 后台任务
        self.worker_thread: QThread | None = None
        self.worker: WatermarkRemoverWorker | None = None
        self.is_running = False

    def log(self, msg: str):
        self.ui.log_text.append(msg)

    def on_select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv);;所有文件 (*.*)"
        )
        if not file_path:
            self.log("未选择视频")
            return
        if self.cap is not None:
            self.cap.release()

        self.video_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            self.log("❌ 视频打开失败！")
            self.cap = None
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.current_frame_idx = 0
        self.canvas.clear_mark_rects()

        self.log(f"✅ 已加载视频：{file_path}")
        self.log(f"视频信息：总帧 {self.total_frames}，FPS {self.fps:.2f}")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.canvas.set_frame(frame_rgb)
            self.log(f"当前帧：{self.current_frame_idx}")

        self.ui.btn_frame_prev.setEnabled(True)
        self.ui.btn_frame_next.setEnabled(True)
        self.ui.btn_start.setEnabled(True)

    def on_prev_frame(self):
        if self.cap is None or self.current_frame_idx <= 0:
            return
        self.current_frame_idx -= 1
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.canvas.set_frame(frame_rgb)
            self.log(f"当前帧：{self.current_frame_idx}")

    def on_next_frame(self):
        if self.cap is None or self.current_frame_idx >= self.total_frames - 1:
            return
        self.current_frame_idx += 1
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.canvas.set_frame(frame_rgb)
            self.log(f"当前帧：{self.current_frame_idx}")

    def on_delete_video(self):
        if self.is_running:
            self.log("⚠️ 任务运行中，不能删除视频")
            return
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.video_path = None
        self.canvas.set_frame(None)
        self.current_frame_idx = 0
        self.total_frames = 0
        self.output_path = ""
        self.ui.edit_output.setText("")
        self.ui.edit_watermark_rect.setText("")

        self.ui.btn_frame_prev.setEnabled(False)
        self.ui.btn_frame_next.setEnabled(False)
        self.ui.btn_start.setEnabled(False)
        self.ui.progress_bar.setValue(0)
        self.log("🗑️ 视频已卸载")

    def on_select_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "输出视频保存位置",
            "",
            "MP4视频 (*.mp4);;所有文件 (*.*)"
        )
        if file_path:
            self.output_path = file_path
            self.ui.edit_output.setText(file_path)
            self.log(f"📁 输出路径：{file_path}")

    def on_auto_detect(self):
        self.log("ℹ️ 自动水印识别待接入算法，当前请手动框选多个水印")

    def on_clear_rect(self):
        self.canvas.clear_mark_rects()
        self.ui.edit_watermark_rect.setText("")
        self.log("🧹 已清空当前帧所有水印标记框")

    def on_canvas_rect_selected(self, x, y, w, h):
        # 新增标记框，追加到列表，不会覆盖旧框
        self.canvas.add_mark_rect(x, y, w, h)
        rect_str_list = [f"{rx},{ry},{rw},{rh}" for rx, ry, rw, rh in self.canvas.mark_rects]
        self.ui.edit_watermark_rect.setText(" | ".join(rect_str_list))
        self.log(f"📍 添加水印框 #{len(self.canvas.mark_rects)}：x={x},y={y},w={w},h={h}")

    def on_start_process(self):
        if self.is_running:
            self.log("⚠️ 任务正在运行，请勿重复点击")
            return
        if self.cap is None:
            self.log("⚠️ 请先加载视频！")
            return
        if not self.output_path:
            self.log("⚠️ 请先选择输出保存路径！")
            return
        if len(self.canvas.mark_rects) == 0:
            self.log("⚠️ 请至少框选一处水印区域！")
            return

        self.is_running = True
        self.ui.btn_start.setEnabled(False)
        self.ui.btn_cancel.setEnabled(True)
        self.log("🚀 启动去水印后台任务...")

        # 创建线程和worker
        self.worker_thread = QThread()
        self.worker = WatermarkRemoverWorker(self.video_path, self.output_path, self.canvas.mark_rects.copy())
        self.worker.moveToThread(self.worker_thread)

        # 信号绑定
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.ui.progress_bar.setValue)
        self.worker.log_msg.connect(self.log)
        self.worker.finished_signal.connect(self.on_task_finish)

        self.worker_thread.start()

    def on_task_finish(self, success):
        self.is_running = False
        self.ui.btn_start.setEnabled(True)
        self.ui.btn_cancel.setEnabled(False)
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker_thread = None
        self.worker = None
        if success:
            self.log("✅ 全部处理完成！")
        else:
            self.log("⚠️ 任务结束（取消或失败）")

    def on_cancel(self):
        if self.worker is not None:
            self.worker.stop()
        self.log("🛑 发送任务取消指令")
