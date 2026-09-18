from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDoubleSpinBox, QSlider, QGroupBox, QTextEdit, QFrame, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt
class Ui_VideoEditPage(object):
    def setupUi(self, VideoEditPage):
        VideoEditPage.setObjectName("VideoEditPage")
        VideoEditPage.resize(1480, 920)
        main_layout = QHBoxLayout(VideoEditPage)
        main_layout.setContentsMargins(18,18,18,18)
        main_layout.setSpacing(20)
        # ========== 左侧预览区域 ==========
        self.left_widget = QFrame()
        self.left_widget.setObjectName("left_widget")
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(12,12,12,12)
        left_layout.setSpacing(12)
        self.preview_container = QFrame()
        self.preview_container.setObjectName("preview_container")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setContentsMargins(0,0,0,0)
        self.preview_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_container.setMinimumSize(400,300)
        self.label_preview = QLabel()
        self.label_preview.setObjectName("frame_label")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview.setStyleSheet("background-color: transparent;")
        self.label_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        preview_layout.addWidget(self.label_preview)
        left_layout.addWidget(self.preview_container, stretch=1)
        # 底部控制栏
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0,0,0,0)
        bottom_layout.setSpacing(12)
        self.slider_progress = QSlider(Qt.Orientation.Horizontal)
        self.slider_progress.setObjectName("slider_progress")
        self.btn_open = QPushButton("打开视频")
        self.btn_play = QPushButton("播放 / 暂停")
        self.btn_set_start = QPushButton("设置起始点")
        self.btn_set_end = QPushButton("设置结束点")
        self.btn_clear = QPushButton("清空")
        self.btn_back_home = QPushButton("返回首页")
        bottom_layout.addWidget(self.slider_progress)
        bottom_layout.addWidget(self.btn_open)
        bottom_layout.addWidget(self.btn_play)
        bottom_layout.addWidget(self.btn_set_start)
        bottom_layout.addWidget(self.btn_set_end)
        bottom_layout.addWidget(self.btn_clear)
        bottom_layout.addWidget(self.btn_back_home)
        left_layout.addWidget(bottom_bar)
        # ========== 右侧控制面板 ==========
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(14)
        # 组1：播放速度
        group_speed = QGroupBox("播放速度")
        group_speed_layout = QVBoxLayout(group_speed)
        group_speed_layout.setContentsMargins(12,16,12,12)
        group_speed_layout.setSpacing(8)
        self.double_speed = QDoubleSpinBox()
        self.double_speed.setRange(0.25, 4.0)
        self.double_speed.setValue(1.0)
        group_speed_layout.addWidget(QLabel("倍速:"))
        group_speed_layout.addWidget(self.double_speed)
        # 组2：调色参数
        group_color = QGroupBox("调色")
        group_color_layout = QVBoxLayout(group_color)
        group_color_layout.setContentsMargins(12,16,12,12)
        group_color_layout.setSpacing(8)
        self.double_bright = QDoubleSpinBox()
        self.double_bright.setRange(-1.0,1.0)
        self.double_bright.setValue(0.0)
        self.double_contrast = QDoubleSpinBox()
        self.double_contrast.setRange(-1.0,1.0)
        self.double_contrast.setValue(0.0)
        self.double_saturation = QDoubleSpinBox()
        self.double_saturation.setRange(-1.0,1.0)
        self.double_saturation.setValue(0.0)
        group_color_layout.addWidget(QLabel("亮度"))
        group_color_layout.addWidget(self.double_bright)
        group_color_layout.addWidget(QLabel("对比度"))
        group_color_layout.addWidget(self.double_contrast)
        group_color_layout.addWidget(QLabel("饱和度"))
        group_color_layout.addWidget(self.double_saturation)
        # 组3：导出
        group_export = QGroupBox("导出")
        group_export_layout = QVBoxLayout(group_export)
        group_export_layout.setContentsMargins(12,16,12,12)
        group_export_layout.setSpacing(10)
        self.btn_export = QPushButton("导出剪辑视频")
        # 新增进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        group_export_layout.addWidget(self.btn_export)
        group_export_layout.addWidget(self.progress_bar)
        # 日志输出
        group_log = QGroupBox("日志输出")
        group_log_layout = QVBoxLayout(group_log)
        group_log_layout.setContentsMargins(12,16,12,12)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        group_log_layout.addWidget(self.log_text)
        right_layout.addWidget(group_speed)
        right_layout.addWidget(group_color)
        right_layout.addWidget(group_export)
        right_layout.addWidget(group_log, stretch=1)
        # 固定左右3:1拉伸比例
        main_layout.addWidget(self.left_widget, stretch=3)
        main_layout.addWidget(self.right_widget, stretch=1)
        # ========== 全局样式表 ==========
        VideoEditPage.setStyleSheet("""
            QWidget {
                background-color: #191923;
                color: #f0f0f5;
                font-family: Microsoft YaHei;
                font-size:13px;
            }
            QGroupBox {
                background-color:#242432;
                border-radius:10px;
                border:1px solid #34344a;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left:10px;
                padding:0 6px;
                color:#ffffff;
            }
            QPushButton{
                background-color:#333348;
                border-radius:7px;
                border:none;
                padding:7px 12px;
                color:#fff;
            }
            QPushButton:hover{
                background-color:#44445c;
            }
            QPushButton#btn_export{
                background-color:#2563eb;
            }
            QPushButton#btn_export:hover{
                background-color:#3b82f6;
            }
            QDoubleSpinBox {
                background-color:#2c2c3f;
                border:1px solid #3a3a54;
                border-radius:6px;
                color:#fff;
                min-height:28px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width:22px;
                background-color:#383852;
                border-radius:4px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color:#484868;
            }
            QDoubleSpinBox::up-arrow {
                width: 8px;
                height:8px;
            }
            QDoubleSpinBox::down-arrow {
                width:8px;
                height:8px;
            }
            QSlider{
                background-color:#2c2c3f;
                border:1px solid #3a3a54;
                border-radius:6px;
                color:#fff;
            }
            QTextEdit{
                background-color:#12121b;
                border:1px solid #34344a;
                border-radius:8px;
                color:#b8b8cc;
            }
            QFrame#left_widget{
                background-color:#000000;
                border:2px solid #2c2c3f;
                border-radius:12px;
            }
            QFrame#preview_container{
                background-color:#000000;
                border-radius:8px;
            }
            QProgressBar{
                background-color:#2c2c3f;
                border-radius:4px;
                height:8px;
                text-align:center;
            }
            QProgressBar::chunk{
                background-color:#2563eb;
                border-radius:4px;
            }
        """)
