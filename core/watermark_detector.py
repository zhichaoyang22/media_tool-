# core/watermark_detector.py
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage


class WatermarkDetector:
    """水印检测算法模块，纯计算逻辑，不操作UI组件"""
    def __init__(self, detect_threshold: int = 22):
        self.detect_threshold = detect_threshold

    def calc_watermark_score(self, image: QImage, rect: QRect) -> int:
        total = 0
        light_count = 0
        high_light = 0
        edge_count = 0

        img_w = image.width()
        img_h = image.height()

        top = max(0, rect.top())
        bottom = min(img_h, rect.bottom())
        left = max(0, rect.left())
        right = min(img_w, rect.right())

        if bottom <= top or right <= left:
            return 0

        for y in range(top, bottom):
            for x in range(left, right):
                pixel = image.pixelColor(x, y)
                r = pixel.red()
                g = pixel.green()
                b = pixel.blue()
                brightness = (r + g + b) // 3

                if brightness > 160:
                    light_count += 1
                if brightness > 200:
                    high_light += 1

                if x + 1 < right:
                    px_next = image.pixelColor(x+1, y)
                    br_next = (px_next.red()+px_next.green()+px_next.blue())//3
                    diff = abs(brightness - br_next)
                    if diff > 35:
                        edge_count +=1
                total += 1

        if total == 0:
            return 0

        light_ratio = light_count / total
        hl_ratio = high_light / total
        edge_ratio = edge_count / total

        score = 0
        if 0.02 < light_ratio < 0.80:
            score += 22
        if hl_ratio > 0.01:
            score += 15
        if edge_ratio > 0.03:
            score += 25
        return score

    def scan_corner_regions(self, orig_img: QImage):
        """
        扫描四角 + 多组小窗口，返回所有得分超过阈值的水印候选框列表（支持多处水印）
        """
        orig_w = orig_img.width()
        orig_h = orig_img.height()
        # 原有四角大窗口
        corner_w = int(orig_w * 0.12)
        corner_h = int(orig_h * 0.10)
        regions_orig = [
            QRect(orig_w - corner_w, orig_h - corner_h, corner_w, corner_h),
            QRect(0, orig_h - corner_h, corner_w, corner_h),
            QRect(orig_w - corner_w, 0, corner_w, corner_h),
            QRect(0, 0, corner_w, corner_h),
        ]
        # 新增：右下角多组小窗口，专门抓右下角小字水印
        small_win_sizes = [
            (int(orig_w*0.08), int(orig_h*0.07)),
            (int(orig_w*0.06), int(orig_h*0.05)),
            (int(orig_w*0.10), int(orig_h*0.06)),
        ]
        for sw, sh in small_win_sizes:
            rx = orig_w - sw
            ry = orig_h - sh
            regions_orig.append(QRect(rx, ry, sw, sh))

        candidate_list = []
        for r in regions_orig:
            if r.width() <12 or r.height()<12:
                continue
            sc = self.calc_watermark_score(orig_img, r)
            # 超过阈值就加入候选列表
            if sc >= self.detect_threshold:
                candidate_list.append({"rect": r, "score": sc})
        # 返回全部合格候选，不再只返回1个最优
        return candidate_list

    @staticmethod
    def merge_overlap_rects(rect_list, iou_thresh=0.2):
        """
        矩形合并：合并重叠度iou>阈值的框，消除重复检测
        rect_list: [(x,y,w,h),...]
        return: 合并之后 [(x,y,w,h),...]
        """
        if len(rect_list) == 0:
            return []
        out = []
        used = [False]*len(rect_list)
        for i in range(len(rect_list)):
            if used[i]:
                continue
            x1,y1,w1,h1 = rect_list[i]
            r1 = [x1,y1,x1+w1,y1+h1]
            cxmin,cymin = r1[0],r1[1]
            cxmax,cymax = r1[2],r1[3]
            used[i]=True
            for j in range(i+1, len(rect_list)):
                if used[j]:
                    continue
                x2,y2,w2,h2 = rect_list[j]
                r2 = [x2,y2,x2+w2,y2+h2]
                inter_x1 = max(r1[0], r2[0])
                inter_y1 = max(r1[1], r2[1])
                inter_x2 = min(r1[2], r2[2])
                inter_y2 = min(r1[3], r2[3])
                if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
                    continue
                inter_area = (inter_x2-inter_x1)*(inter_y2-inter_y1)
                area1 = (r1[2]-r1[0])*(r1[3]-r1[1])
                area2 = (r2[2]-r2[0])*(r2[3]-r2[1])
                iou = inter_area / min(area1, area2)
                if iou >= iou_thresh:
                    used[j]=True
                    cxmin = min(cxmin, r2[0])
                    cymin = min(cymin, r2[1])
                    cxmax = max(cxmax, r2[2])
                    cymax = max(cymax, r2[3])
            nw = cxmax - cxmin
            nh = cymax - cymin
            out.append((cxmin, cymin, nw, nh))
        return out


    @staticmethod
    def canvas_rect_to_original(rel_x, rel_y, rel_w, rel_h,
                                orig_pix, scale_pix, canvas_width, canvas_height):
        """
        【入参：预览缩放图的相对坐标rel_x/rel_y，已经剔除img_offset，不要再减偏移】
        缩放预览图坐标 → 原图真实像素坐标 x,y,w,h
        """
        orig_w = orig_pix.width()
        orig_h = orig_pix.height()
        scale_w = scale_pix.width()
        scale_h = scale_pix.height()

        ox = int(rel_x * orig_w / scale_w)
        oy = int(rel_y * orig_h / scale_h)
        ow = int(rel_w * orig_w / scale_w)
        oh = int(rel_h * orig_h / scale_h)
        return (ox, oy, ow, oh)

    @staticmethod
    def original_rect_to_canvas(orig_x, orig_y, orig_w, orig_h,
                                orig_pix, scale_pix, canvas_width, canvas_height):
        """原图像素坐标 → 画布坐标 x,y,w,h"""
        o_w = orig_pix.width()
        o_h = orig_pix.height()
        s_w = scale_pix.width()
        s_h = scale_pix.height()
        off_x = (canvas_width - s_w) // 2
        off_y = (canvas_height - s_h) // 2

        cx = int(orig_x * s_w / o_w) + off_x
        cy = int(orig_y * s_h / o_h) + off_y
        c_rw = int(orig_w * s_w / o_w)
        c_rh = int(orig_h * s_h / o_h)
        return (cx, cy, c_rw, c_rh)
