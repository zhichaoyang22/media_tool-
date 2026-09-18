from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QTextEdit,
                             QProgressBar, QSpinBox, QFrame,
                             QComboBox)
from PyQt6.QtCore import Qt


class Ui_VideoBgRemovePage(object):
    def setupUi(self, VideoBgRemovePage):
        VideoBgRemovePage.setObjectName("VideoBgRemovePage")
        VideoBgRemovePage.resize(1300, 820)

        # 顶层布局，放返回按钮
        top_layout = QVBoxLayout(VideoBgRemovePage)
        top_layout.setContentsMargins(20, 20, 20, 20)
        top_layout.setSpacing(12)

        top_bar_layout = QHBoxLayout()
        self.btn_back_home = QPushButton("返回首页")
        self.btn_back_home.setObjectName("btnBack")
        self.btn_back_home.setFixedSize(110,34)
        # 直接添加按钮，不添加弹性拉伸，按钮就在最左侧
        top_bar_layout.addWidget(self.btn_back_home)
        # addStretch放在末尾，占用剩余空间，防止按钮被拉伸
        top_bar_layout.addStretch(1)
        top_layout.addLayout(top_bar_layout)


        self.container = QFrame()
        self.container.setObjectName("pageContainer")
        top_layout.addWidget(self.container)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(16)

        # ========= 左侧预览区，删掉底部两个标签 =========
        self.left_group = QGroupBox("视频预览")
        self.left_group.setObjectName("previewGroup")
        left_layout = QVBoxLayout(self.left_group)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        self.label_preview = QLabel("预览窗口\n请导入视频")
        self.label_preview.setObjectName("labelPreview")
        self.label_preview.setMinimumSize(640, 480)
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.label_preview)

        container_layout.addWidget(self.left_group, stretch=3)

        # ========= 右侧参数区 =========
        self.right_group = QGroupBox("参数设置")
        self.right_group.setObjectName("paramGroup")
        right_layout = QVBoxLayout(self.right_group)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)

        self.label_model = QLabel("抠图模型：u2net")
        self.label_model.setObjectName("infoLabel")
        right_layout.addWidget(self.label_model)

        sample_layout = QHBoxLayout()
        sample_layout.setSpacing(10)
        self.label_sample = QLabel("帧采样间隔")
        self.label_sample.setObjectName("fieldLabel")
        self.spin_sample = QSpinBox()
        self.spin_sample.setObjectName("spinBox")
        self.spin_sample.setRange(1, 30)
        self.spin_sample.setValue(1)
        self.spin_sample.setFixedWidth(100)
        sample_layout.addWidget(self.label_sample)
        sample_layout.addWidget(self.spin_sample)
        sample_layout.addStretch(1)
        right_layout.addLayout(sample_layout)

        # 导出格式选择
        format_layout = QHBoxLayout()
        format_layout.setSpacing(10)
        self.label_format = QLabel("导出格式")
        self.label_format.setObjectName("fieldLabel")
        self.combo_format = QComboBox()
        self.combo_format.setObjectName("comboBox")
        self.combo_format.addItem("MP4", "mp4")
        self.combo_format.addItem("MOV(透明通道)", "mov")
        self.combo_format.setFixedWidth(140)
        format_layout.addWidget(self.label_format)
        format_layout.addWidget(self.combo_format)
        format_layout.addStretch(1)
        right_layout.addLayout(format_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        right_layout.addWidget(self.progress_bar)

        self.label_status = QLabel("状态：等待导入视频")
        self.label_status.setObjectName("statusLabel")
        right_layout.addWidget(self.label_status)

        self.label_output_file = QLabel("输出文件：未导出")
        self.label_output_file.setObjectName("outputFileLabel")
        right_layout.addWidget(self.label_output_file)

        # 右侧按钮垂直排列
        action_btn_layout = QVBoxLayout()
        action_btn_layout.setSpacing(10)

        self.btn_open = QPushButton("导入视频")
        self.btn_open.setObjectName("btnNormal")
        self.btn_open.setFixedHeight(40)

        self.btn_start = QPushButton("开始抠除背景")
        self.btn_start.setObjectName("btnAccent")
        self.btn_start.setFixedHeight(40)

        self.btn_save = QPushButton("导出视频")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setEnabled(False)

        self.btn_reset = QPushButton("重置")
        self.btn_reset.setObjectName("btnNormal")
        self.btn_reset.setFixedHeight(40)

        action_btn_layout.addWidget(self.btn_open)
        action_btn_layout.addWidget(self.btn_start)
        action_btn_layout.addWidget(self.btn_save)
        action_btn_layout.addWidget(self.btn_reset)
        right_layout.addLayout(action_btn_layout)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("运行日志...")
        self.log_text.setFixedHeight(120)
        right_layout.addWidget(self.log_text)

        right_layout.addStretch(1)
        container_layout.addWidget(self.right_group, stretch=2)

        # ========= 全局深色样式 =========
        VideoBgRemovePage.setStyleSheet("""
            QWidget#VideoBgRemovePage {
                background-color: #1a1a27;
            }
            QPushButton#btnBack{
                background-color:#34344a;
                border:1px solid #464662;
                border-radius:8px;
                color:#fff;
            }
            QPushButton#btnBack:hover{
                background-color:#40405a;
            }
            QFrame#pageContainer {
                background-color: #242435;
                border: 1px solid #2f2f42;
                border-radius: 16px;
            }
            QGroupBox {
                color: #e8e8f0;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2f2f42;
                border-radius: 14px;
                background-color: #1e1e2c;
                margin-top: 12px;
                padding-top: 18px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                left: 14px;
                top: 6px;
                color: #ffffff;
            }
            QLabel#labelPreview {
                background-color: #12121c;
                border: 2px dashed #3a3a55;
                border-radius: 12px;
                color: #7a7a95;
                font-size: 14px;
            }
            QLabel#infoLabel, QLabel#fieldLabel {
                color: #cfcfe6;
                font-size: 13px;
                background-color: transparent;
            }
            QLabel#statusLabel {
                color: #9aa7ff;
                font-size: 12px;
                background-color: transparent;
            }
            QLabel#outputFileLabel {
                color: #8fd18f;
                font-size: 12px;
                background-color: transparent;
            }
            QPushButton {
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btnPrimary {
                background-color: #3b5bdb;
            }
            QPushButton#btnPrimary:hover {
                background-color: #4f72e8;
            }
            QPushButton#btnNormal {
                background-color: #34344a;
                border: 1px solid #464662;
            }
            QPushButton#btnNormal:hover {
                background-color: #40405a;
            }
            QPushButton#btnAccent {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3050ff, stop:1 #b828b8);
            }
            QPushButton#btnAccent:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4566ff, stop:1 #cf3ed1);
            }
            QPushButton:disabled {
                background-color: #2a2a3a;
                color: #6a6a85;
            }
            QSpinBox, QComboBox {
                background-color: #12121c;
                border: 1px solid #3a3a55;
                border-radius: 8px;
                color: #ffffff;
                padding: 4px 8px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #2a2a3a;
                width: 16px;
            }
            QComboBox::drop-down {
                background-color: #2a2a3a;
                width: 20px;
            }
            QProgressBar {
                background-color: #12121c;
                border: none;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3050ff, stop:1 #b828b8);
                border-radius: 5px;
            }
            QTextEdit#logText {
                background-color: #12121c;
                border: 1px solid #2f2f42;
                border-radius: 10px;
                color: #cfcfe6;
                font-size: 12px;
                padding: 8px;
            }
        """)
