import numpy as np


def bgr2rgb(bgr_img: np.ndarray) -> np.ndarray:
    """BGR -> RGB (opencv格式转RGB)"""
    return bgr_img[..., ::-1].copy()


def rgb2bgr(rgb_img: np.ndarray) -> np.ndarray:
    """RGB -> BGR"""
    return rgb_img[..., ::-1].copy()


def canvas_to_original(canvas_rect: tuple, scale_ratio: float) -> tuple:
    """
    画布上鼠标框选坐标 → 原图真实坐标
    canvas_rect: (x,y,w,h) 画布控件坐标
    """
    x, y, w, h = canvas_rect
    ox = x / scale_ratio
    oy = y / scale_ratio
    ow = w / scale_ratio
    oh = h / scale_ratio
    return (int(ox), int(oy), int(ow), int(oh))


def original_to_canvas(original_rect: tuple, scale_ratio: float) -> tuple:
    """原图坐标 → 画布预览坐标"""
    x, y, w, h = original_rect
    cx = x * scale_ratio
    cy = y * scale_ratio
    cw = w * scale_ratio
    ch = h * scale_ratio
    return (int(cx), int(cy), int(cw), int(ch))
