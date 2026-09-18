from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import os
import gc
from rembg import new_session, remove
from .ui_video_bg_remove_page import Ui_VideoBgRemovePage

# ==========模型加载，读取项目本地models文件夹u2net.onnx==========
try:
    model_path = os.path.join(os.getcwd(), "models", "u2net.onnx")
    sess = new_session(
        model_name="u2net",
        model_path=model_path,
        providers=["CPUExecutionProvider"]
    )
    print(f"✅ 加载项目本地模型: {model_path}")
except Exception as e:
    sess = None
    print(f"❌ 模型加载失败:{e}")
# ==============================================================

class VideoBgRemoveThread(QThread):
    progress_signal = pyqtSignal(int)
    preview_frame_signal = pyqtSignal(np.ndarray)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)

    def __init__(self, video_path, sample_step, mask_threshold=0.2):
        super().__init__()
        self.video_path = video_path
        self.sample_step = sample_step
        self.mask_threshold = mask_threshold  # 掩码阈值，0.2优先保留细线条
        self.frame_list = []
        self._stop_flag = False

    def run(self):
        if sess is None:
            self.log_signal.emit("模型未加载，无法抠图！")
            return
        self.log_signal.emit(f"开始逐帧抠除背景，当前mask阈值:{self.mask_threshold}")
        cap = cv2.VideoCapture(self.video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        idx = 0

        while True:
            ret, frame = cap.read()
            if not ret or self._stop_flag:
                break
            if idx % self.sample_step == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 获取mask，增加.copy()解决只读数组报错
                mask_rgba = remove(rgb, session=sess, alpha_matting=False, return_mask=True)
                mask = mask_rgba[:, :, 0].copy()

                # 阈值二值化，低于阈值判定为背景
                mask[mask < self.mask_threshold * 255] = 0
                mask[mask >= self.mask_threshold * 255] = 255

                # 形态膨胀：扩大主体mask，包住金色细线条
                kernel = np.ones((2, 2), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=1)

                # 合并原图+Alpha通道
                rgba = np.dstack([rgb, mask])

                self.frame_list.append(rgba)
                self.preview_frame_signal.emit(rgba)
                gc.collect()  # 每帧处理完释放内存
            progress = int(idx / max(total - 1, 1) * 100)
            self.progress_signal.emit(progress)
            idx += 1

        cap.release()
        self.log_signal.emit("抠图完成，请预览！")
        self.finished_signal.emit(self.frame_list)

    def stop(self):
        self._stop_flag = True


class VideoBgRemovePage(QWidget):
    back_to_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_VideoBgRemovePage()
        self.ui.setupUi(self)

        self.video_path = ""
        self.processed_frames = []
        self.thread = None

        self.ui.btn_back_home.clicked.connect(self.back_to_home.emit)
        self.ui.btn_open.clicked.connect(self.open_video)
        self.ui.btn_start.clicked.connect(self.start_remove_bg)
        self.ui.btn_save.clicked.connect(self.export_video)
        self.ui.btn_reset.clicked.connect(self.reset_page)

    def log(self, msg):
        self.ui.log_text.append(msg)

    def update_status(self, text):
        self.ui.label_status.setText(f"状态：{text}")

    def open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频",
            "",
            "视频文件(*.mp4 *.mov *.avi *.mkv)"
        )
        if not path:
            return
        self.video_path = path
        self.processed_frames.clear()
        self.log(f"已载入视频：{path}")
        self.update_status("已导入，等待开始抠除背景")
        self.ui.label_output_file.setText("输出文件：未导出")
        self.ui.btn_save.setEnabled(False)

        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.show_preview(rgb)
        cap.release()

    def show_preview(self, img_arr):
        # RGBA棋盘格预览透明通道
        h, w = img_arr.shape[:2]
        if img_arr.shape[-1] ==4:
            background = np.full((h,w,3), 80, dtype=np.uint8)
            alpha = img_arr[:,:,3:4]/255.0
            rgb = (img_arr[:,:,:3] * alpha + background * (1-alpha)).astype(np.uint8)
            qimg = QImage(rgb.data, w, h, w*3, QImage.Format.Format_RGB888)
        else:
            qimg = QImage(img_arr.data, w, h, w*3, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.ui.label_preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label_preview.setPixmap(pix)

    def start_remove_bg(self):
        if not self.video_path:
            self.log("请先导入视频")
            return
        sample = self.ui.spin_sample.value()
        self.ui.progress_bar.setValue(0)
        self.processed_frames.clear()

        # 阈值0.2，保留发光细线，如果还是丢线条可以改成0.15
        self.thread = VideoBgRemoveThread(self.video_path, sample, mask_threshold=0.2)
        self.thread.progress_signal.connect(self.ui.progress_bar.setValue)
        self.thread.preview_frame_signal.connect(self.show_preview)
        self.thread.log_signal.connect(self.log)
        self.thread.finished_signal.connect(self.on_task_finish)

        self.ui.btn_start.setEnabled(False)
        self.ui.btn_save.setEnabled(False)
        self.update_status("正在抠图中...")
        self.thread.start()

    def on_task_finish(self, frame_list):
        self.processed_frames = frame_list
        self.ui.btn_start.setEnabled(True)
        if self.processed_frames:
            self.show_preview(self.processed_frames[-1])
            self.ui.btn_save.setEnabled(True)
            self.update_status("抠图完成，预览确认后导出")
            self.log(f"抠图完成，共缓存 {len(frame_list)} 帧")
        else:
            self.update_status("未处理到有效帧")

    def export_video(self):
        if not self.processed_frames:
            self.log("没有可导出的帧，请先抠图")
            return
        video_dir = os.path.dirname(self.video_path) if self.video_path else "."
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        export_format = self.ui.combo_format.currentText()
        default_name = f"{video_name}_bg_removed.{export_format}"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存视频",
            os.path.join(video_dir, default_name),
            f"{export_format.upper()} (*.{export_format})"
        )
        if not save_path:
            return
        if not save_path.lower().endswith(f".{export_format}"):
            save_path += f".{export_format}"

        self.log(f"正在导出：{save_path}")
        try:
            h, w = self.processed_frames[0].shape[:2]
            if export_format == "mov":
                # MOV支持透明通道，PNG编码保存RGBA
                fourcc = cv2.VideoWriter_fourcc(*"png ")
                out = cv2.VideoWriter(save_path, fourcc, 24, (w, h), isColor=True)
                for rgba in self.processed_frames:
                    bgra = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
                    out.write(bgra)
            else:
                # MP4丢弃Alpha通道
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(save_path, fourcc, 24, (w, h))
                for rgba in self.processed_frames:
                    bgr = cv2.cvtColor(rgba[:,:,:3], cv2.COLOR_RGBA2BGR)
                    out.write(bgr)
            out.release()
            self.ui.label_output_file.setText(f"输出文件：{save_path}")
            self.update_status("导出完成")
            self.log(f"导出成功：{save_path}")
        except Exception as e:
            self.log(f"导出失败：{str(e)}")
            self.update_status("导出失败")

    def reset_page(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.video_path = ""
        self.processed_frames.clear()
        self.ui.label_preview.setText("预览窗口\n请导入视频")
        self.ui.label_output_file.setText("输出文件：未导出")
        self.ui.progress_bar.setValue(0)
        self.ui.log_text.clear()
        self.ui.btn_save.setEnabled(False)
        self.ui.btn_start.setEnabled(True)
        self.update_status("等待导入视频")
