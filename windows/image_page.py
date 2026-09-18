from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from PIL import Image
from .ui_image_page import Ui_ImagePage


class ImageWorkThread(QThread):
    finished_signal = pyqtSignal(np.ndarray)
    log_signal = pyqtSignal(str)

    def __init__(self, img_np, task_type, params):
        super().__init__()
        self.img_np = img_np
        self.task_type = task_type
        self.params = params

    def run(self):
        try:
            if self.task_type == "beauty":
                out_img = self.process_beauty()
                self.finished_signal.emit(out_img)
                self.log_signal.emit("✅ 美化处理完成")
            elif self.task_type == "remove_bg":
                out_img = self.process_remove_bg()
                self.finished_signal.emit(out_img)
                self.log_signal.emit("✅ AI去除背景完成")
        except Exception as e:
            self.log_signal.emit(f"❌ 处理失败：{str(e)}")

    def process_beauty(self):
        img = self.img_np.copy()
        bright = self.params["bright"]
        contrast = self.params["contrast"]
        saturate = self.params["saturate"]
        sharp = self.params["sharp"]

        bright_factor = 1.0 + bright / 200.0
        img = cv2.convertScaleAbs(img, alpha=bright_factor, beta=0)
        contrast_factor = 1.0 + contrast / 120.0
        img = cv2.convertScaleAbs(img, alpha=contrast_factor, beta=0)
        if saturate != 0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            if saturate > 0:
                s = cv2.add(s, int(saturate * 1.2))
            else:
                s = cv2.subtract(s, int(-saturate * 0.8))
            s = np.clip(s, 0, 255).astype(np.uint8)
            hsv = cv2.merge((h, s, v))
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        if sharp > 0:
            alpha = sharp / 100.0
            blurred = cv2.GaussianBlur(img, (3, 3), 0)
            img = cv2.addWeighted(img, 1.0 + alpha, blurred, -alpha, 0)
        return img

    def process_remove_bg(self):
        from rembg import remove, new_session
        # 加载轻量模型u2netp
        session = new_session("u2netp")
        img_pil = Image.fromarray(cv2.cvtColor(self.img_np, cv2.COLOR_BGR2RGB))

        max_long_side = 2000
        w, h = img_pil.size
        scale_ratio = 1.0
        origin_size = (w, h)

        # 长边超过阈值，先缩小图片推理，防止内存爆掉
        if max(w, h) > max_long_side:
            scale_ratio = max_long_side / max(w, h)
            new_w, new_h = int(w * scale_ratio), int(h * scale_ratio)
            work_img = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            work_img = img_pil

        # 传入session而不是model_name
        out_pil_small = remove(work_img, session=session)

        # 如果缩放了，把结果放大回原图尺寸
        if scale_ratio != 1.0:
            out_pil = out_pil_small.resize(origin_size, Image.Resampling.LANCZOS)
        else:
            out_pil = out_pil_small

        out_np = cv2.cvtColor(np.array(out_pil), cv2.COLOR_RGBA2BGRA)
        return out_np




