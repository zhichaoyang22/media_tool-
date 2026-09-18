import gc
import os
import cv2
import numpy as np
from PIL import Image, ImageSequence
from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QImage, QPixmap
from .ui_image_enhance_page import Ui_ImageEnhancePage


class BeautifyThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    preview_signal = pyqtSignal(QPixmap)
    finish_signal = pyqtSignal(bool, object)

    def __init__(self, file_path, sample_mode, output_format, enable_enhance):
        super().__init__()
        self.file_path = file_path
        self.sample_mode = sample_mode
        self.output_format = output_format
        self.enable_enhance = enable_enhance
        self.stop_flag = False

    def one_click_beautify(self, pil_img):
        alpha_channel = None
        if pil_img.mode == "RGBA":
            alpha_channel = pil_img.split()[-1]
            rgb_img = pil_img.convert("RGB")
        else:
            rgb_img = pil_img.convert("RGB")
        img_cv = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
        # 轻微降噪
        img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, h=3, hColor=3, templateWindowSize=7, searchWindowSize=21)
        # USM锐化增强线条清晰度
        gaussian = cv2.GaussianBlur(img_cv, (0, 0), 1.2)
        img_cv = cv2.addWeighted(img_cv, 1.4, gaussian, -0.4, 0)
        # CLAHE局部对比度，画面通透不发灰
        lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        img_cv = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        # 轻微提亮
        img_cv = cv2.convertScaleAbs(img_cv, alpha=1.08, beta=5)
        # 转回PIL
        result_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        out_pil = Image.fromarray(result_rgb)
        if alpha_channel is not None:
            out_pil.putalpha(alpha_channel)
        return out_pil

    def run(self):
        try:
            self.log_signal.emit("开始处理素材")
            ext = os.path.splitext(self.file_path)[1].lower()
            result_data = {"type": "", "data": None, "output_format": self.output_format}

            if ext == ".gif":
                im = Image.open(self.file_path)
                frames = []
                total_frames = im.n_frames
                self.log_signal.emit(f"GIF总帧数：{total_frames}")
                step = 1
                if self.sample_mode == "每2帧取一帧":
                    step = 2
                elif self.sample_mode == "每3帧取一帧":
                    step = 3
                frame_idx = 0
                for idx, frame in enumerate(ImageSequence.Iterator(im)):
                    if self.stop_flag:
                        self.log_signal.emit("任务已中断")
                        self.finish_signal.emit(False, None)
                        return
                    if idx % step != 0:
                        continue
                    frame = frame.convert("RGBA")
                    if self.enable_enhance:
                        beautified_frame = self.one_click_beautify(frame)
                    else:
                        beautified_frame = frame
                    frames.append(beautified_frame)
                    frame_idx += 1
                    self.progress_signal.emit(frame_idx, total_frames)
                if len(frames) == 0:
                    self.log_signal.emit("❌没有有效帧")
                    self.finish_signal.emit(False, None)
                    return
                result_data["type"] = "gif"
                result_data["data"] = frames
                self.preview_signal.emit(self.pil_to_qpixmap(frames[-1]))

            elif ext == ".mp4":
                cap = cv2.VideoCapture(self.file_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                self.log_signal.emit(f"MP4视频，总帧数：{total_frames}, FPS:{fps:.1f}")
                frames = []
                step = 1
                if self.sample_mode == "每2帧取一帧":
                    step = 2
                elif self.sample_mode == "每3帧取一帧":
                    step = 3
                frame_idx = 0
                read_idx = 0
                while True:
                    ret, cv_frame = cap.read()
                    if not ret:
                        break
                    if self.stop_flag:
                        cap.release()
                        self.log_signal.emit("任务已中断")
                        self.finish_signal.emit(False, None)
                        return
                    if read_idx % step != 0:
                        read_idx +=1
                        continue
                    rgb = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(rgb).convert("RGBA")
                    if self.enable_enhance:
                        pil_frame = self.one_click_beautify(pil_frame)
                    frames.append(pil_frame)
                    frame_idx +=1
                    self.progress_signal.emit(frame_idx, total_frames)
                    read_idx +=1
                cap.release()
                result_data["type"] = "video"
                result_data["data"] = {"frames": frames, "fps": fps}
                self.preview_signal.emit(self.pil_to_qpixmap(frames[-1]))

            else:
                # 单张图片
                pil_img = Image.open(self.file_path)
                self.log_signal.emit("美化图片中")
                if self.enable_enhance:
                    out_img = self.one_click_beautify(pil_img)
                else:
                    out_img = pil_img
                result_data["type"] = "image"
                result_data["data"] = out_img
                self.preview_signal.emit(self.pil_to_qpixmap(out_img))

            self.log_signal.emit("✅素材处理完成，请点击【导出】保存文件")
            self.finish_signal.emit(True, result_data)
        except Exception as e:
            self.log_signal.emit(f"❌处理异常：{str(e)}")
            import traceback
            self.log_signal.emit(traceback.format_exc())
            self.finish_signal.emit(False, None)
        finally:
            gc.collect()

    def pil_to_qpixmap(self, pil_img):
        pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw","RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def stop_task(self):
        self.stop_flag = True


class ImageEnhancePage(QWidget):
    back_to_home = pyqtSignal()

    def __init__(self, back_home_callback=None):
        try:
            super().__init__()
            self.ui = Ui_ImageEnhancePage()
            self.ui.setupUi(self)
            self.source_file = None
            self.result_data = None
            self.worker_thread = None
            self.back_home_callback = back_home_callback

            self.ui.btn_back_home.clicked.connect(self.go_back_home)
            self.ui.btn_open.clicked.connect(self.open_material)
            self.ui.btn_start.clicked.connect(self.start_process)
            self.ui.btn_export.clicked.connect(self.export_file)
            self.ui.btn_reset.clicked.connect(self.reset_all)

            self.ui.label_progress.setText("进度：0%")
        except Exception as e:
            print(f"页面初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def go_back_home(self):
        self.back_to_home.emit()
        if self.back_home_callback:
            self.back_home_callback()

    def open_material(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开素材", "", "媒体文件 (*.png *.jpg *.jpeg *.gif *.webp *.mp4)"
        )
        if not file_path:
            return
        self.source_file = file_path
        self.result_data = None
        self.ui.text_log.append(f"打开素材: {file_path}")
        # 加载原图预览
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp4":
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
            else:
                return
        else:
            pil_img = Image.open(file_path)
        pix = self.pil_to_qpixmap(pil_img)
        self.ui.label_origin.setPixmap(pix.scaled(self.ui.label_origin.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def pil_to_qpixmap(self, pil_img):
        pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw","RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def start_process(self):
        try:
            if not self.source_file:
                self.ui.text_log.append("请先打开素材！")
                return
            if self.worker_thread and self.worker_thread.isRunning():
                self.ui.text_log.append("任务正在运行中，请等待完成或重置！")
                return

            self.ui.label_progress.setText("进度：0%")
            # 读取当前保留UI控件
            sample_mode = self.ui.cbb_frame_sample.currentText()
            output_format = self.ui.cbb_out_format.currentText()
            enable_enhance = self.ui.check_enhance.isChecked()

            self.worker_thread = BeautifyThread(self.source_file, sample_mode, output_format, enable_enhance)
            self.worker_thread.log_signal.connect(self.on_log)
            self.worker_thread.progress_signal.connect(self.on_progress)
            self.worker_thread.preview_signal.connect(self.on_preview_result)
            self.worker_thread.finish_signal.connect(self.on_finish)
            self.worker_thread.start()
            self.ui.text_log.append(f"已选中：帧采样={sample_mode},输出格式={output_format}")
        except Exception as e:
            self.ui.text_log.append(f"❌启动任务异常：{str(e)}")

    def on_log(self, msg):
        self.ui.text_log.append(msg)

    def on_progress(self, current, total):
        if total > 0:
            percent = int(current * 100 / total)
            self.ui.label_progress.setText(f"进度：{percent}%")

    def on_preview_result(self, pixmap):
        self.ui.label_result.setPixmap(pixmap.scaled(self.ui.label_result.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def on_finish(self, success, result_data):
        if success:
            self.result_data = result_data
            self.ui.label_progress.setText("进度：100%")
            self.ui.text_log.append("✅处理完成，点击【导出】保存文件")
        else:
            self.ui.text_log.append("❌美化任务失败")
        self.worker_thread = None

    def export_file(self):
        if self.result_data is None:
            self.ui.text_log.append("❌请先处理素材，再执行导出！")
            return
        res_type = self.result_data["type"]
        out_fmt = self.result_data["output_format"]
        save_path, _ = QFileDialog.getSaveFileName(self, "保存输出", "", f"{out_fmt} 文件 (*.{out_fmt.lower()})")
        if not save_path:
            self.ui.text_log.append("已取消导出")
            return
        try:
            if res_type == "image":
                out_img = self.result_data["data"]
                out_img.save(save_path)
            elif res_type == "gif":
                frames = self.result_data["data"]
                frames[0].save(save_path, save_all=True, append_images=frames[1:], loop=0, duration=100)
            elif res_type == "video":
                frames = self.result_data["data"]["frames"]
                fps = self.result_data["data"]["fps"]
                h,w = frames[0].size
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(save_path, fourcc, fps, (w,h))
                for pimg in frames:
                    cv_frame = cv2.cvtColor(np.array(pimg.convert("RGB")), cv2.COLOR_RGB2BGR)
                    writer.write(cv_frame)
                writer.release()
            self.ui.text_log.append(f"✅导出成功：{save_path}")
        except Exception as e:
            self.ui.text_log.append(f"❌导出失败: {str(e)}")

    def reset_all(self):
        try:
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.stop_task()
                self.worker_thread.wait()
            self.source_file = None
            self.result_data = None
            self.ui.label_origin.clear()
            self.ui.label_result.clear()
            self.ui.text_log.clear()
            self.ui.label_progress.setText("进度：0%")
            self.ui.text_log.append("✅已重置所有参数")
            gc.collect()
        except Exception as e:
            self.ui.text_log.append(f"❌重置异常：{str(e)}")