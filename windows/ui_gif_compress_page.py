from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QSlider, QGroupBox, QTextEdit, QSizePolicy,
                             QSpinBox, QFrame)
from PyQt6.QtCore import Qt
class Ui_GifCompressPage(object):
    def setupUi(self, GifCompressPage):
        GifCompressPage.setObjectName("GifCompressPage")
        GifCompressPage.resize(1280, 760)
        main_layout = QHBoxLayout(GifCompressPage)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ========== 左侧：顶部栏 + 原图/结果对比预览 ==========
        left_widget = QFrame()
        left_widget.setObjectName("leftWidget")
        left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # 顶部栏
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        self.btn_back = QPushButton("← 返回首页")
        self.btn_back.setObjectName("btn_back")
        self.btn_back.setFixedHeight(36)
        self.btn_back.setFixedWidth(130)
        top_spacer = QWidget()
        top_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(top_spacer)
        left_layout.addLayout(top_bar)

        # 对比预览容器【锁定布局，禁止被图片撑开】
        preview_container = QFrame()
        preview_container.setObjectName("previewContainer")
        preview_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        preview_layout = QHBoxLayout(preview_container)
        preview_layout.setContentsMargins(14, 14, 14, 14)
        preview_layout.setSpacing(14)

        # 原图预览Frame
        origin_frame = QFrame()
        origin_frame.setObjectName("originFrame")
        origin_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        origin_layout = QVBoxLayout(origin_frame)
        origin_layout.setSpacing(8)
        self.label_origin_title = QLabel("导入原图")
        self.label_origin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_origin_title.setStyleSheet("font-weight:bold;font-size:14px;color:#ddddff;")
        self.label_origin = QLabel("请打开GIF文件")
        self.label_origin.setObjectName("label_origin")
        self.label_origin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 核心：Label忽略图片尺寸，不撑开父布局
        self.label_origin.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.label_origin.setScaledContents(False)
        self.label_origin.setStyleSheet("color:#b8b8d4;font-size:14px;letter-spacing:1px;")
        origin_layout.addWidget(self.label_origin_title)
        origin_layout.addWidget(self.label_origin, stretch=1)

        # 结果预览Frame
        result_frame = QFrame()
        result_frame.setObjectName("resultFrame")
        result_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        result_layout = QVBoxLayout(result_frame)
        result_layout.setSpacing(8)
        self.label_result_title = QLabel("抠图完成效果")
        self.label_result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_result_title.setStyleSheet("font-weight:bold;font-size:14px;color:#ddddff;")
        self.label_result = QLabel("预览效果")
        self.label_result.setObjectName("label_result")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 核心：Label忽略图片尺寸，不撑开父布局
        self.label_result.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.label_result.setScaledContents(False)
        self.label_result.setStyleSheet("color:#b8b8d4;font-size:14px;letter-spacing:1px;")
        result_layout.addWidget(self.label_result_title)
        result_layout.addWidget(self.label_result, stretch=1)

        preview_layout.addWidget(origin_frame, stretch=1)
        preview_layout.addWidget(result_frame, stretch=1)
        left_layout.addWidget(preview_container, stretch=4)
        main_layout.addWidget(left_widget, stretch=4)

        # ========== 右侧：固定宽度面板，永远不会被挤压 ==========
        right_widget = QFrame()
        right_widget.setObjectName("rightWidget")
        right_widget.setFixedWidth(280) # 固定宽度，锁死！
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # 文件操作
        group_file = QGroupBox("文件操作")
        group_file.setObjectName("group_file")
        group_file_layout = QVBoxLayout(group_file)
        group_file_layout.setContentsMargins(12, 16, 12, 12)
        group_file_layout.setSpacing(10)
        self.btn_open = QPushButton("打开GIF")
        self.btn_export = QPushButton("导出GIF")
        self.btn_open.setObjectName("btn_open")
        self.btn_export.setObjectName("btn_export")
        self.btn_open.setFixedHeight(38)
        self.btn_export.setFixedHeight(38)
        group_file_layout.addWidget(self.btn_open)
        group_file_layout.addWidget(self.btn_export)
        right_layout.addWidget(group_file)

        # 播放控制
        group_play = QGroupBox("播放控制")
        group_play.setObjectName("group_play")
        group_play_layout = QVBoxLayout(group_play)
        group_play_layout.setContentsMargins(12, 16, 12, 12)
        group_play_layout.setSpacing(10)
        self.btn_play = QPushButton("播放 / 暂停")
        self.btn_play.setObjectName("btn_play")
        self.btn_play.setFixedHeight(34)
        self.slider_frame = QSlider(Qt.Orientation.Horizontal)
        self.slider_frame.setObjectName("slider_frame")
        self.label_fps = QLabel("帧间隔: 1.0s")
        self.label_fps.setObjectName("label_fps")
        self.label_fps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_play_layout.addWidget(self.btn_play)
        group_play_layout.addWidget(self.slider_frame)
        group_play_layout.addWidget(self.label_fps)
        right_layout.addWidget(group_play)

        # 压缩设置
        group_compress = QGroupBox("压缩设置")
        group_compress.setObjectName("group_compress")
        group_compress_layout = QVBoxLayout(group_compress)
        group_compress_layout.setContentsMargins(12, 16, 12, 12)
        group_compress_layout.setSpacing(8)
        self.spin_color_count = QSpinBox()
        self.spin_color_count.setRange(8, 256)
        self.spin_color_count.setValue(128)
        self.spin_color_count.setObjectName("spin_color_count")
        size_layout = QHBoxLayout()
        size_layout.setSpacing(6)
        self.spin_w = QSpinBox()
        self.spin_w.setRange(0, 4000)
        self.spin_w.setObjectName("spin_w")
        self.spin_h = QSpinBox()
        self.spin_h.setRange(0, 4000)
        self.spin_h.setObjectName("spin_h")
        size_layout.addWidget(QLabel("宽:"))
        size_layout.addWidget(self.spin_w)
        size_layout.addWidget(QLabel("高:"))
        size_layout.addWidget(self.spin_h)
        group_compress_layout.addWidget(QLabel("颜色数:"))
        group_compress_layout.addWidget(self.spin_color_count)
        group_compress_layout.addLayout(size_layout)
        right_layout.addWidget(group_compress)

        # AI背景抠除
        group_removebg = QGroupBox("AI背景抠除")
        group_removebg.setObjectName("group_removebg")
        group_removebg_layout = QVBoxLayout(group_removebg)
        group_removebg_layout.setContentsMargins(12, 16, 12, 12)
        group_removebg_layout.setSpacing(8)
        self.btn_ai_remove_bg = QPushButton("启用透明抠图")
        self.btn_ai_remove_bg.setObjectName("btn_ai_remove_bg")
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setRange(0, 100)
        self.slider_threshold.setValue(25)
        self.slider_threshold.setObjectName("slider_threshold")
        self.label_thresh = QLabel("抠图阈值: 25")
        self.label_thresh.setObjectName("label_thresh")
        self.label_thresh.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_removebg_layout.addWidget(self.btn_ai_remove_bg)
        group_removebg_layout.addWidget(self.slider_threshold)
        group_removebg_layout.addWidget(self.label_thresh)
        right_layout.addWidget(group_removebg)

        # 日志
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("运行日志...")
        self.log_text.setObjectName("log_text")
        self.log_text.setFixedHeight(90)
        right_layout.addWidget(self.log_text)
        right_layout.addStretch(1)
        main_layout.addWidget(right_widget)

        # ========== 暗黑样式 ==========
        GifCompressPage.setStyleSheet("""
            QWidget {
                background-color: #1c1c2e;
                color: #ffffff;
                font-size: 13px;
                font-family: Microsoft YaHei;
            }
            QPushButton {
                background-color: #343456;
                border: 1px solid #5048aa;
                border-radius: 8px;
                color: #ffffff;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #47477c;
                border-color: #7060ff;
            }
            QPushButton:pressed {
                background-color: #2c2c48;
            }
            #leftWidget,
            #rightWidget {
                background-color: transparent;
            }
            #previewContainer {
                background-color: #141424;
                border: 1px solid #2a2a44;
                border-radius: 14px;
            }
            #originFrame,
            #resultFrame {
                background-color: #111120;
                border: 1px dashed #424270;
                border-radius: 12px;
            }
            QGroupBox {
                background-color: #24243f;
                border: 1px solid #373760;
                border-radius: 12px;
                color: #e8e8ff;
                font-weight: bold;
                margin-top: 4px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #ddddff;
            }
            QSpinBox,
            QComboBox {
                background-color: #222238;
                border: 1px solid #3c3c68;
                border-radius: 6px;
                color: #ffffff;
                padding: 4px 6px;
            }
            QTextEdit {
                background-color: #151527;
                border: 1px solid #34345c;
                border-radius: 8px;
                color: #cfcfff;
                padding: 6px;
            }
            QSlider::groove:horizontal {
                background-color: #303050;
                height: 5px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #7055ff;
                width: 15px;
                height: 15px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)