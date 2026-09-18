import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QProgressBar, QTextEdit, QGroupBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QImage
from .base_page import BasePage
from .watermark_preview_canvas import PreviewCanvas, DarkMessageBox
from core.watermark_detector import WatermarkDetector

class ImageWatermarkPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(page_title="图片去水印", parent=parent)
        self.image_path = ""
        self.output_path = ""
        self.detector = WatermarkDetector(detect_threshold=22)
        self.setMinimumSize(960, 680)
        self._multi_watermark_rel = []
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # ========== 左侧画布区域 ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = PreviewCanvas(parent_page=self)
        # 绑定画布对外信号，只监听，不读写内部成员
        self.canvas.signal_image_changed.connect(self._on_canvas_image_changed)
        self.canvas.signal_selection_changed.connect(self._on_canvas_selection_changed)
        left_layout.addWidget(self.canvas)
        # 按钮容器：选择图片 + 删除图片
        btn_container = QWidget()
        btn_container_layout = QHBoxLayout(btn_container)
        btn_container_layout.setContentsMargins(10, 10, 10, 10)
        btn_container_layout.setSpacing(12)
        self.btn_open_file = QPushButton("选择图片")
        self.btn_open_file.setFixedSize(160, 44)
        self.btn_open_file.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#423880;
            border:none;
            border-radius:10px;
            font-size:14px;
        }
        QPushButton:hover{background-color:#5648aa;}
        QPushButton:pressed{background-color:#352e66;}
        """)
        self.btn_open_file.clicked.connect(self.select_image)
        self.btn_delete_img = QPushButton("删除图片")
        self.btn_delete_img.setFixedSize(160, 44)
        self.btn_delete_img.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#993848;
            border:none;
            border-radius:10px;
            font-size:14px;
        }
        QPushButton:hover{background-color:#b84456;}
        QPushButton:pressed{background-color:#7a2c38;}
        """)
        self.btn_delete_img.setVisible(False)
        self.btn_delete_img.clicked.connect(self._on_delete_image)
        btn_container_layout.addWidget(self.btn_open_file)
        btn_container_layout.addWidget(self.btn_delete_img)
        left_layout.addWidget(btn_container)
        main_layout.addWidget(left_widget, stretch=4)
        # ========== 右侧控制面板 ==========
        right_widget = QWidget()
        right_widget.setFixedWidth(340)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(16)
        right_layout.setContentsMargins(0, 0, 0, 0)
        group_style = """
        QGroupBox{
            color:#ffffff;
            font-size:14px;
            font-weight:bold;
            border:1px solid #383854;
            border-radius:12px;
            background-color:#222236;
            margin-top:8px;
        }
        QGroupBox::title{
            subcontrol-origin: margin;
            left:14px;
            top:2px;
            padding:0 6px;
        }
        """
        edit_style = """
        QLineEdit{
            background-color:#2a2a40;
            color:#e8e8f2;
            border:1px solid #383854;
            border-radius:8px;
            padding:0 10px;
            font-size:13px;
        }
        """
        btn_normal_style = """
        QPushButton{
            color:#ffffff;
            background-color:#343452;
            border:none;
            border-radius:8px;
            font-size:13px;
        }
        QPushButton:hover{background-color:#444466;}
        QPushButton:pressed{background-color:#2b2b42;}
        """
        # 输出配置
        grp_out = QGroupBox("输出配置")
        grp_out.setStyleSheet(group_style)
        lay_out = QVBoxLayout(grp_out)
        lay_out.setContentsMargins(14, 22, 14, 14)
        lay_out.setSpacing(12)
        row_out = QHBoxLayout()
        self.edit_output = QLineEdit()
        self.edit_output.setPlaceholderText("输出保存路径")
        self.edit_output.setFixedHeight(36)
        self.edit_output.setStyleSheet(edit_style)
        row_out.addWidget(self.edit_output, stretch=1)
        self.btn_select_out = QPushButton("选择")
        self.btn_select_out.setFixedWidth(70)
        self.btn_select_out.setFixedHeight(36)
        self.btn_select_out.setStyleSheet(btn_normal_style)
        self.btn_select_out.clicked.connect(self.select_output_path)
        row_out.addWidget(self.btn_select_out)
        lay_out.addLayout(row_out)
        right_layout.addWidget(grp_out)
        # 水印区域参数
        grp_watermark = QGroupBox("水印区域参数")
        grp_watermark.setStyleSheet(group_style)
        lay_wm = QVBoxLayout(grp_watermark)
        lay_wm.setContentsMargins(14, 22, 14, 14)
        lay_wm.setSpacing(12)
        tip_label = QLabel("鼠标在图片上拖框选择水印区域")
        tip_label.setStyleSheet("QLabel{color:#9494b8;font-size:12px;}")
        lay_wm.addWidget(tip_label)
        self.edit_region = QLineEdit()
        self.edit_region.setPlaceholderText("例如：10,460,700,60")
        self.edit_region.setFixedHeight(36)
        self.edit_region.setStyleSheet(edit_style)
        lay_wm.addWidget(self.edit_region)
        self.btn_auto_detect = QPushButton("自动识别水印")
        self.btn_auto_detect.setFixedHeight(38)
        self.btn_auto_detect.setStyleSheet(btn_normal_style)
        self.btn_auto_detect.clicked.connect(self.auto_detect_watermark)
        lay_wm.addWidget(self.btn_auto_detect)
        self.btn_clear_selection = QPushButton("清除选择")
        self.btn_clear_selection.setFixedHeight(38)
        self.btn_clear_selection.setStyleSheet(btn_normal_style)
        self.btn_clear_selection.clicked.connect(self.clear_selection)
        lay_wm.addWidget(self.btn_clear_selection)
        right_layout.addWidget(grp_watermark)
        # 处理控制
        grp_run = QGroupBox("处理控制")
        grp_run.setStyleSheet(group_style)
        lay_run = QVBoxLayout(grp_run)
        lay_run.setContentsMargins(14, 22, 14, 14)
        lay_run.setSpacing(12)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
        QProgressBar{
            background-color:#2a2a40;
            border:none;
            border-radius:6px;
            text-align:center;
            color:#ffffff;
        }
        QProgressBar::chunk{background-color:#5648aa;border-radius:6px;}
        """)
        lay_run.addWidget(self.progress_bar)
        self.btn_start = QPushButton("开始去除水印")
        self.btn_start.setFixedHeight(42)
        self.btn_start.setEnabled(False)
        self.btn_start.setStyleSheet("""
        QPushButton{
            color:#ffffff;
            background-color:#5648aa;
            border:none;
            border-radius:10px;
            font-size:14px;
            font-weight:bold;
        }
        QPushButton:hover:!disabled{background-color:#6b5bc2;}
        QPushButton:pressed:!disabled{background-color:#423880;}
        QPushButton:disabled{background-color:#343452;color:#707090;}
        """)
        self.btn_start.clicked.connect(self.start_remove_watermark)
        lay_run.addWidget(self.btn_start)
        right_layout.addWidget(grp_run)
        # 运行日志
        grp_log = QGroupBox("运行日志")
        grp_log.setStyleSheet(group_style)
        lay_log = QVBoxLayout(grp_log)
        lay_log.setContentsMargins(14, 22, 14, 14)
        lay_log.setSpacing(12)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(130)
        self.log_text.setStyleSheet("""
        QTextEdit{
            background-color:#2a2a40;
            color:#b4b4d8;
            border:1px solid #383854;
            border-radius:8px;
            font-size:12px;
        }
        """)
        lay_log.addWidget(self.log_text)
        right_layout.addWidget(grp_log)
        right_layout.addStretch(1)
        main_layout.addWidget(right_widget)
        self.content_layout.addLayout(main_layout)

    # --------------------------画布信号回调（仅更新UI，不碰canvas内部字段）--------------------------
    def _on_canvas_image_changed(self, has_image: bool):
        self.btn_delete_img.setVisible(has_image)
        self.btn_open_file.setEnabled(not has_image)
        if not has_image:
            self.image_path = ""
            self.edit_region.clear()
            self.edit_output.clear()
            self.output_path = ""
            self.progress_bar.setValue(0)
            self._multi_watermark_rel = []
        self.update_start_button()

    def _on_canvas_selection_changed(self, has_valid: bool):
        sel = self.canvas.get_selection()
        if sel:
            self.edit_region.setText(f"{sel['x']},{sel['y']},{sel['width']},{sel['height']}")
            self.log(f"已选择区域：x={sel['x']}, y={sel['y']}, w={sel['width']}, h={sel['height']}")
        else:
            self.edit_region.clear()
        self.update_start_button()

    def _on_delete_image(self):
        self.canvas.clear_all()
        self._multi_watermark_rel = []
        self.log("已删除图片，重置全部状态")

    # --------------------------页面业务方法--------------------------
    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return
        self.edit_region.clear()
        self.output_path = ""
        self.edit_output.clear()
        self.progress_bar.setValue(0)
        self._multi_watermark_rel = []
        self.log("全部重置，清空上一轮所有数据")
        self.image_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            DarkMessageBox.showWarning(self, "提示", "无法加载图片")
            return
        self.canvas.set_image(pixmap)
        self.log(f"已加载图片：{os.path.basename(path)}")

    def select_output_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存结果", "", "PNG图片 (*.png);;JPG图片 (*.jpg)"
        )
        if path:
            self.output_path = path
            self.edit_output.setText(path)
            self.log(f"输出路径：{path}")
            self.update_start_button()

    def auto_detect_watermark(self):
        if self.canvas.original_pixmap is None:
            QMessageBox.warning(self, "提示", "请先加载图片")
            return
        cw, ch = self.canvas.width(), self.canvas.height()
        if cw <= 20 or ch <= 20:
            QMessageBox.warning(self, "提示", "窗口还没渲染完成，请调整窗口大小")
            return
        self.log("开始自动识别水印区域...")
        q_img = self.canvas.original_pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        candidates = self.detector.scan_corner_regions(q_img)
        if len(candidates) == 0:
            QMessageBox.information(self, "提示", "未识别出水印，请手动框选")
            self.log("识别：未找到满足阈值水印")
            self.canvas.clear_selection()
            self._multi_watermark_rel = []
            return
        canvas_rects = []
        for item in candidates:
            r_orig = item["rect"]
            cx, cy, cw_rect, ch_rect = WatermarkDetector.original_rect_to_canvas(
                r_orig.x(), r_orig.y(), r_orig.width(), r_orig.height(),
                self.canvas.original_pixmap,
                self.canvas.scale_pixmap,
                self.canvas.width(),
                self.canvas.height()
            )
            rel_x = cx - self.canvas.img_offset_x
            rel_y = cy - self.canvas.img_offset_y
            rel_rect = QRect(rel_x, rel_y, cw_rect, ch_rect)
            screen_rect = QRect(cx, cy, cw_rect, ch_rect)
            canvas_rects.append((rel_rect, screen_rect))
        # UI只绘制第一个框
        first_rel, first_screen = canvas_rects[0]
        self.canvas.set_selection_rects(first_rel, first_screen)
        self.edit_region.setText(f"{first_rel.x()},{first_rel.y()},{first_rel.width()},{first_rel.height()}")
        # 保存全部多点rel坐标
        self._multi_watermark_rel = [(r[0].x(), r[0].y(), r[0].width(), r[0].height()) for r in canvas_rects]
        self.log(f"自动检测到 {len(self._multi_watermark_rel)} 处水印")
        self.update_start_button()

    def clear_selection(self):
        self.canvas.clear_selection()
        self.edit_region.clear()
        self._multi_watermark_rel = []
        self.log("已清除选择区域")
        self.update_start_button()

    def update_start_button(self):
        has_img = bool(self.image_path)
        has_region = bool(self.edit_region.text().strip())
        has_out = bool(self.output_path)
        self.btn_start.setEnabled(has_img and has_region and has_out)

    def start_remove_watermark(self):
        import cv2
        import numpy as np
        import os
        if not self.image_path:
            DarkMessageBox.showWarning(self, "提示", "请先加载图片")
            return
        if not self.output_path:
            DarkMessageBox.showWarning(self, "提示", "请选择输出保存路径")
            return
        rel_coords_list = []
        if hasattr(self,"_multi_watermark_rel") and len(self._multi_watermark_rel)>0:
            rel_coords_list = self._multi_watermark_rel
        else:
            region_text = self.edit_region.text().strip()
            if not region_text:
                DarkMessageBox.showWarning(self, "提示", "没有水印区域，请框选或者使用自动检测")
                return
            try:
                rel_x, rel_y, rel_w, rel_h = [int(v.strip()) for v in region_text.split(",")]
                rel_coords_list = [(rel_x, rel_y, rel_w, rel_h)]
            except Exception:
                DarkMessageBox.showWarning(self, "提示", "坐标格式错误")
                return
        self.log(f"待处理水印数量：{len(rel_coords_list)}")
        img = cv2.imdecode(np.fromfile(self.image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            DarkMessageBox.showWarning(self, "错误", "读取图片失败")
            return
        img_h, img_w = img.shape[:2]
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        expand = 3
        for rel_x, rel_y, rel_w, rel_h in rel_coords_list:
            ox, oy, ow, oh = WatermarkDetector.canvas_rect_to_original(
                rel_x, rel_y, rel_w, rel_h,
                self.canvas.original_pixmap,
                self.canvas.scale_pixmap,
                self.canvas.width(),
                self.canvas.height()
            )
            self.log(f"水印原图坐标 ox={ox},oy={oy},ow={ow},oh={oh}")
            if ox <0 or oy <0 or ow <=0 or oh <=0:
                continue
            x1 = max(0, ox-expand)
            y1 = max(0, oy-expand)
            x2 = min(img_w, ox+ow+expand)
            y2 = min(img_h, oy+oh+expand)
            mask[y1:y2, x1:x2] = 255
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        self.progress_bar.setValue(40)
        self.log("开始多点水印修复...")
        repair_radius = 3
        out_img = cv2.inpaint(img, mask, repair_radius, cv2.INPAINT_TELEA)
        self.progress_bar.setValue(85)
        suffix = os.path.splitext(self.output_path)[1]
        ok_buf, buf = cv2.imencode(suffix, out_img)
        if not ok_buf:
            DarkMessageBox.showWarning(self, "错误", "保存失败")
            return
        buf.tofile(self.output_path)
        self.progress_bar.setValue(100)
        self.log(f"✅{len(rel_coords_list)}处水印去除完成，输出：{self.output_path}")
        DarkMessageBox.showInfo(self,"完成","水印处理完毕")
        self._multi_watermark_rel = []
        self.canvas.clear_all()
        self.image_path = ""
        self.output_path = ""
        self.log("处理完毕，界面已重置，可以加载下一张图片")

    def log(self, text):
        self.log_text.append(text)
