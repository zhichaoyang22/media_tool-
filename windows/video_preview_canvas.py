from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage, QPen, QFont
from PyQt6.QtCore import Qt, QRect, QPoint
import numpy as np

class VideoPreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_rgb: np.ndarray | None = None
        self.on_rect_selected = None

        # 原图尺寸
        self.orig_width = 0
        self.orig_height = 0
        self.scale = 1.0
        self.draw_offset_x = 0
        self.draw_offset_y = 0
        self.draw_width = 0
        self.draw_height = 0

        # 鼠标拖拽临时框
        self.is_dragging = False
        self.drag_start: QPoint = QPoint(0, 0)
        self.drag_end: QPoint = QPoint(0, 0)

        # 多水印标记框列表：存储原图坐标 (x,y,w,h)
        self.mark_rects = []

    def set_frame(self, rgb_frame: np.ndarray | None):
        self.frame_rgb = rgb_frame
        if rgb_frame is not None:
            self.orig_height, self.orig_width = rgb_frame.shape[:2]
        else:
            self.orig_width = 0
            self.orig_height = 0
            self.mark_rects.clear()
        self.update()

    def clear_mark_rects(self):
        """清空当前帧所有标记框"""
        self.mark_rects.clear()
        self.update()

    def add_mark_rect(self, x, y, w, h):
        """添加一个水印标记框（原图像素坐标）"""
        self.mark_rects.append((x, y, w, h))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)
        if self.frame_rgb is None:
            return

        h, w, ch = self.frame_rgb.shape
        qimg = QImage(
            self.frame_rgb.data,
            w,
            h,
            w * ch,
            QImage.Format.Format_RGB888
        )

        # 等比例居中，自动黑边
        w_widget = self.width()
        h_widget = self.height()
        scale_w = w_widget / w
        scale_h = h_widget / h
        self.scale = min(scale_w, scale_h)

        self.draw_width = int(w * self.scale)
        self.draw_height = int(h * self.scale)
        self.draw_offset_x = (w_widget - self.draw_width) // 2
        self.draw_offset_y = (h_widget - self.draw_height) // 2

        painter.drawImage(
            QRect(self.draw_offset_x, self.draw_offset_y, self.draw_width, self.draw_height),
            qimg
        )

        # 绘制已保存的多个标记框（原图坐标转画布坐标）
        pen_mark = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen_mark)
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        for idx, (x, y, w_box, h_box) in enumerate(self.mark_rects):
            cx = int(x * self.scale) + self.draw_offset_x
            cy = int(y * self.scale) + self.draw_offset_y
            cw = int(w_box * self.scale)
            ch = int(h_box * self.scale)
            painter.drawRect(cx, cy, cw, ch)
            painter.drawText(QPoint(cx+4, cy+14), f"#{idx+1}")

        # 绘制正在拖拽的临时虚线框
        if self.is_dragging:
            pen_drag = QPen(Qt.GlobalColor.red, 2)
            pen_drag.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen_drag)
            painter.drawRect(QRect(self.drag_start, self.drag_end))

    def mousePressEvent(self, event):
        if self.frame_rgb is None:
            return
        pos = event.pos()
        img_rect = QRect(self.draw_offset_x, self.draw_offset_y, self.draw_width, self.draw_height)
        if img_rect.contains(pos):
            self.is_dragging = True
            self.drag_start = pos
            self.drag_end = pos

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return
        self.drag_end = event.pos()
        self.update()
    def clear_frame(self):
        self.frame_rgb = None
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.is_dragging:
            return
        self.is_dragging = False
        self.update()

        # 画布坐标
        x1 = min(self.drag_start.x(), self.drag_end.x())
        y1 = min(self.drag_start.y(), self.drag_end.y())
        x2 = max(self.drag_start.x(), self.drag_end.x())
        y2 = max(self.drag_start.y(), self.drag_end.y())

        # 减去图片偏移
        x1_img = x1 - self.draw_offset_x
        y1_img = y1 - self.draw_offset_y
        x2_img = x2 - self.draw_offset_x
        y2_img = y2 - self.draw_offset_y

        # 换算原图像素
        x_real = int(x1_img / self.scale)
        y_real = int(y1_img / self.scale)
        w_real = int((x2_img - x1_img) / self.scale)
        h_real = int((y2_img - y1_img) / self.scale)

        # 边界保护
        x_real = np.clip(x_real, 0, self.orig_width - 1)
        y_real = np.clip(y_real, 0, self.orig_height - 1)
        w_real = np.clip(w_real, 1, self.orig_width - x_real)
        h_real = np.clip(h_real, 1, self.orig_height - y_real)

        if self.on_rect_selected is not None:
            self.on_rect_selected(x_real, y_real, w_real, h_real)
