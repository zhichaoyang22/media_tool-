# components/func_card.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class FuncCard(QFrame):
    """首页功能卡片组件，带hover悬浮效果 + 点击信号"""
    # 自定义信号：点击时发送卡片标题字符串
    clicked = pyqtSignal(str)

    def __init__(self, title, desc):
        super().__init__()
        self.card_title = title
        self.setFixedHeight(130)
        self.setStyleSheet("""
        QFrame{
            background-color:#242436;
            border-radius:12px;
            border:1px solid #34344c;
        }
        QFrame:hover{
            background-color:#2c2c44;
            border:1px solid #6348d8;
        }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18,18,18,18)
        layout.setSpacing(8)

        icon_box = QLabel()
        icon_box.setFixedSize(42,42)
        icon_box.setStyleSheet("""
        QLabel{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #5068ff, stop:1 #b838c8);
            border-radius:10px;
        }
        """)
        layout.addWidget(icon_box, alignment=Qt.AlignmentFlag.AlignLeft)

        label_title = QLabel(title)
        label_title.setStyleSheet("QLabel{color:#ffffff; font-size:15px; font-weight:bold;}")
        layout.addWidget(label_title, alignment=Qt.AlignmentFlag.AlignLeft)

        label_desc = QLabel(desc)
        label_desc.setStyleSheet("QLabel{color:#b0b0cc; font-size:12px;}")
        layout.addWidget(label_desc, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addStretch()

    def mousePressEvent(self, event):
        """鼠标点击卡片，触发自定义信号"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.card_title)
        super().mousePressEvent(event)
