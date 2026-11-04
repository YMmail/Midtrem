"""studio_wall_details.py - สายไฟรอบห้อง + สวิตช์ไฟข้างประตู (PyOpenGL ล้วน)
ใช้: wall_wires(W, D, H)  /  light_switches(D)   (ตำแหน่งตามห้อง 305x355x130 นิ้ว, 1 หน่วย = 1 เมตร)"""
from OpenGL.GL import *
from studio_gfx import box, gquad, ball, cable, SHADE_N

SWITCH_Y = 1.25
SWITCH_WHITE_X = (5.20, 5.32)
SWITCH_CHROME_X = (5.085, 5.185)


def _ring_pts(W, D, H, dy, dxo):
    bm = 0.37 / 2
    Y = H - 0.18 + dy
    yc = 2.65 + dy
    zd, zn, xw, xe = D - 0.015, 0.015, 0.015, W - 0.015
    xl = W / 2 - bm - 0.012 - dxo
    xr = W / 2 + bm + 0.012 + dxo
    return [(xl, Y, zd), (xw, Y, zd), (xw, Y, 0.125), (0.27, Y, 0.125), (0.285, Y, zn),
            (W / 2 - 0.22, Y, zn), (W / 2 - 0.19, Y, 0.125), (W / 2 + 0.19, Y, 0.125), (W / 2 + 0.22, Y, zn),
            (W - 0.285, Y, zn), (W - 0.27, Y, 0.125), (xe, Y, 0.125), (xe, Y, zd), (xr, Y, zd),
            (xr, yc, zd), (xl, yc, zd), (xl, Y, zd)]


def _clip(x, y, z, axis, col=(0.80, 0.80, 0.78)):
    s = 0.012
    if axis == 'x':
        box(x - s, y - 0.020, z - 0.018, x + s, y + 0.020, z + 0.018, col)
    else:
        box(x - 0.018, y - 0.020, z - s, x + 0.018, y + 0.020, z + s, col)


def wall_wires(W, D, H):
    blk, wht, gry = (0.05, 0.05, 0.06), (0.90, 0.90, 0.88), (0.35, 0.36, 0.38)
    bm = 0.37 / 2
    zd, zn, xw, xe = D - 0.015, 0.015, 0.015, W - 0.015
    Y = H - 0.18
    for (dy, dxo, r, col) in ((0.0, 0.0, 0.008, blk), (-0.025, 0.014, 0.006, wht), (0.022, 0.026, 0.005, gry)):
        pts = _ring_pts(W, D, H, dy, dxo)
        cable(pts, r, col)
        ball(pts[0][0], pts[0][1], pts[0][2], r * 1.05, col, 6, 4)
    x = 0.30
    while x < W / 2 - bm - 0.25:
        _clip(x, Y, zd, 'x'); x += 0.55
    x = W / 2 + bm + 0.30
    while x < W - 0.30:
        _clip(x, Y, zd, 'x'); x += 0.55
    for x in (0.9, 1.7, 2.5, 3.2, 4.55, 5.25, 6.05, 6.85):
        _clip(x, Y, zn, 'x')
    z = 0.5
    while z < D - 0.2:
        _clip(xw, Y, z, 'z'); _clip(xe, Y, z, 'z'); z += 0.60
    xs = W - 0.155
    cable([(xs, Y, zd), (xs, 0.50, zd)], 0.007, blk)
    for y in (2.85, 2.30, 1.60, 0.95):
        _clip(xs, y, zd, 'x')
    box(xs - 0.045, 0.40, zd - 0.025, xs + 0.045, 0.54, zd, wht)
    box(xs - 0.030, 0.425, zd - 0.030, xs + 0.030, 0.475, zd - 0.025, (0.30, 0.30, 0.32))
    cable([(2.45, Y, zd), (2.45, 2.88, zd)], 0.007, blk)
    box(2.45 - 0.055, 2.70, zd - 0.035, 2.45 + 0.055, 2.88, zd, wht)
    box(2.45 - 0.040, 2.72, zd - 0.040, 2.45 + 0.040, 2.86, zd - 0.035, (0.82, 0.82, 0.80))
    cable([(xw, Y, 7.55), (xw, 0.60, 7.55)], 0.007, blk)
    box(0.0, 0.50, 7.55 - 0.045, 0.025, 0.60, 7.55 + 0.045, wht)
    box(0.025, 0.52, 7.55 - 0.030, 0.030, 0.58, 7.55 + 0.030, (0.30, 0.30, 0.32))


def light_switches(D):
    z, cy = D, SWITCH_Y
    rocker = (0.93, 0.92, 0.88)
    rocker_lo = tuple(v * SHADE_N * 0.80 for v in rocker)
    line = (0.22, 0.22, 0.23)
    x0, x1 = SWITCH_WHITE_X
    box(x0, cy - 0.039, z - 0.018, x1, cy + 0.039, z, (0.97, 0.97, 0.95))
    pitch = (x1 - x0) / 3
    for i in range(3):
        mx = x0 + pitch * (i + 0.5)
        box(mx - 0.0105, cy - 0.021, z - 0.024, mx + 0.0105, cy + 0.021, z - 0.018, rocker)
        zf = z - 0.0243
        gquad([(mx - 0.0105, cy - 0.021, zf), (mx + 0.0105, cy - 0.021, zf),
               (mx + 0.0105, cy, zf), (mx - 0.0105, cy, zf)], [rocker_lo] * 4)
        gquad([(mx - 0.0105, cy - 0.0008, zf - 0.0001), (mx + 0.0105, cy - 0.0008, zf - 0.0001),
               (mx + 0.0105, cy + 0.0008, zf - 0.0001), (mx - 0.0105, cy + 0.0008, zf - 0.0001)], [line] * 4)
    c0, c1 = SWITCH_CHROME_X
    box(c0, cy - 0.033, z - 0.008, c1, cy + 0.033, z, (0.74, 0.76, 0.79))
    for k in range(2):
        mx = c0 + (c1 - c0) * (0.30 + 0.40 * k)
        gquad([(mx - 0.013, cy - 0.020, z - 0.0083), (mx + 0.013, cy - 0.020, z - 0.0083),
               (mx + 0.013, cy + 0.020, z - 0.0083), (mx - 0.013, cy + 0.020, z - 0.0083)], [(0.07, 0.07, 0.08)] * 4)
        box(mx - 0.009, cy - 0.016, z - 0.015, mx + 0.009, cy + 0.016, z - 0.008, (0.95, 0.95, 0.93))
        zf = z - 0.0153
        gquad([(mx - 0.009, cy - 0.016, zf), (mx + 0.009, cy - 0.016, zf),
               (mx + 0.009, cy, zf), (mx - 0.009, cy, zf)], [rocker_lo] * 4)


def aircon_brackets(cx, H, steel=(0.62, 0.64, 0.67)):
    """ขายึดแอร์ 2 แท่งที่ยึดกับเพดาน (ซ้าย/ขวาของตัวแอร์)"""
    for dx in (-.6, .6):
        box(cx + dx - .01, H - .15, .87, cx + dx + .01, H, .89, steel)
