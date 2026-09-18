from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                             QLabel, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt
from components import TitleBar, FuncCard
from .image_watermark_page import ImageWatermarkPage
from .video_watermark_page import VideoWatermarkPage
# =====新增导入=====
from .gif_page import GifPage
from .image_page import ImagePage
from .image_repair_page import ImageRepairPage
from .video_edit_page import VideoEditPage
from .gif_compress_page import GifCompressPage
from .video_bg_remove_page import VideoBgRemovePage
# 在HomeWindow头部导入区新增一行
from .image_enhance_page import ImageEnhancePage

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("media-tool")
        self.setMinimumSize(1040, 680)
        self.resize(1200,760)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.shadow_container = QWidget()
        self.setCentralWidget(self.shadow_container)
        self.shadow_container.setStyleSheet("""
        QWidget{
            background-color:#1a1a27;
            border:1px solid #2a2a3a;
            border-radius:16px;
        }
        """)
        main_layout = QVBoxLayout(self.shadow_container)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        self.title_bar.btn_min.clicked.connect(self.showMinimized)
        self.title_bar.btn_max.clicked.connect(self.toggle_maximize)
        self.title_bar.btn_close.clicked.connect(self.close)
        # 页面堆叠容器
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        # -------- 首页页面 index=0 --------
        home_page_widget = QWidget()
        home_content_layout = QVBoxLayout(home_page_widget)
        home_content_layout.setContentsMargins(20,20,20,20)
        home_content_layout.setSpacing(22)
        banner = QFrame()
        banner.setFixedHeight(140)
        banner.setStyleSheet("""
        QFrame{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3050ff, stop:1 #b828b8);
            border-radius:14px;
        }
        """)
        banner_layout = QVBoxLayout(banner)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.setContentsMargins(20,20,20,20)
        banner_layout.setSpacing(8)
        title = QLabel("媒体智能处理工具箱")
        title.setStyleSheet("QLabel{color:#ffffff; font-size:26px; font-weight:bold;}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ========= 修改横幅副标题 =========
        sub_title = QLabel("图片去水印、视频去水印、视频转GIF、GIF压缩优化、图片美化抠图、马赛克处理一站式处理")
        sub_title.setStyleSheet("QLabel{color:#ffffff; font-size:14px;}")
        sub_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.addWidget(title)
        banner_layout.addWidget(sub_title)
        home_content_layout.addWidget(banner)
        grid = QGridLayout()
        grid.setSpacing(16)
        cards_data = [
            ("图片去水印", "AI智能消除图片LOGO、文字和角落水印"),
            ("视频去水印", "视频画面无痕去除角落、全屏水印"),
            ("视频转GIF", "截取片段生成高清GIF动图"),
            ("图片处理", "图片美化、AI抠图、高清增强、图片格式互转"),
            ("图片修复", "图片/视频添加马赛克、去除马赛克"),
            ("视频剪辑", "分割、变速、调色基础剪辑"),
        ]
        idx = 0
        for card_title, card_desc in cards_data:
            card = FuncCard(card_title, card_desc)
            card.clicked.connect(self.on_card_clicked)
            row = idx // 3
            col = idx % 3
            grid.addWidget(card, row, col)
            idx += 1
        home_content_layout.addLayout(grid)
        label_section = QLabel("常用增强工具")
        label_section.setStyleSheet("QLabel{color:#ddddf0; font-size:14px;}")
        home_content_layout.addWidget(label_section)
        grid2 = QGridLayout()
        grid2.setSpacing(16)
        cards_data2 = [
            ("GIF压缩优化", "减小动图体积，保留画面质量"),
            ("视频抠除背景", "一键去除视频背景，支持透明前景提取"),
            ("图片增强修复", "老照片、截图画质提升"),
        ]

        idx = 0
        for card_title, card_desc in cards_data2:
            card = FuncCard(card_title, card_desc)
            card.clicked.connect(self.on_card_clicked)
            row = idx // 3
            col = idx % 3
            grid2.addWidget(card, row, col)
            idx += 1
        home_content_layout.addLayout(grid2)
        home_content_layout.addStretch()
        self.stacked_widget.addWidget(home_page_widget)
        # -------- 图片去水印页面 index=1 --------
        self.page_img_watermark = ImageWatermarkPage()
        self.page_img_watermark.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.page_img_watermark)
        # -------- 视频去水印页面 index=2 --------
        self.page_video_watermark = VideoWatermarkPage()
        self.page_video_watermark.back_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.page_video_watermark)
        # =====新增：视频转GIF页面 index=3=====
        self.page_gif = GifPage()
        self.page_gif.back_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.page_gif)
        # =====新增：图片处理页面 index=4=====
        self.page_image = ImagePage()
        self.page_image.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.page_image)
        # =====图片修复页面 index=5=====
        self.image_repair_page = ImageRepairPage()
        self.image_repair_page.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.image_repair_page)
        # ====== 视频剪辑页面 index=6 ======
        self.video_edit_page = VideoEditPage()
        self.video_edit_page.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.video_edit_page)
        # =====新增：GIF压缩优化页面 index=7=====
        self.gif_compress_page = GifCompressPage()
        # 【删除了这一行】self.gif_compress_page.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.gif_compress_page)
        # =====新增：视频抠除背景页面 index=8=====
        self.video_bg_remove_page = VideoBgRemovePage()
        self.video_bg_remove_page.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.video_bg_remove_page)
        # =====新增：图片增强修复页面 index=9=====
        self.image_enhance_page = ImageEnhancePage()
        self.image_enhance_page.back_to_home.connect(self.go_home)
        self.stacked_widget.addWidget(self.image_enhance_page)  


    def on_card_clicked(self, card_name: str):
        """卡片点击路由跳转"""
        if card_name == "图片去水印":
            self.stacked_widget.setCurrentIndex(1)
        elif card_name == "视频去水印":
            self.stacked_widget.setCurrentIndex(2)
        elif card_name == "视频转GIF":
            self.stacked_widget.setCurrentIndex(3)
        elif card_name == "图片处理":
            self.stacked_widget.setCurrentIndex(4)
        elif card_name == "图片修复":
            self.stacked_widget.setCurrentIndex(5)
        elif card_name == "视频剪辑":
            self.stacked_widget.setCurrentIndex(6)
        elif card_name == "GIF压缩优化":
            self.stacked_widget.setCurrentIndex(7)
        elif card_name == "视频抠除背景":
            self.stacked_widget.setCurrentIndex(8)
        elif card_name == "图片增强修复":
            self.stacked_widget.setCurrentIndex(9) 

    def go_home(self):
        """切回首页"""
        self.stacked_widget.setCurrentIndex(0)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
