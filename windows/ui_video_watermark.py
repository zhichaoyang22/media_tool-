# ui_video_watermark.py
# 纯UI定义文件：只构造控件、布局、样式，不写业务逻辑，不绑定信号
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QGroupBox, QLineEdit, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt
class Ui_VideoWatermarkPage:
    """纯UI组装类，类似pyuic生成的ui代码风格"""
    def setup_ui(self, parent_widget: QWidget):
        """传入父容器，构建全部界面；控件全部存为self.xxx，外部可访问"""
        # ==========修复点==========
        root_layout = QHBoxLayout()
        parent_widget.setLayout(root_layout)
        # ==========================
        root_layout.setContentsMargins(12,12,12,12)
        root_layout.setSpacing(12)
        # ========== 左侧区域【修改为self.left_container】 ==========
        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setSpacing(10)
        self.btn_back = QPushButton("返回首页")
        self.btn_back.setStyleSheet("""
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
        self.label_preview = QLabel("视频预览区域")
        self.label_preview.setMinimumSize(800, 450)
        self.label_preview.setStyleSheet("""
        QLabel {
            background-color: #1e1e2e;
            border: 2px solid #89b4fa;
            border-radius: 8px;
            color: #cccccc;
            font-size: 14px;
        }""")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_btn_layout = QHBoxLayout()
        self.btn_select_video = QPushButton("选择视频")
        self.btn_select_video.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }""")
        self.btn_frame_prev = QPushButton("上一帧")
        self.btn_frame_prev.setEnabled(False)
        self.btn_frame_prev.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:disabled {background-color:#444;color:#777;}
        QPushButton:hover:!disabled {background-color:#b4befe;}
        """)
        self.btn_frame_next = QPushButton("下一帧")
        self.btn_frame_next.setEnabled(False)
        self.btn_frame_next.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:disabled {background-color:#444;color:#777;}
        QPushButton:hover:!disabled {background-color:#b4befe;}
        """)
        self.btn_del_video = QPushButton("删除视频")
        self.btn_del_video.setStyleSheet("""
        QPushButton {
            background-color: #f38ba8;
            color: #1e1e2e;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #f2cdcd;
        }""")
        bottom_btn_layout.addWidget(self.btn_select_video)
        bottom_btn_layout.addWidget(self.btn_frame_prev)
        bottom_btn_layout.addWidget(self.btn_frame_next)
        bottom_btn_layout.addWidget(self.btn_del_video)
        left_layout.addWidget(self.btn_back)
        left_layout.addWidget(self.label_preview)
        left_layout.addLayout(bottom_btn_layout)
        # ========== 右侧区域【修改为self.right_container】 ==========
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setSpacing(10)
        # 输出配置
        group_output = QGroupBox("输出配置")
        group_output.setStyleSheet("""
        QGroupBox {
            color: #89b4fa;
            font-weight: bold;
            border: 1px solid #89b4fa;
            border-radius: 8px;
            margin-top: 10px;
            padding:10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left:10px;
            padding:0 5px;
        }""")
        g_out_layout = QHBoxLayout(group_output)
        self.edit_output = QLineEdit()
        self.edit_output.setStyleSheet("""
        QLineEdit {
            background-color:#1e1e2e;
            border:1px solid #89b4fa;
            color:#cccccc;
            border-radius:4px;
            padding:8px;
        }""")
        self.btn_out_select = QPushButton("选择")
        self.btn_out_select.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 8px 14px;
            border-radius:4px;
            font-weight:bold;
        }
        QPushButton:hover {
            background-color:#b4befe;
        }""")
        g_out_layout.addWidget(self.edit_output)
        g_out_layout.addWidget(self.btn_out_select)
        right_layout.addWidget(group_output)
        # 水印参数
        group_wm = QGroupBox("水印区域参数")
        group_wm.setStyleSheet("""
        QGroupBox {
            color: #89b4fa;
            font-weight: bold;
            border: 1px solid #89b4fa;
            border-radius: 8px;
            margin-top: 10px;
            padding:10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left:10px;
            padding:0 5px;
        }""")
        g_wm_layout = QVBoxLayout(group_wm)
        self.edit_watermark_rect = QLineEdit()
        self.edit_watermark_rect.setPlaceholderText("例如：10,460,700,60")
        self.edit_watermark_rect.setStyleSheet("""
        QLineEdit {
            background-color:#1e1e2e;
            border:1px solid #89b4fa;
            color:#cccccc;
            border-radius:4px;
            padding:8px;
        }""")
        self.btn_auto_detect = QPushButton("自动识别水印")
        self.btn_auto_detect.setStyleSheet("""
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 8px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color:#b4befe;
        }""")
        self.btn_clear = QPushButton("清除坐标")
        self.btn_clear.setStyleSheet("""
        QPushButton {
            background-color: #f38ba8;
            color: #1e1e2e;
            border: none;
            padding:8px;
            border-radius:6px;
            font-weight:bold;
        }
        QPushButton:hover {
            background-color:#f2cdcd;
        }""")
        g_wm_layout.addWidget(self.edit_watermark_rect)
        g_wm_layout.addWidget(self.btn_auto_detect)
        g_wm_layout.addWidget(self.btn_clear)
        right_layout.addWidget(group_wm)
        # 处理控制
        group_ctrl = QGroupBox("处理控制")
        group_ctrl.setStyleSheet("""
        QGroupBox {
            color: #89b4fa;
            font-weight: bold;
            border: 1px solid #89b4fa;
            border-radius: 8px;
            margin-top: 10px;
            padding:10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left:10px;
            padding:0 5px;
        }""")
        g_ctrl_layout = QVBoxLayout(group_ctrl)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
        QProgressBar {
            background-color:#1e1e2e;
            border:1px solid #89b4fa;
            border-radius:4px;
            text-align:center;
            color:#ffffff;
            height:20px;
        }
        QProgressBar::chunk {
            background-color:#89b4fa;
            border-radius:3px;
        }""")
        self.btn_start = QPushButton("开始处理")
        self.btn_start.setEnabled(False)
        self.btn_start.setStyleSheet("""
        QPushButton {
            background-color: #a6e3a1;
            color: #1e1e2e;
            border: none;
            padding:10px;
            border-radius:6px;
            font-weight:bold;
        }
        QPushButton:disabled {
            background-color:#444444;
            color:#777777;
        }
        QPushButton:hover:!disabled {
            background-color:#b4befe;
        }""")
        self.btn_cancel = QPushButton("取消任务")
        self.btn_cancel.setStyleSheet("""
        QPushButton {
            background-color: #f38ba8;
            color: #1e1e2e;
            border: none;
            padding:10px;
            border-radius:6px;
            font-weight:bold;
        }
        QPushButton:hover {
            background-color:#f2cdcd;
        }""")
        g_ctrl_layout.addWidget(self.progress_bar)
        g_ctrl_layout.addWidget(self.btn_start)
        g_ctrl_layout.addWidget(self.btn_cancel)
        right_layout.addWidget(group_ctrl)
        # 日志
        group_log = QGroupBox("运行日志")
        group_log.setStyleSheet("""
        QGroupBox {
            color: #89b4fa;
            font-weight: bold;
            border: 1px solid #89b4fa;
            border-radius: 8px;
            margin-top: 10px;
            padding:10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left:10px;
            padding:0 5px;
        }""")
        log_layout = QVBoxLayout(group_log)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
        QTextEdit {
            background-color:#1e1e2e;
            border:1px solid #89b4fa;
            color:#cccccc;
            border-radius:4px;
            padding:8px;
            font-size:13px;
        }""")
        log_layout.addWidget(self.log_text)
        right_layout.addWidget(group_log)
        root_layout.addWidget(self.left_container, stretch=3)
        root_layout.addWidget(self.right_container, stretch=2)
