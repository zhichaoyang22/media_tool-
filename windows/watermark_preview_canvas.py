# windows/watermark_preview_canvas.py
from PyQt6.QtWidgets import QLabel, QMessageBox
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage


class DarkMessageBox(QMessageBox):
    """深色自定义弹窗，匹配项目暗色主题"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QMessageBox {
            background-color: #1e1e2e;
            color: #ffffff;
            border-radius: 12px;
        }
        QLabel {
            color: #e8e8f2;
            font-size:14px;
            background-color:transparent;
        }
        QPushButton{
            background-color:#5648aa;
            color:#ffffff;
            border:none;
            border-radius:8px;
            padding:8px 20px;
            font-size:14px;
            min-width:80px;
        }
        QPushButton:hover{background-color:#6b5bc2;}
        QPushButton:pressed{background-color:#423880;}
        """)
        self.setWindowTitle("提示")

    @staticmethod
    def showWarning(parent, title, text):
        msg = DarkMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec()

    @staticmethod
    def showInfo(parent, title, text):
        msg = DarkMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec()


class PreviewCanvas(QLabel):
    signal_image_changed = pyqtSignal(bool)
    signal_selection_changed = pyqtSignal(bool)

    def __init__(self, parent_page=None):
        super().__init__()
        self.parent_page = parent_page
        self.original_pixmap: QPixmap | None = None
        self.scale_pixmap: QPixmap | None = None

        self.img_relative_rect = QRect()
        self.screen_draw_rect = QRect()

        self.drawing = False
        self.start_img_pt = QPoint()
        self.end_img_pt = QPoint()

        self.img_offset_x = 0
        self.img_offset_y = 0

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
        QLabel{
            border:1px solid #383854;
            border-radius:12px;
            color:#9494b8;
            background-color:#161622;
            font-size:14px;
        }
        """)

    def set_selection_rects(self, relative_rect: QRect, screen_rect: QRect):
        """对外公开接口：设置选框，页面层只能调用该方法，禁止直接读写内部rect变量"""
        self.img_relative_rect = relative_rect
        self.screen_draw_rect = screen_rect
        valid = self.img_relative_rect.isValid() and self.img_relative_rect.width() >= 10 and self.img_relative_rect.height() >= 10
        self.signal_selection_changed.emit(valid)
        self.update()
        
    def clear_selection(self):
        self.img_relative_rect = QRect()
        self.screen_draw_rect = QRect()
        self.signal_selection_changed.emit(False)
        self.update()

    def set_image(self, pix: QPixmap):
        self.clear_selection()
        self.original_pixmap = None
        self.scale_pixmap = None
        self.img_offset_x = 0
        self.img_offset_y = 0
        has_img = False
        if pix and not pix.isNull():
            self.original_pixmap = pix
            has_img = True
        self.signal_image_changed.emit(has_img)
        self.update()

    def clear_all(self):
        self.img_relative_rect = QRect()
        self.screen_draw_rect = QRect()
        self.original_pixmap = None
        self.scale_pixmap = None
        self.img_offset_x = 0
        self.img_offset_y = 0
        self.signal_image_changed.emit(False)
        self.signal_selection_changed.emit(False)
        self.update()

    def mousePressEvent(self, event):
        if self.original_pixmap is None or self.original_pixmap.isNull():
            return
        screen_pt = event.pos()
        img_pt = QPoint(screen_pt.x() - self.img_offset_x, screen_pt.y() - self.img_offset_y)
        self.drawing = True
        self.start_img_pt = img_pt
        self.end_img_pt = img_pt
        self.update()

    def mouseMoveEvent(self, event):
        if not self.drawing or self.original_pixmap is None or self.original_pixmap.isNull():
            return
        screen_pt = event.pos()
        self.end_img_pt = QPoint(screen_pt.x() - self.img_offset_x, screen_pt.y() - self.img_offset_y)

        self.img_relative_rect = QRect(self.start_img_pt, self.end_img_pt).normalized()
        self.screen_draw_rect = QRect(
            self.img_relative_rect.x() + self.img_offset_x,
            self.img_relative_rect.y() + self.img_offset_y,
            self.img_relative_rect.width(),
            self.img_relative_rect.height()
        )
        valid = self.img_relative_rect.isValid() and self.img_relative_rect.width() >= 10 and self.img_relative_rect.height() >= 10
        self.signal_selection_changed.emit(valid)
        self.update()

    def mouseReleaseEvent(self, event):
        self.drawing = False
        valid = self.img_relative_rect.isValid() and self.img_relative_rect.width() >= 10 and self.img_relative_rect.height() >= 10
        self.signal_selection_changed.emit(valid)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.original_pixmap is not None and not self.original_pixmap.isNull():
            self.scale_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.img_offset_x = (self.width() - self.scale_pixmap.width()) // 2
            self.img_offset_y = (self.height() - self.scale_pixmap.height()) // 2
            painter.drawPixmap(self.img_offset_x, self.img_offset_y, self.scale_pixmap)
        else:
            self.scale_pixmap = None
            self.img_offset_x = 0
            self.img_offset_y = 0

        if self.screen_draw_rect.isValid():
            pen = QPen(QColor("#5648aa"), 2)
            painter.setPen(pen)
            painter.setBrush(QColor(86, 72, 170, 80))
            painter.drawRect(self.screen_draw_rect)

    def get_selection(self):
        if not self.scale_pixmap or not self.img_relative_rect.isValid():
            return None
        sx = self.img_relative_rect.x()
        sy = self.img_relative_rect.y()
        sw = self.img_relative_rect.width()
        sh = self.img_relative_rect.height()
        if sw < 10 or sh < 10:
            return None
        return {"x": sx, "y": sy, "width": sw, "height": sh}
