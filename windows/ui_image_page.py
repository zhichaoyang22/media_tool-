from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QSlider, QGroupBox,
                             QFileDialog, QComboBox, QTextEdit)
from PyQt6.QtCore import Qt


class Ui_ImagePage(object):
    def setupUi(self, ImagePage):
        ImagePage.setObjectName("ImagePage")
        # 页面主布局
        main_layout = QVBoxLayout(ImagePage)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ====================== 全局样式 ======================
        ImagePage.setStyleSheet("""
        QWidget {
            background-color: #1a1a27;
            color: #ffffff;
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            font-size: 14px;
        }
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3050ff, stop:1 #b828b8);
            border: none;
            border-radius: 8px;
            color: #ffffff;
            font-size: 15px;
            font-weight: 700;
            padding: 9px 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4560ff, stop:1 #c838c8);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2540df, stop:1 #a818a8);
        }
        QGroupBox {
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            margin-top: 8px;
            padding: 8px 6px;
            font-weight: bold;
            color: #e8e8ff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 6px;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #2a2a3a;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            width: 18px;
            height: 18px;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3050ff, stop:1 #b828b8);
            border-radius: 9px;
            margin: -6px 0;
        }
        QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4560ff, stop:1 #c838c8);
        }
        /* ========== QComboBox 美化 ========== */
        QComboBox {
            background-color: #222233;
            border: 1px solid #3a3a4a;
            border-radius: 8px;
            padding: 7px 26px 7px 10px;
            color: #ffffff;
            font-size: 14px;
        }
        QComboBox:hover {
            border: 1px solid #505068;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border: none;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top:7px solid #b828b8;
        }
        QComboBox::down-arrow:hover {
            border-top-color: #c838c8;
        }
        QComboBox QAbstractItemView {
            background-color: #222233;
            border: 1px solid #3a3a4a;
            border-radius: 10px;
            padding: 6px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            min-height: 30px;
            border-radius: 6px;
            padding-left:8px;
            color:#fff;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #323248;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #b828b8;
        }
        /* ==================================== */
        QTextEdit {
            background-color: #111122;
            border: 1px solid #2a2a3a;
            border-radius: 8px;
            padding: 8px;
            color: #dddddd;
        }
        QLabel {
            color: #e8e8ff;
        }
        """)

        # ========= 顶部区域：返回首页在最左侧 =========
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        self.btn_back = QPushButton("返回首页")
        self.btn_back.setFixedWidth(110)
        self.btn_back.setFixedHeight(38)
        top_layout.addWidget(self.btn_back)

        self.label_title = QLabel("图片处理")
        self.label_title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
        """)
        top_layout.addWidget(self.label_title)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # ========= 中间主体区域 =========
        center_layout = QHBoxLayout()
        center_layout.setSpacing(18)
        center_layout.setStretch(0, 72)
        center_layout.setStretch(1, 28)

        # -------- 左侧预览面板 --------
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0,0,0,0)
        preview_layout.setSpacing(14)

        # 原图预览卡片
        self.label_origin = QLabel("原图")
        self.label_origin.setMinimumSize(420, 300)
        self.label_origin.setStyleSheet("""
            background: #222233;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            color: #888899;
        """)
        self.label_origin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.label_origin, stretch=1)

        # 结果预览卡片
        self.label_result = QLabel("处理结果")
        self.label_result.setMinimumSize(420, 300)
        self.label_result.setStyleSheet("""
            background: #222233;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            color: #888899;
        """)
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.label_result, stretch=1)

        # -------- 右侧控制面板 --------
        control_widget = QWidget()
        control_widget.setMinimumWidth(240)
        control_widget.setMaximumWidth(280)
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(0,0,0,0)
        control_layout.setSpacing(10)

        # 打开/保存按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.btn_open = QPushButton("打开图片")
        self.btn_open.setFixedHeight(40)
        self.btn_open.setFixedWidth(110)

        self.btn_save = QPushButton("保存图片")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setFixedWidth(110)
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_save)
        control_layout.addLayout(btn_layout)

        # 图片美化分组
        group_beauty = QGroupBox("图片美化")
        beauty_layout = QGridLayout(group_beauty)
        beauty_layout.setSpacing(6)
        beauty_layout.setContentsMargins(6,6,6,6)
        self.slider_bright = QSlider(Qt.Orientation.Horizontal)
        self.slider_bright.setRange(-100, 100)
        self.slider_bright.setValue(0)
        beauty_layout.addWidget(QLabel("亮度"), 0, 0)
        beauty_layout.addWidget(self.slider_bright, 0, 1)

        self.slider_contrast = QSlider(Qt.Orientation.Horizontal)
        self.slider_contrast.setRange(-100, 100)
        self.slider_contrast.setValue(0)
        beauty_layout.addWidget(QLabel("对比度"), 1, 0)
        beauty_layout.addWidget(self.slider_contrast, 1, 1)

        self.slider_saturate = QSlider(Qt.Orientation.Horizontal)
        self.slider_saturate.setRange(-100, 100)
        self.slider_saturate.setValue(0)
        beauty_layout.addWidget(QLabel("饱和度"), 2, 0)
        beauty_layout.addWidget(self.slider_saturate, 2, 1)

        self.slider_sharp = QSlider(Qt.Orientation.Horizontal)
        self.slider_sharp.setRange(0, 100)
        self.slider_sharp.setValue(0)
        beauty_layout.addWidget(QLabel("锐化"), 3, 0)
        beauty_layout.addWidget(self.slider_sharp, 3, 1)

        self.btn_auto_enhance = QPushButton("一键自动增强")
        self.btn_auto_enhance.setFixedHeight(38)
        beauty_layout.addWidget(self.btn_auto_enhance, 4, 0, 1, 2)
        control_layout.addWidget(group_beauty)

        # AI抠图分组
        group_remove_bg = QGroupBox("AI抠图")
        bg_layout = QVBoxLayout(group_remove_bg)
        bg_layout.setSpacing(6)
        bg_layout.setContentsMargins(6,6,6,6)
        self.combo_bg_mode = QComboBox()
        self.combo_bg_mode.addItems(["快速", "标准", "高质量"])
        self.btn_remove_bg = QPushButton("去除背景")
        self.btn_remove_bg.setFixedHeight(38)
        bg_layout.addWidget(self.combo_bg_mode)
        bg_layout.addWidget(self.btn_remove_bg)
        control_layout.addWidget(group_remove_bg)

        # 格式转换分组
        group_format = QGroupBox("格式转换")
        fmt_layout = QVBoxLayout(group_format)
        fmt_layout.setSpacing(6)
        fmt_layout.setContentsMargins(6,6,6,6)
        self.combo_format = QComboBox()
        self.combo_format.addItems(["JPG", "PNG", "WEBP"])
        self.slider_quality = QSlider(Qt.Orientation.Horizontal)
        self.slider_quality.setRange(10, 100)
        self.slider_quality.setValue(85)
        fmt_layout.addWidget(QLabel("输出格式"))
        fmt_layout.addWidget(self.combo_format)
        fmt_layout.addWidget(QLabel("品质"))
        fmt_layout.addWidget(self.slider_quality)
        control_layout.addWidget(group_format)

        control_layout.addStretch(1)

        center_layout.addWidget(preview_widget)
        center_layout.addWidget(control_widget)
        main_layout.addLayout(center_layout, stretch=1)

        # ========= 底部日志 =========
        self.log_text = QTextEdit()
        self.log_text.setMinimumHeight(50)
        self.log_text.setMaximumHeight(70)
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text)
