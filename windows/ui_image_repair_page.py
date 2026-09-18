from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QGroupBox, QTextEdit, QSizePolicy, QComboBox, QProgressBar)
from PyQt6.QtCore import Qt


class Ui_ImageRepairPage(object):
    def setupUi(self, ImageRepairPage):
        ImageRepairPage.setObjectName("ImageRepairPage")
        ImageRepairPage.resize(1200, 760)

        main_layout = QHBoxLayout(ImageRepairPage)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(20)

        # ========== 左侧预览区域 ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.btn_back = QPushButton("返回首页")
        self.btn_back.setFixedHeight(42)
        self.btn_back.setStyleSheet("""
            QPushButton{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3b6ef8, stop:1 #8b3cf0);
                color:white;
                border-radius:8px;
                font-size:14px;
                font-weight:bold;
            }
            QPushButton:hover{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5480fa, stop:1 #9f58f5);
            }
        """)
        left_layout.addWidget(self.btn_back)

        self.label_preview = QLabel()
        self.label_preview.setMinimumSize(600, 500)
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview.setText("图片预览区域")
        self.label_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label_preview.setStyleSheet("""
            color:#999999;
            background:#111118;
            border-radius:8px;
            border:1px solid #27273a;
        """)
        left_layout.addWidget(self.label_preview)

        main_layout.addWidget(left_widget, stretch=3)

        # ========== 右侧控制面板 ==========
        right_widget = QWidget()
        right_widget.setFixedWidth(320)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        # 媒体类型
        group_type = QGroupBox("媒体类型")
        group_type.setStyleSheet("""
            QGroupBox{
                color:#e8e8f0;
                font-size:13px;
                font-weight:500;
            }
            QGroupBox::title{
                subcontrol-origin: margin;
                left:10px;
                padding:0 4px;
            }
        """)
        type_layout = QVBoxLayout(group_type)
        type_layout.setContentsMargins(12, 20, 12, 12)
        type_layout.setSpacing(8)

        self.combo_media = QComboBox()
        self.combo_media.addItems(["图片", "视频"])
        self.combo_media.setFixedHeight(30)
        self.combo_media.setStyleSheet(self._combo_style())
        type_layout.addWidget(self.combo_media)
        right_layout.addWidget(group_type)

        # 处理模式
        group_mode = QGroupBox("处理模式")
        group_mode.setStyleSheet("""
            QGroupBox{
                color:#e8e8f0;
                font-size:13px;
                font-weight:500;
            }
            QGroupBox::title{
                subcontrol-origin: margin;
                left:10px;
                padding:0 4px;
            }
        """)
        mode_layout = QVBoxLayout(group_mode)
        mode_layout.setContentsMargins(12, 20, 12, 12)
        mode_layout.setSpacing(8)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["添加马赛克", "传统修复遮挡"])
        self.combo_mode.setFixedHeight(30)
        self.combo_mode.setStyleSheet(self._combo_style())
        mode_layout.addWidget(self.combo_mode)
        right_layout.addWidget(group_mode)

        # 参数设置
        group_param = QGroupBox("参数设置")
        group_param.setStyleSheet("""
            QGroupBox{
                color:#e8e8f0;
                font-size:13px;
                font-weight:500;
            }
            QGroupBox::title{
                subcontrol-origin: margin;
                left:10px;
                padding:0 4px;
            }
        """)
        param_layout = QVBoxLayout(group_param)
        param_layout.setContentsMargins(12, 20, 12, 12)
        param_layout.setSpacing(10)

        self.label_block = QLabel("马赛克块大小：10")
        self.label_block.setStyleSheet("color:#e0e0eb;font-size:12px;")

        self.slider_block = QSlider(Qt.Orientation.Horizontal)
        self.slider_block.setRange(2, 50)
        self.slider_block.setValue(10)
        self.slider_block.setStyleSheet(self._slider_style())

        self.label_brush = QLabel("画笔大小：10")
        self.label_brush.setStyleSheet("color:#e0e0eb;font-size:12px;")

        self.slider_brush = QSlider(Qt.Orientation.Horizontal)
        self.slider_brush.setRange(2, 60)
        self.slider_brush.setValue(10)
        self.slider_brush.setStyleSheet(self._slider_style())

        tip_label = QLabel("提示：在图片上按住鼠标拖动涂抹区域")
        tip_label.setStyleSheet("color:#a0a0b8;font-size:11px;")
        tip_label.setWordWrap(True)

        param_layout.addWidget(self.label_block)
        param_layout.addWidget(self.slider_block)
        param_layout.addWidget(self.label_brush)
        param_layout.addWidget(self.slider_brush)
        param_layout.addWidget(tip_label)
        right_layout.addWidget(group_param)

        # 操作
        group_op = QGroupBox("操作")
        group_op.setStyleSheet("""
            QGroupBox{
                color:#e8e8f0;
                font-size:13px;
                font-weight:500;
            }
            QGroupBox::title{
                subcontrol-origin: margin;
                left:10px;
                padding:0 4px;
            }
        """)
        op_layout = QVBoxLayout(group_op)
        op_layout.setContentsMargins(12, 20, 12, 12)
        op_layout.setSpacing(12)

        self.btn_open = QPushButton("打开文件")
        self.btn_open.setFixedHeight(40)
        self.btn_open.setStyleSheet("""
            QPushButton{
                background:#3b6ef8;
                color:white;
                border-radius:8px;
                font-size:14px;
            }
            QPushButton:hover{
                background:#5480fa;
            }
        """)

        self.btn_run = QPushButton("执行处理")
        self.btn_run.setFixedHeight(40)
        self.btn_run.setStyleSheet("""
            QPushButton{
                background:#8b3cf0;
                color:white;
                border-radius:8px;
                font-size:14px;
            }
            QPushButton:hover{
                background:#9f58f5;
            }
        """)

        row_btn = QHBoxLayout()
        row_btn.setSpacing(12)

        self.btn_save = QPushButton("导出文件")
        self.btn_save.setFixedHeight(34)
        self.btn_save.setStyleSheet(self._secondary_btn_style())

        self.btn_reset = QPushButton("重置选区")
        self.btn_reset.setFixedHeight(34)
        self.btn_reset.setStyleSheet(self._secondary_btn_style())

        row_btn.addWidget(self.btn_save)
        row_btn.addWidget(self.btn_reset)

        op_layout.addWidget(self.btn_open)
        op_layout.addWidget(self.btn_run)
        op_layout.addLayout(row_btn)
        right_layout.addWidget(group_op)

        # 处理进度
        progress_label = QLabel("处理进度")
        progress_label.setStyleSheet("color:#e8e8f0;font-size:13px;font-weight:500;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar{
                background:#222222;
                border-radius:6px;
            }
            QProgressBar::chunk{
                background:#7b61ff;
                border-radius:6px;
            }
        """)

        right_layout.addWidget(progress_label)
        right_layout.addWidget(self.progress_bar)

        # 日志
        group_log = QGroupBox("日志")
        group_log.setStyleSheet("""
            QGroupBox{
                color:#e8e8f0;
                font-size:13px;
                font-weight:500;
            }
            QGroupBox::title{
                subcontrol-origin: margin;
                left:10px;
                padding:0 4px;
            }
        """)
        log_layout = QVBoxLayout(group_log)
        log_layout.setContentsMargins(12, 20, 12, 12)
        log_layout.setSpacing(8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(90)
        self.log_text.setStyleSheet("""
            QTextEdit{
                background:#12121b;
                color:#c8c8dc;
                border:1px solid #2a2a3a;
                border-radius:6px;
            }
        """)
        log_layout.addWidget(self.log_text)
        right_layout.addWidget(group_log)

        main_layout.addWidget(right_widget)

    def _combo_style(self):
        return """
            QComboBox{
                background:#2a2a3a;
                color:#f0f0f8;
                border:1px solid #3a3a4e;
                border-radius:6px;
                padding-left:8px;
            }
            QComboBox::drop-down{
                border:none;
            }
            QComboBox:hover{
                background:#35354a;
            }
            QComboBox QAbstractItemView{
                background:#2a2a3a;
                color:#f0f0f8;
                border:1px solid #3a3a4e;
                outline:none;
            }
            QComboBox QAbstractItemView::item{
                color:#f0f0f8;
                min-height:26px;
                padding:2px;
            }
            QComboBox QAbstractItemView::item:hover{
                background:#35354a;
            }
        """

    def _slider_style(self):
        return """
            QSlider::groove:horizontal{
                background:#3a3a4e;
                height:4px;
                border-radius:2px;
            }
            QSlider::handle:horizontal{
                background:#3b6ef8;
                width:14px;
                height:14px;
                margin:-5px 0;
                border-radius:7px;
            }
        """

    def _secondary_btn_style(self):
        return """
            QPushButton{
                background:#2a2a3a;
                color:#e8e8f0;
                border:1px solid #3a3a4e;
                border-radius:6px;
                font-size:12px;
            }
            QPushButton:hover{
                background:#35354a;
            }
        """
