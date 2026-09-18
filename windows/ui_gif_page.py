from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QTextEdit, QProgressBar,
    QSpinBox, QDoubleSpinBox, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt
class Ui_GifPage(object):
    def setupUi(self, GifPage):
        GifPage.setObjectName("GifPage")
        GifPage.resize(1000, 700)
        main_layout = QHBoxLayout(GifPage)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        # --------------------------
        # 左侧预览区
        # --------------------------
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a2c;
                border: 1px solid #2c2c44;
                border-radius: 12px;
            }
        """)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)
        self.btn_back = QPushButton("返回首页")
        self.btn_back.setMinimumHeight(38)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #2c2c44;
                color: #ffffff;
                border: 1px solid #383858;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #383858;
                border-color: #484868;
            }
            QPushButton:pressed {
                background-color: #252538;
            }
        """)
        self.label_preview = QLabel()
        self.label_preview.setMinimumSize(480, 360)
        self.label_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label_preview.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 1px solid #2c2c44;
                border-radius: 8px;
                color: #888888;
            }
        """)
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_row = QHBoxLayout()
        self.btn_prev_frame = QPushButton("上一帧")
        self.btn_next_frame = QPushButton("下一帧")
        self.btn_prev_frame.setEnabled(False)
        self.btn_next_frame.setEnabled(False)
        for btn in [self.btn_prev_frame, self.btn_next_frame]:
            btn.setMinimumHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c44;
                    color: #ffffff;
                    border: 1px solid #383858;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #383858;
                }
                QPushButton:disabled {
                    background-color: #222233;
                    color: #777788;
                    border-color: #282838;
                }
            """)
        frame_row.addWidget(self.btn_prev_frame)
        frame_row.addWidget(self.btn_next_frame)
        left_layout.addWidget(self.btn_back)
        left_layout.addWidget(self.label_preview, stretch=1)
        left_layout.addLayout(frame_row)
        main_layout.addWidget(left_widget, stretch=3)
        # --------------------------
        # 右侧参数区（按你的建议，多组横向行布局）
        # --------------------------
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a2c;
                border: 1px solid #2c2c44;
                border-radius: 12px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)
        # 工具函数：一行放两个控件（label+输入框 成对）
        def add_two_param_row(layout, label1, widget1, label2, widget2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)
            # 左边一组
            col1 = QVBoxLayout()
            col1.setSpacing(4)
            lab1 = QLabel(label1)
            lab1.setStyleSheet("color:#ddddf0; font-size:13px;")
            widget1.setMinimumHeight(36)
            widget1.setStyleSheet("""
                QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #252538;
                    border: 1px solid #353550;
                    border-radius: 6px;
                    padding: 6px 8px;
                    color: #ffffff;
                    font-size:13px;
                }
            """)
            col1.addWidget(lab1)
            col1.addWidget(widget1)
            # 右边一组
            col2 = QVBoxLayout()
            col2.setSpacing(4)
            lab2 = QLabel(label2)
            lab2.setStyleSheet("color:#ddddf0; font-size:13px;")
            widget2.setMinimumHeight(36)
            widget2.setStyleSheet(widget1.styleSheet())
            col2.addWidget(lab2)
            col2.addWidget(widget2)
            row_layout.addLayout(col1, stretch=1)
            row_layout.addLayout(col2, stretch=1)
            layout.addLayout(row_layout)
        # 工具函数：一行两个按钮
        def add_two_btn_row(layout, btn1, btn2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)
            for btn in [btn1, btn2]:
                btn.setMinimumHeight(38)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c44;
                        color: #ffffff;
                        border: 1px solid #383858;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-size: 13px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #383858;
                    }
                    QPushButton:pressed {
                        background-color: #252538;
                    }
                """)
                row_layout.addWidget(btn, stretch=1)
            layout.addLayout(row_layout)
        # ========== 第一行：选择视频 + 卸载视频 ==========
        self.btn_select_video = QPushButton("选择视频")
        self.btn_del_video = QPushButton("卸载视频")
        add_two_btn_row(right_layout, self.btn_select_video, self.btn_del_video)
        # ========== 第二行：起始帧 + 结束帧 ==========
        self.spin_start_frame = QSpinBox()
        self.spin_end_frame = QSpinBox()
        add_two_param_row(right_layout, "起始帧", self.spin_start_frame, "结束帧", self.spin_end_frame)
        # ========== 第三行：GIF帧率（单独一行） ==========
        lab_fps = QLabel("GIF帧率")
        lab_fps.setStyleSheet("color:#ddddf0; font-size:13px;")
        self.spin_fps = QSpinBox()
        self.spin_fps.setMinimumHeight(36)
        self.spin_fps.setStyleSheet("""
            QSpinBox {
                background-color: #252538;
                border: 1px solid #353550;
                border-radius: 6px;
                padding: 6px 8px;
                color: #ffffff;
                font-size:13px;
            }
        """)
        right_layout.addWidget(lab_fps)
        right_layout.addWidget(self.spin_fps)
        # ========== 第四行：缩放比例 + 循环次数 ==========
        self.spin_scale = QDoubleSpinBox()
        self.spin_loop = QSpinBox()
        add_two_param_row(right_layout, "缩放比例", self.spin_scale, "循环次数(0无限)", self.spin_loop)
        # ========== 新增第五行：动画倍速 ==========
        self.spin_speed = QDoubleSpinBox()
        add_two_param_row(right_layout, "动画倍速", self.spin_speed, "", QLabel(""))
        # ========== 选择输出路径 ==========
        self.btn_select_out = QPushButton("选择输出路径")
        self.edit_out_path = QLineEdit()
        self.edit_out_path.setReadOnly(True)
        self.edit_out_path.setMinimumHeight(36)
        self.edit_out_path.setStyleSheet("""
            QLineEdit {
                background-color: #252538;
                border: 1px solid #353550;
                border-radius: 6px;
                padding: 6px 8px;
                color: #ffffff;
                font-size:13px;
            }
        """)
        self.btn_select_out.setMinimumHeight(38)
        self.btn_select_out.setStyleSheet("""
            QPushButton {
                background-color: #2c2c44;
                color: #ffffff;
                border: 1px solid #383858;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #383858;
            }
        """)
        right_layout.addWidget(self.btn_select_out)
        right_layout.addWidget(self.edit_out_path)
        # ========== 开始生成 / 取消任务 ==========
        self.btn_start = QPushButton("开始生成GIF")
        self.btn_cancel = QPushButton("取消任务")
        self.btn_cancel.setEnabled(False)
        for btn in [self.btn_start, self.btn_cancel]:
            btn.setMinimumHeight(42)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3050ff;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4060ff;
                }
                QPushButton:pressed {
                    background-color: #2840d0;
                }
                QPushButton:disabled {
                    background-color: #222233;
                    color: #777788;
                }
            """)
        right_layout.addWidget(self.btn_start)
        right_layout.addWidget(self.btn_cancel)
        # ========== 进度条 + 日志 ==========
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(26)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #222235;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3050ff;
                border-radius: 6px;
            }
        """)
        right_layout.addWidget(self.progress_bar)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #151522;
                border: 1px solid #303048;
                border-radius: 6px;
                color: #ccccdd;
                font-size: 12px;
                padding: 6px;
            }
        """)
        right_layout.addWidget(self.log_text)
        right_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(right_widget, stretch=2)
        GifPage.setStyleSheet("""
            QWidget {
                background-color: #121220;
                color: #eeeeee;
                font-size: 13px;
            }
        """)
