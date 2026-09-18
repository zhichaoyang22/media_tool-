import gc
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove
from rembg.session_factory import new_session
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, QThread, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from .ui_gif_compress_page import Ui_GifCompressPage

# ======================全局单例模型会话【强制CPU】======================
try:
    sess = new_session("u2net", providers=["CPUExecutionProvider"])
except Exception as e:
    sess = None
    print(f"AI抠图模型加载失败: {e}")
# =====================================================================

class GifCompressThread(QThread):
    progress_signal = pyqtSignal(int)
    single_frame_signal = pyqtSignal(Image.Image)
    finished_signal = pyqtSignal(list)
    log_signal = pyqtSignal(str)

    def __init__(self, frame_list, enable_remove_bg, params):
        super().__init__()
        self.frame_list = frame_list
        self.enable_remove_bg = enable_remove_bg
        self.params = params

    def run(self):
        result_frames = []
        total = len(self.frame_list)
        try:
            for idx, frame_pil in enumerate(self.frame_list):
                if self.enable_remove_bg and sess is not None:
                    # AI抠图
                    out_img = remove(frame_pil, session=sess)
                    # 保留亮线 + Alpha羽化去毛刺
                    out_img = self.keep_lines(frame_pil, out_img)
                else:
                    out_img = frame_pil.convert("RGBA")

                result_frames.append(out_img)
                self.single_frame_signal.emit(out_img)
                self.progress_signal.emit(int((idx + 1) / total * 100))
                gc.collect()
            self.finished_signal.emit(result_frames)
            self.log_signal.emit("✅ GIF抠图处理全部完成")
        except Exception as err:
            self.log_signal.emit(f"❌ 处理异常：{str(err)}")

    def keep_lines(self, original_pil, ai_pil):
        """保留原图高亮线条，Alpha通道高斯羽化消除边缘毛刺"""
        src = np.array(original_pil.convert("RGBA"), dtype=np.float32)
        dst = np.array(ai_pil.convert("RGBA"), dtype=np.float32)
        r, g, b, a = src[..., 0], src[..., 1], src[..., 2], src[..., 3]

        # 亮线识别规则
        yellow_line = (r > 160) & (g > 110) & (b < 130)
        white_line = (r > 220) & (g > 220) & (b > 220)
        brightness = (r + g + b) / 3.0
        bright_line = (brightness > 180) & (r > 140) & (g > 140)
        blue_bg_yellow = (b > 120) & (r > 180) & (g > 140)
        line_mask = yellow_line | white_line | bright_line | blue_bg_yellow

        # 线条区域强制使用原图颜色，不透明
        dst[..., 0] = np.where(line_mask, r, dst[..., 0])
        dst[..., 1] = np.where(line_mask, g, dst[..., 1])
        dst[..., 2] = np.where(line_mask, b, dst[..., 2])
        dst[..., 3] = np.where(line_mask, 255, dst[..., 3])

        img = Image.fromarray(dst.astype(np.uint8), mode="RGBA")
        # Alpha通道单独高斯羽化，去除毛刺
        alpha_channel = img.split()[3]
        alpha_channel = alpha_channel.filter(ImageFilter.GaussianBlur(radius=0.75))
        img.putalpha(alpha_channel)
        return img


class GifCompressPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_GifCompressPage()
        self.ui.setupUi(self)

        self.raw_frames = []
        self.frame_durations = []
        self.processed_frames = []
        self.play_idx = 0
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.play_next_frame)
        self.enable_ai_bg_remove = False

        # ==========修复点：绑定方法名和定义保持一致 go_back_home ==========
        self.ui.btn_open.clicked.connect(self.open_gif)
        self.ui.btn_export.clicked.connect(self.export_gif)
        self.ui.btn_play.clicked.connect(self.toggle_play)
        self.ui.btn_ai_remove_bg.clicked.connect(self.toggle_ai_remove_bg)
        self.ui.btn_back.clicked.connect(self.go_back_home)

        # 滑块联动
        self.ui.slider_threshold.valueChanged.connect(self.on_thresh_slider_change)
        self.ui.slider_frame.valueChanged.connect(self.on_frame_slider_change)
        self.ui.label_thresh.setText(f"抠图阈值: {self.ui.slider_threshold.value()}")
        self.ui.label_fps.setText(f"帧间隔: {self.ui.slider_frame.value()/10:.1f}s")

    def go_back_home(self):
        # 返回首页，切换stackedWidget页面
        self.parent().setCurrentIndex(0)

    def toggle_ai_remove_bg(self):
        self.enable_ai_bg_remove = not self.enable_ai_bg_remove
        if self.enable_ai_bg_remove:
            self.ui.btn_ai_remove_bg.setText("关闭透明抠图")
            self.start_process()
        else:
            self.ui.btn_ai_remove_bg.setText("启用透明抠图")
            self.ui.log_text.append("⚠️ AI抠图已关闭")

    def on_thresh_slider_change(self, val):
        self.ui.label_thresh.setText(f"抠图阈值: {val}")

    def on_frame_slider_change(self, val):
        sec = val / 10
        self.ui.label_fps.setText(f"帧间隔: {sec:.1f}s")
        if self.play_timer.isActive():
            self.play_timer.setInterval(int(sec*1000))

    def pil_to_qimage(self, pil_img):
        """PIL.Image转QImage，支持RGBA透明"""
        pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        return qimg

    def show_pil_to_label(self, pil_img, label):
        qimg = self.pil_to_qimage(pil_img)
        scaled_img = qimg.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(scaled_img))

    def open_gif(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开GIF", "", "GIF Files (*.gif)")
        if not path:
            return
        try:
            im = Image.open(path)
            self.raw_frames.clear()
            self.frame_durations.clear()
            for i in range(im.n_frames):
                im.seek(i)
                frame = im.copy().convert("RGBA")
                self.raw_frames.append(frame)
                self.frame_durations.append(im.info.get("duration", 100))
            self.processed_frames = self.raw_frames.copy()
            self.play_idx = 0
            # 左侧【导入原图】加载第一帧原图
            self.show_pil_to_label(self.raw_frames[0], self.ui.label_origin)
            self.show_pil_to_label(self.raw_frames[0], self.ui.label_result)
            self.ui.log_text.append(f"✅ 成功载入GIF，总帧数：{len(self.raw_frames)}")
        except Exception as e:
            self.ui.log_text.append(f"❌ 打开失败：{str(e)}")

    def toggle_play(self):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.ui.btn_play.setText("播放 / 暂停")
        else:
            interval = int(self.ui.slider_frame.value() /10 * 1000)
            self.play_timer.start(interval)
            self.ui.btn_play.setText("暂停")

    def play_next_frame(self):
        if not self.processed_frames:
            return
        # 右侧预览抠图结果
        self.show_pil_to_label(self.processed_frames[self.play_idx], self.ui.label_result)
        self.play_idx += 1
        if self.play_idx >= len(self.processed_frames):
            self.play_idx = 0

    def start_process(self):
        if not self.raw_frames:
            self.ui.log_text.append("⚠️ 请先打开GIF文件")
            return
        params = {
            "colors": self.ui.spin_color_count.value(),
            "width": self.ui.spin_w.value(),
            "height": self.ui.spin_h.value(),
            "threshold": self.ui.slider_threshold.value()
        }
        self.thread = GifCompressThread(self.raw_frames, self.enable_ai_bg_remove, params)
        self.thread.single_frame_signal.connect(self.on_single_frame)
        self.thread.progress_signal.connect(self.on_progress)
        self.thread.finished_signal.connect(self.on_process_finish)
        self.thread.log_signal.connect(self.on_log)
        self.thread.start()

    def on_single_frame(self, pil_img):
        self.show_pil_to_label(pil_img, self.ui.label_result)

    def on_progress(self, val):
        self.ui.log_text.append(f"处理进度：{val}%")

    def on_process_finish(self, frames):
        self.processed_frames = frames
        self.ui.log_text.append("✅ 全部帧处理完成，可以导出GIF")

    def on_log(self, msg):
        self.ui.log_text.append(msg)

    def export_gif(self):
        if not self.processed_frames:
            self.ui.log_text.append("⚠️ 请先完成GIF抠图处理")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "保存GIF", "", "GIF Files (*.gif)")
        if not save_path:
            return
        try:
            # 读取宽高参数，为0则使用原图尺寸
            w = self.ui.spin_w.value()
            h = self.ui.spin_h.value()
            out_frames = []
            for f in self.processed_frames:
                if w>0 and h>0:
                    f = f.resize((w,h), Image.Resampling.LANCZOS)
                out_frames.append(f)
            out_frames[0].save(
                save_path,
                save_all=True,
                append_images=out_frames[1:],
                duration=self.frame_durations,
                disposal=2,
                optimize=True,
                loop=0  # loop=0：无限循环播放，解决GIF停在第一帧
            )
            self.ui.log_text.append(f"✅ 导出成功：{save_path}（无限循环GIF）")
        except Exception as e:
            self.ui.log_text.append(f"❌ 导出失败：{str(e)}")
