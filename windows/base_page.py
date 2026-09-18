# windows/base_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class BasePage(QWidget):
    """所有功能子页面的基类，统一返回按钮、统一样式"""
    # 返回首页信号
    back_to_home = pyqtSignal()

    def __init__(self, page_title="功能页面", parent=None):
        super().__init__(parent)
        self.page_title = page_title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 顶部导航栏：返回按钮 + 页面标题
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(16)

        self.btn_back = QPushButton("返回首页")
        self.btn_back.setFixedHeight(38)
        self.btn_back.setMinimumWidth(110)
        self.btn_back.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#423880;
            border:none;
            border-radius:10px;
            padding-left:14px;
            padding-right:14px;
            font-size:13px;
            font-weight:500;
        }
        QPushButton:hover{
            background-color:#5648aa;
        }
        QPushButton:pressed{
            background-color:#352e66;
        }
        """)
        self.btn_back.clicked.connect(self.back_to_home.emit)
        nav_bar.addWidget(self.btn_back)

        label_title = QLabel(page_title)
        label_title.setStyleSheet("QLabel{color:#ffffff; font-size:18px; font-weight:bold;}")
        nav_bar.addWidget(label_title)
        nav_bar.addStretch()

        layout.addLayout(nav_bar)

        # 内容容器，子类往这里加自己的控件
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(16)
        layout.addLayout(self.content_layout)

        layout.addStretch()
