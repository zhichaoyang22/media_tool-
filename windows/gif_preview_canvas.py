from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtCore import Qt, QRect
import numpy as np

class GifPreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_rgb: np.ndarray | None = None
        self.orig_width = 0
        self.orig_height = 0
        self.scale = 1.0
        self.draw_offset_x = 0
        self.draw_offset_y = 0
        self.draw_width = 0
        self.draw_height = 0

    def set_frame(self, rgb_frame: np.ndarray | None):
        self.frame_rgb = rgb_frame
        if rgb_frame is not None:
            self.orig_height, self.orig_width = rgb_frame.shape[:2]
        else:
            self.orig_width = 0
            self.orig_height = 0
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