class ImagePage(QWidget, Ui_ImagePage):
    back_to_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)

        self.origin_img_np = None
        self.result_img_np = None
        self.work_thread = None

        self.bind_signals()

    def bind_signals(self):
        self.btn_back.clicked.connect(self.back_to_home.emit)
        self.btn_open.clicked.connect(self.open_image)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_auto_enhance.clicked.connect(self.auto_enhance)
        self.btn_remove_bg.clicked.connect(self.run_remove_bg)

        # 滑块松开才处理，避免拖动疯狂刷新
        self.slider_bright.sliderReleased.connect(self.run_beauty)
        self.slider_contrast.sliderReleased.connect(self.run_beauty)
        self.slider_saturate.sliderReleased.connect(self.run_beauty)
        self.slider_sharp.sliderReleased.connect(self.run_beauty)

    def log(self, msg):
        self.log_text.append(msg)

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片(*.jpg *.png *.webp *.jpeg)")
        if not path:
            return
        try:
            img_pil = Image.open(path)
            self.origin_img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            self.result_img_np = self.origin_img_np.copy()
            self.show_pixmap(self.origin_img_np, self.label_origin)
            self.show_pixmap(self.result_img_np, self.label_result)
            self.log(f"✅ 已加载图片：{path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"图片读取失败：{str(e)}")

    def show_pixmap(self, img_np, label):
        if img_np.shape[-1] == 4:
            rgb = cv2.cvtColor(img_np, cv2.COLOR_BGRA2RGBA)
            qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 4, QImage.Format.Format_RGBA8888)
        else:
            rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 3, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pix)

    def run_beauty(self):
        if self.origin_img_np is None:
            QMessageBox.information(self, "提示", "请先打开图片")
            return
        params = {
            "bright": self.slider_bright.value(),
            "contrast": self.slider_contrast.value(),
            "saturate": self.slider_saturate.value(),
            "sharp": self.slider_sharp.value(),
        }
        self.work_thread = ImageWorkThread(self.origin_img_np, "beauty", params)
        self.work_thread.finished_signal.connect(self.on_process_done)
        self.work_thread.log_signal.connect(self.log)
        self.work_thread.start()
        self.log("🔄 正在应用图片美化...")

    def auto_enhance(self):
        """自适应一键增强，根据图片亮度自动分配参数"""
        if self.origin_img_np is None:
            QMessageBox.information(self, "提示", "请先打开图片")
            return
        gray = cv2.cvtColor(self.origin_img_np, cv2.COLOR_BGR2GRAY)
        avg_bright = np.mean(gray)
        if avg_bright < 70:
            b_val, c_val, s_val, sh_val = 22, 16, 10, 20
            self.log("📷 检测图片偏暗，自动提亮增强")
        elif avg_bright > 180:
            b_val, c_val, s_val, sh_val = -12, 14, 6, 22
            self.log("📷 检测图片偏亮，压高光增强细节")
        else:
            b_val, c_val, s_val, sh_val = 10, 9, 7, 16
            self.log("📷 图片亮度正常，应用基础增强")
        self.slider_bright.setValue(b_val)
        self.slider_contrast.setValue(c_val)
        self.slider_saturate.setValue(s_val)
        self.slider_sharp.setValue(sh_val)
        self.run_beauty()

    def run_remove_bg(self):
        if self.origin_img_np is None:
            QMessageBox.information(self, "提示", "请先打开图片")
            return
        self.work_thread = ImageWorkThread(self.origin_img_np, "remove_bg", {})
        self.work_thread.finished_signal.connect(self.on_process_done)
        self.work_thread.log_signal.connect(self.log)
        self.work_thread.start()
        self.log("🔄 AI抠图处理中，首次运行会自动下载模型，请等待...")

    def on_process_done(self, out_np):
        self.result_img_np = out_np
        self.show_pixmap(self.result_img_np, self.label_result)

    def save_image(self):
        if self.result_img_np is None:
            QMessageBox.information(self, "提示", "暂无处理结果")
            return
        fmt = self.combo_format.currentText().lower()
        quality = self.slider_quality.value()
        filter_str = f"{fmt.upper()}图片 (*.{fmt})"
        save_path, _ = QFileDialog.getSaveFileName(self, "导出图片", "", filter_str)
        if not save_path:
            return
        try:
            if fmt == "jpg":
                if self.result_img_np.shape[-1] == 4:
                    rgb = cv2.cvtColor(self.result_img_np, cv2.COLOR_BGRA2BGR)
                else:
                    rgb = self.result_img_np
                img_pil = Image.fromarray(cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB))
                img_pil.save(save_path, quality=quality, optimize=True)
            elif fmt == "png":
                img_pil = Image.fromarray(cv2.cvtColor(self.result_img_np, cv2.COLOR_BGRA2RGBA))
                img_pil.save(save_path, "PNG", optimize=True)
            elif fmt == "webp":
                img_pil = Image.fromarray(cv2.cvtColor(self.result_img_np, cv2.COLOR_BGRA2RGBA))
                img_pil.save(save_path, "WEBP", quality=quality, lossless=False)
            self.log(f"✅ 文件导出成功：{save_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败：{str(e)}")
