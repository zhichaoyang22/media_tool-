from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QGroupBox, QComboBox, QTextEdit, QCheckBox)
from PyQt6.QtCore import Qt
class Ui_ImageEnhancePage:
    def setupUi(self, parent_widget: QWidget):
        parent_widget.setObjectName("ImageEnhancePage")
        parent_widget.resize(1400, 880)
        root_layout = QHBoxLayout(parent_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(14)
        # ========== 左侧：上下预览 ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        # 原图预览
        self.label_origin = QLabel("原图预览")
        self.label_origin.setMinimumSize(700, 300)
        self.label_origin.setStyleSheet("""
        QLabel {
            background-color: #1e1e2e;
            border: 2px solid #89b4fa;
            border-radius: 8px;
            color: #cccccc;
        }""")
        self.label_origin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_origin.setScaledContents(False)
        # 增强结果预览
        self.label_result = QLabel("增强结果预览")
        self.label_result.setMinimumSize(700, 300)
        self.label_result.setStyleSheet("""
        QLabel {
            background-color: #1e1e2e;
            border: 2px solid #89b4fa;
            border-radius: 8px;
            color: #cccccc;
        }""")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_result.setScaledContents(False)
        left_layout.addWidget(self.label_origin)
        left_layout.addWidget(self.label_result)
        # ========== 右侧控制面板 ==========
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        self.btn_back_home = QPushButton("返回首页")
        self.btn_back_home.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }""")
        self.btn_open = QPushButton("打开素材")
        self.btn_open.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }""")
        self.btn_start = QPushButton("开始处理")
        self.btn_start.setStyleSheet("""
        QPushButton {
            background-color: #a6e3a1;
            color: #1e1e2e;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #94e2d5;
        }""")
        self.btn_export = QPushButton("导出文件")
        self.btn_export.setStyleSheet("""
        QPushButton {
            background-color: #a6e3a1;
            color: #1e1e2e;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #94e2d5;
        }""")
        self.btn_reset = QPushButton("重置所有参数")
        self.btn_reset.setStyleSheet("""
        QPushButton {
            background-color: #f9e2af;
            color: #1e1e2e;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #fab387;
        }""")
        right_layout.addWidget(self.btn_back_home)
        right_layout.addWidget(self.btn_open)
        right_layout.addWidget(self.btn_start)
        right_layout.addWidget(self.btn_export)
        self.check_enhance = QCheckBox("启用高清增强")
        self.check_enhance.setChecked(True)
        self.check_enhance.setStyleSheet("color:#cdd6f4; font-size:13px;")
        right_layout.addWidget(self.check_enhance)

        # ========= 删掉：增强模式、超分倍率两个GroupBox =========

        group_sample = QGroupBox("帧采样设置（视频/GIF）")
        group_sample.setStyleSheet("""
        QGroupBox{color:#89b4fa;font-weight:bold;border:1px solid #89b4fa;border-radius:8px;margin-top:6px;}
        QGroupBox::title{subcontrol-origin: margin;left:10px;padding:0 4px;}""")
        sample_layout = QVBoxLayout(group_sample)
        self.cbb_frame_sample = QComboBox()
        self.cbb_frame_sample.addItems(["全部帧", "每2帧取一帧", "每3帧取一帧"])
        sample_layout.addWidget(self.cbb_frame_sample)

        group_output = QGroupBox("输出设置")
        group_output.setStyleSheet("""
        QGroupBox{color:#89b4fa;font-weight:bold;border:1px solid #89b4fa;border-radius:8px;margin-top:6px;}
        QGroupBox::title{subcontrol-origin: margin;left:10px;padding:0 4px;}""")
        output_layout = QVBoxLayout(group_output)
        self.cbb_out_format = QComboBox()
        self.cbb_out_format.addItems(["jpg", "png", "webp", "gif", "mp4"])
        output_layout.addWidget(self.cbb_out_format)

        right_layout.addWidget(group_sample)
        right_layout.addWidget(group_output)
        right_layout.addWidget(self.btn_reset)

        # 日志框
        self.text_log = QTextEdit()
        self.text_log.setPlaceholderText("处理日志输出...")
        self.text_log.setMaximumHeight(140)
        self.text_log.setStyleSheet("""
        QTextEdit {
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 6px;
            color:#cdd6f4;
        }""")
        right_layout.addWidget(self.text_log)

        # 新增：进度百分比标签
        self.label_progress = QLabel("进度：0%")
        self.label_progress.setStyleSheet("""
        QLabel {
            color: #a6e3a1;
            font-size: 14px;
            font-weight: bold;
            padding: 6px 10px;
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 6px;
        }""")
        right_layout.addWidget(self.label_progress)

        root_layout.addWidget(left_widget, stretch=3)
        root_layout.addWidget(right_widget, stretch=1)