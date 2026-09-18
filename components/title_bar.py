# components/title_bar.py
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint


class TitleBar(QFrame):
    """自定义标题栏，支持窗口拖动"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("""
        QFrame{
            background-color:#1e1e2f;
            border-bottom:1px solid #2a2a3a;
        }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16,0,8,0)
        layout.setSpacing(10)

        title_label = QLabel("media-tool")
        title_label.setStyleSheet("QLabel{color:#ffffff; font-size:14px;}")
        layout.addWidget(title_label)

        layout.addStretch()

        self.btn_min = QPushButton("─")
        self.btn_min.setFixedSize(32,32)
        self.btn_min.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#2a2a3a;
            border:none;
            border-radius:6px;
            font-size:16px;
        }
        QPushButton:hover{
            background-color:#3a3a52;
        }
        """)
        layout.addWidget(self.btn_min)

        self.btn_max = QPushButton("□")
        self.btn_max.setFixedSize(32,32)
        self.btn_max.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#2a2a3a;
            border:none;
            border-radius:6px;
            font-size:14px;
        }
        QPushButton:hover{
            background-color:#3a3a52;
        }
        """)
        layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(32,32)
        self.btn_close.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#e53935;
            border:none;
            border-radius:6px;
            font-size:18px;
        }
        QPushButton:hover{
            background-color:#ff5252;
        }
        """)
        layout.addWidget(self.btn_close)

        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.window().move(self.window().pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
