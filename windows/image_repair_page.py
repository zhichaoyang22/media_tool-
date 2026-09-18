from PyQt6.QtWidgets import QWidget, QFileDialog, QApplication
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
import cv2
import numpy as np
import av
from fractions import Fraction
from .ui_image_repair_page import Ui_ImageRepairPage
import torch
import os
#from mobile_sam import sam_model_registry, SamPredictor
class ImageRepairPage(QWidget):
    back_to_home = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImageRepairPage()
        self.ui.setupUi(self)
        # 图像数据
        self.origin_img: np.ndarray | None = None
        self.display_pixmap: QPixmap | None = None
        self.scale_ratio = 1.0
        self.is_drawing = False
        self.draw_strokes = []       # 所有已经画完的笔画，二维列表
        self.current_stroke = []     # 当前正在绘制的笔画
        self.current_video_path = ""
        self.processed_video_frames = []
        self.video_fps = 24
        self.video_w = 0
        self.video_h = 0
        self.is_video_source = False
        # ========== MobileSAM ==========
        self.sam_predictor = None
        self.sam_loaded = False
        self.sam_model_path = os.path.join("models", "mobile_sam.pt")
        # 绑定控件信号
        self.ui.btn_back.clicked.connect(self.back_to_home.emit)
        self.ui.btn_open.clicked.connect(self.open_file)
        self.ui.btn_run.clicked.connect(self.process_media)
        self.ui.btn_save.clicked.connect(self.save_file)
        self.ui.btn_reset.clicked.connect(self.reset_canvas)
        self.ui.slider_block.valueChanged.connect(self.update_block_tip)
        self.ui.slider_brush.valueChanged.connect(self.update_brush_tip)
        # 挂载画布鼠标事件
        self.ui.label_preview.mousePressEvent = self.on_mouse_press
        self.ui.label_preview.mouseMoveEvent = self.on_mouse_move
        self.ui.label_preview.mouseReleaseEvent = self.on_mouse_release
        # 初始化加载SAM
        self.load_mobile_sam()
    def load_mobile_sam(self):
        """MobileSAM暂时禁用"""
        self.log("ℹ️MobileSAM未启用，AI物体消除功能不可用")
        self.sam_loaded = False
        return
    def update_block_tip(self, val):
        self.ui.label_block.setText(f"马赛克块大小：{val}")
    def update_brush_tip(self, val):
        self.ui.label_brush.setText(f"画笔大小：{val}")
    def log(self, msg):
        self.ui.log_text.append(msg)
        QApplication.processEvents()
    def open_file(self):
        # ==========【修复文件过滤器】==========
        path, filter_selected = QFileDialog.getOpenFileName(
            self,
            "选择媒体文件",
            "",
            "所有媒体 (*.png *.jpg *.jpeg *.bmp *.mp4 *.mov);;图片文件 (*.png *.jpg *.jpeg *.bmp);;视频文件 (*.mp4 *.mov)"
        )
        if not path:
            return
        self.log(f"已打开文件：{path}")
        self.current_video_path = path
        ext = path.lower()
        # 打开新文件清空所有画笔
        self.draw_strokes.clear()
        self.current_stroke.clear()
        self.processed_video_frames.clear()
        if ext.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            self.ui.combo_media.setCurrentText("图片")
            self.is_video_source = False
            self.load_image(path)
        elif ext.endswith((".mp4", ".mov")):
            self.ui.combo_media.setCurrentText("视频")
            self.is_video_source = True
            self.load_video(path)
        else:
            self.log("❌不支持该文件格式")
    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            self.log("❌图片读取失败")
            return
        self.origin_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.refresh_preview()
        self.log("✅图片加载成功")
    def load_video(self, path):
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        if not ret:
            self.log("❌视频读取失败")
            cap.release()
            return
        self.origin_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.origin_img = np.ascontiguousarray(self.origin_img)
        self.video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        self.refresh_preview()
        self.log(f"✅视频加载成功，尺寸 {self.video_w}×{self.video_h} FPS:{self.video_fps:.1f}")
    def refresh_preview(self):
        if self.origin_img is None:
            self.ui.label_preview.clear()
            self.ui.label_preview.setText("图片预览区域")
            return
        h, w = self.origin_img.shape[:2]
        label_size = self.ui.label_preview.size()
        img_contiguous = np.ascontiguousarray(self.origin_img)
        qimg = QImage(img_contiguous.data, w, h, w * 3, QImage.Format.Format_RGB888)
        self.display_pixmap = QPixmap.fromImage(qimg).scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.scale_ratio = self.display_pixmap.width() / w
        self.ui.label_preview.setPixmap(self.display_pixmap)
        self.ui.label_preview.repaint()
    def get_pixmap_offset(self):
        label_w = self.ui.label_preview.width()
        label_h = self.ui.label_preview.height()
        pix_w = self.display_pixmap.width()
        pix_h = self.display_pixmap.height()
        offset_x = (label_w - pix_w) / 2
        offset_y = (label_h - pix_h) / 2
        return offset_x, offset_y
    def on_mouse_press(self, event):
        if self.display_pixmap is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = True
            self.current_stroke = [event.position()]
    def on_mouse_move(self, event):
        if not self.is_drawing or self.display_pixmap is None:
            return
        self.current_stroke.append(event.position())
        self.draw_brush_preview()
    def on_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = False
            if len(self.current_stroke) > 1:
                self.draw_strokes.append(self.current_stroke.copy())
            self.current_stroke.clear()
    def draw_brush_preview(self):
        pix = self.display_pixmap.copy()
        painter = QPainter(pix)
        pen = QPen(QColor(255, 80, 80, 120))
        pen.setWidth(self.ui.slider_brush.value())
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        offset_x, offset_y = self.get_pixmap_offset()
        # 绘制所有已保存笔画
        for stroke in self.draw_strokes:
            pts_pix = []
            for p in stroke:
                px = p.x() - offset_x
                py = p.y() - offset_y
                pts_pix.append(QPoint(int(px), int(py)))
            for i in range(len(pts_pix) - 1):
                painter.drawLine(pts_pix[i], pts_pix[i+1])
        # 当前正在画的笔画
        pts_pix = []
        for p in self.current_stroke:
            px = p.x() - offset_x
            py = p.y() - offset_y
            pts_pix.append(QPoint(int(px), int(py)))
        for i in range(len(pts_pix) - 1):
            painter.drawLine(pts_pix[i], pts_pix[i+1])
        painter.end()
        self.ui.label_preview.setPixmap(pix)
    def apply_mosaic_line(self, img, strokes, block_size, brush_size):
        """添加马赛克"""
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        for stroke in strokes:
            if len(stroke) < 2:
                continue
            for i in range(len(stroke)-1):
                x1, y1 = stroke[i]
                x2, y2 = stroke[i+1]
                cv2.line(mask, (x1,y1), (x2,y2), 255, thickness=brush_size)
        ys, xs = np.where(mask>0)
        if len(ys) == 0:
            return img
        x1 = max(0, xs.min())
        x2 = min(w, xs.max())
        y1 = max(0, ys.min())
        y2 = min(h, ys.max())
        roi = img[y1:y2, x1:x2].copy()
        if roi.size == 0:
            return img
        roi_h, roi_w = roi.shape[:2]
        small = cv2.resize(roi, (block_size, block_size), interpolation=cv2.INTER_NEAREST)
        mosaic_roi = cv2.resize(small, (roi_w, roi_h), interpolation=cv2.INTER_NEAREST)
        result = img.copy()
        result[y1:y2, x1:x2] = mosaic_roi
        return result
    def apply_inpaint_line(self, img, strokes, brush_size):
        """传统局部修复（cv2 inpaint）"""
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        for stroke in strokes:
            if len(stroke) < 2:
                continue
            for i in range(len(stroke)-1):
                x1, y1 = stroke[i]
                x2, y2 = stroke[i+1]
                cv2.line(mask, (x1,y1), (x2,y2), 255, thickness=brush_size)
        ys, xs = np.where(mask > 0)
        if len(ys) == 0:
            return img
        x1 = max(0, xs.min())
        x2 = min(w, xs.max())
        y1 = max(0, ys.min())
        y2 = min(h, ys.max())
        margin = max(4, brush_size // 4)
        x1m = max(0, x1 - margin)
        x2m = min(w, x2 + margin)
        y1m = max(0, y1 - margin)
        y2m = min(h, y2 + margin)
        roi = img[y1m:y2m, x1m:x2m].copy()
        roi_mask = mask[y1m:y2m, x1m:x2m]
        inpaint_radius = 2
        roi_fixed = cv2.inpaint(roi, roi_mask, inpaint_radius, cv2.INPAINT_TELEA)
        result = img.copy()
        result[y1m:y2m, x1m:x2m] = roi_fixed
        return result
    def apply_mobilesam_inpaint(self, img, strokes, brush_size):
        """MobileSAM自动识别物体 + inpaint消除（暂不可用）"""
        self.log("⚠️AI物体消除功能未启用")
        return img
    def process_media(self):
        if self.origin_img is None:
            self.log("请先加载图片/视频！")
            return
        self.ui.progress_bar.setValue(0)
        mode = self.ui.combo_mode.currentText()
        media_type = self.ui.combo_media.currentText()
        block_size = self.ui.slider_block.value()
        brush_size = self.ui.slider_brush.value()
        self.log(f"开始处理，模式:{mode}")
        QApplication.processEvents()
        offset_x, offset_y = self.get_pixmap_offset()
        all_strokes = []
        for stroke in self.draw_strokes:
            pts = []
            for p in stroke:
                real_x = p.x() - offset_x
                real_y = p.y() - offset_y
                if real_x < 0 or real_y <0 or real_x > self.display_pixmap.width() or real_y>self.display_pixmap.height():
                    continue
                x = int(real_x / self.scale_ratio)
                y = int(real_y / self.scale_ratio)
                pts.append([x, y])
            if len(pts)>=2:
                all_strokes.append(pts)
        if len(all_strokes) ==0:
            self.log("⚠️请先在预览图上涂抹区域！")
            return
        if media_type == "图片":
            img = self.origin_img.copy()
            if mode == "添加马赛克":
                img = self.apply_mosaic_line(img, all_strokes, block_size, brush_size)
            elif mode == "传统修复遮挡":
                img = self.apply_inpaint_line(img, all_strokes, brush_size)
            elif mode == "AI物体消除":
                self.log("⚠️MobileSAM未安装，AI物体消除不可用")
                return
            self.origin_img = img
            # 处理完成清空画笔，刷新预览直接显示结果
            self.draw_strokes.clear()
            self.current_stroke.clear()
            self.refresh_preview()
            self.ui.progress_bar.setValue(100)
            self.log("✅图片处理完成，请点击【保存】导出文件")
        else:
            # 视频模式
            if not self.current_video_path:
                self.log("请先加载视频！")
                return
            self.processed_video_frames.clear()
            self.log("视频处理中...")
            self.ui.progress_bar.setValue(10)
            with av.open(self.current_video_path) as in_container:
                in_stream = in_container.streams.video[0]
                total = in_stream.frames
                for idx, frame in enumerate(in_container.decode(in_stream)):
                    rgb = frame.to_rgb().to_ndarray()
                    rgb = np.ascontiguousarray(rgb)
                    if mode == "添加马赛克":
                        rgb = self.apply_mosaic_line(rgb, all_strokes, block_size, brush_size)
                    elif mode == "传统修复遮挡":
                        rgb = self.apply_inpaint_line(rgb, all_strokes, brush_size)
                    elif mode == "AI物体消除":
                        self.log("⚠️MobileSAM未安装，AI物体消除不可用")
                        return
                    self.processed_video_frames.append(rgb)
                    progress = int((idx / total)*90)
                    self.ui.progress_bar.setValue(progress)
                    QApplication.processEvents()
            self.ui.progress_bar.setValue(100)
            self.log("✅视频处理完成，请点击【保存】导出视频")
            # 视频处理完成，预览更新为处理后首帧，清空画笔
            if self.processed_video_frames:
                self.origin_img = self.processed_video_frames[0]
                self.draw_strokes.clear()
                self.current_stroke.clear()
                self.refresh_preview()
    def save_file(self):
        if self.origin_img is None and len(self.processed_video_frames)==0:
            self.log("没有可保存的媒体！")
            return
        media_type = self.ui.combo_media.currentText()
        if media_type == "图片":
            path, _ = QFileDialog.getSaveFileName(self, "保存图片", "",
                "PNG(*.png);;JPG(*.jpg);;BMP(*.bmp)")
            if not path:
                return
            save_img = cv2.cvtColor(self.origin_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(path, save_img)
            self.log(f"✅图片已保存至：{path}")
        else:
            if len(self.processed_video_frames) == 0:
                self.log("❌没有处理好的视频帧")
                return
            path, _ = QFileDialog.getSaveFileName(self, "保存视频", "", "MP4 (*.mp4)")
            if not path:
                return
            try:
                with av.open(path, mode="w") as out_container:
                    out_stream = out_container.add_stream("libx264", rate=Fraction(int(self.video_fps), 1))
                    out_stream.width = self.video_w
                    out_stream.height = self.video_h
                    out_stream.pix_fmt = "yuv420p"
                    for rgb_frame in self.processed_video_frames:
                        rgb_frame = np.ascontiguousarray(rgb_frame)
                        new_frame = av.VideoFrame.from_ndarray(rgb_frame, format="rgb24")
                        packets = out_stream.encode(new_frame)
                        for pkt in packets:
                            out_container.mux(pkt)
                    packets = out_stream.encode()
                    for pkt in packets:
                        out_container.mux(pkt)
                self.log(f"✅视频已保存至：{path}")
            except Exception as e:
                self.log(f"❌视频导出失败: {str(e)}")
    def reset_canvas(self):
        self.origin_img = None
        self.display_pixmap = None
        self.draw_strokes.clear()
        self.current_stroke.clear()
        self.processed_video_frames.clear()
        self.current_video_path = ""
        self.is_video_source = False
        self.ui.label_preview.clear()
        self.ui.label_preview.setText("图片预览区域")
        self.ui.progress_bar.setValue(0)
        self.ui.log_text.clear()
        self.log("✅画布已重置")
