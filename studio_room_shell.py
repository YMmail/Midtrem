#!/usr/bin/env python3
import math
import sys
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

INCH = 0.0254
W = 305 * INCH
D = 355 * INCH
H = 130 * INCH

EYE_HEIGHT = 1.60
PLAYER_RADIUS = 0.16
WALK_SPEED = 1.5
RUN_SPEED = 3.2
START_POS = (W / 2, 8.4)
START_YAW = 0.0
BEAM_HANG = 0.60

WALL_GREY = (0.53, 0.55, 0.60)
CURTAIN = (0.27, 0.29, 0.35)
STEEL = (0.78, 0.80, 0.82)

COLLIDERS = []

FRONT_WALL_T = 0.12
FZ = D + FRONT_WALL_T
CORR_W = 2.40
ZW = FZ + CORR_W
FRONT_GROUPS = 4
GROUP_W = 2.55
PIER_W = 0.40
CORR_X1 = 8.60
CORR_X0 = CORR_X1 - (1.00 + FRONT_GROUPS * GROUP_W + (FRONT_GROUPS - 1) * PIER_W)
DOOR_OPEN_H = 2.00
DOOR_A, DOOR_B = 2.85, 4.93
FRAME_HALF = 0.025
DOOR_TOP = 2.60
STRIP_Y0, STRIP_Y1 = 2.10, 2.58
STRIP_X = ((0.48, 2.78), (5.22, 7.52))
BASE_X0 = DOOR_B + FRAME_HALF
BASE_L = 3.37
BASE_H = 0.12
BASE_T = 0.02
PANEL_X0 = BASE_X0 + 1.54
PANEL_W = 1.23
RACK_X0 = BASE_X0
RACK_LENS = (1.15, 1.15, 1.15)
RACK_H, RACK_D, RACK_T = 0.49, 0.15, 0.02
RACK_RODS = 7
RACK_ROD_R = 0.0075
RACK_ROD_Y0 = 0.05
RACK_ROD_PITCH = 0.07
SIGN_GAP = 0.15
SIGN_W, SIGN_H = 0.27, 0.24
SIGN_Y1 = STRIP_Y0 - 0.65
SIGN_Y0 = SIGN_Y1 - SIGN_H
SIGN_T = 0.004
SILL_H = 0.83
WIN_H = 1.14
PANES = 6
CLERE_Y0 = SILL_H + WIN_H + 0.62
CLERE_Y1 = H - 0.10
FRAME_DARK = (0.30, 0.32, 0.35)
FRONT_START = (CORR_X1 - 0.40, FZ + 1.00)
FRONT_YAW = -math.pi / 2
WALL_HOLES = [(DOOR_A, DOOR_B, 0.0, DOOR_OPEN_H),
              (DOOR_A, DOOR_B, DOOR_OPEN_H + 0.05, STRIP_Y1)]
WALL_HOLES += [(a, b, STRIP_Y0, STRIP_Y1) for (a, b) in STRIP_X]

DOOR_STATE = [0.0]
DOOR_DIR = [1.0]
DOOR_SENSE = 1.4
DOOR_SPEED = 1.3
DOOR_MAX_ANGLE = 90.0
DOOR_MID = (DOOR_A + DOOR_B) / 2
DOOR_ZC = D + 0.06
DOOR_T = 0.03


SHADE_TOP, SHADE_BOT = 1.00, 0.55
SHADE_N, SHADE_S, SHADE_E, SHADE_W = 0.80, 0.90, 0.93, 0.72
LIGHT_DIR = (0.35, 0.80, 0.45)
LIGHT_N = tuple(v / math.sqrt(sum(c * c for c in LIGHT_DIR)) for v in LIGHT_DIR)


def box(x0, y0, z0, x1, y1, z1, c, solid=False, flat=False):
    if solid:
        COLLIDERS.append((min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)))
    r, g, b = c
    k = (1, 1, 1, 1, 1, 1) if flat else (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)
    glBegin(GL_QUADS)
    glColor3f(r * k[0], g * k[0], b * k[0])
    glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glColor3f(r * k[1], g * k[1], b * k[1])
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    glColor3f(r * k[2], g * k[2], b * k[2])
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x0, y1, z0)
    glColor3f(r * k[3], g * k[3], b * k[3])
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glColor3f(r * k[4], g * k[4], b * k[4])
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    glColor3f(r * k[5], g * k[5], b * k[5])
    glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    glEnd()


def cylinder(cx, y0, cz, r, h, c, seg=18, solid=False):
    if solid:
        COLLIDERS.append((cx - r, cz - r, cx + r, cz + r))
    rr, gg, bb = c
    glBegin(GL_QUADS)
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        s = 0.75 + 0.25 * math.cos(a0 - 0.8)
        glColor3f(rr * s, gg * s, bb * s)
        glVertex3f(cx + r * math.cos(a0), y0, cz + r * math.sin(a0))
        glVertex3f(cx + r * math.cos(a1), y0, cz + r * math.sin(a1))
        glVertex3f(cx + r * math.cos(a1), y0 + h, cz + r * math.sin(a1))
        glVertex3f(cx + r * math.cos(a0), y0 + h, cz + r * math.sin(a0))
    glEnd()
    glColor3f(rr, gg, bb)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx, y0 + h, cz)
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        glVertex3f(cx + r * math.cos(a), y0 + h, cz + r * math.sin(a))
    glEnd()


def tquad(tex, pts, uvs, tint=(1, 1, 1)):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex)
    glColor3f(*tint)
    glBegin(GL_QUADS)
    for p, uv in zip(pts, uvs):
        glTexCoord2f(*uv)
        glVertex3f(*p)
    glEnd()
    glDisable(GL_TEXTURE_2D)


def gquad(pts, cols):
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()


def _xs(a):
    return 0.60 + 0.40 * max(0.0, math.sin(a) * LIGHT_N[1] + math.cos(a) * LIGHT_N[2])


def xcyl(x0, x1, cy, cz, r, col, seg=40):
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        for (x, a) in ((x0, a0), (x1, a0), (x1, a1), (x0, a1)):
            s = _xs(a)
            glColor3f(col[0] * s, col[1] * s, col[2] * s)
            glVertex3f(x, cy + r * math.sin(a), cz + r * math.cos(a))
    glEnd()


GLASS_QUADS = []
WINDOW_GLASS_ALPHA = 0.14
WINDOW_GLASS_TINT = (0.70, 0.86, 0.92)


def glass_quad(pts):
    GLASS_QUADS.append(pts)


def draw_window_glass():
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(WINDOW_GLASS_TINT[0], WINDOW_GLASS_TINT[1], WINDOW_GLASS_TINT[2], WINDOW_GLASS_ALPHA)
    glBegin(GL_QUADS)
    for pts in GLASS_QUADS:
        for p in pts:
            glVertex3f(*p)
    glEnd()
    glDisable(GL_BLEND)
    glDepthMask(GL_TRUE)


def wall_pieces(x0, x1, y0, y1, holes):
    ys = sorted({y0, y1} | {v for h in holes for v in (h[2], h[3])})
    pieces = []
    for ya, yb in zip(ys[:-1], ys[1:]):
        cuts = sorted((h[0], h[1]) for h in holes if h[2] <= ya and h[3] >= yb)
        cur = x0
        for (ca, cb) in cuts:
            if ca > cur:
                pieces.append((cur, ca, ya, yb))
            cur = max(cur, cb)
        if cur < x1:
            pieces.append((cur, x1, ya, yb))
    return pieces


STROKE_H = 119.05


def make_text_tex(text, color=(10, 178, 235), size=110):
    asp = sum(glutStrokeWidth(GLUT_STROKE_ROMAN, ord(ch)) for ch in text) / STROKE_H
    return text, asp, tuple(v / 255.0 for v in color)


def _logo_decal(logo, cx, cy, z, h):
    text, asp, col = logo
    k = h / STROKE_H
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glLineWidth(2.0)
    glColor3f(*col)
    glPushMatrix()
    glTranslatef(cx - h * asp / 2, cy - h * 0.38, z)
    glScalef(k, k, k)
    for ch in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
    glPopMatrix()
    glLineWidth(1.0)
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)
    glDepthMask(GL_TRUE)


def upload_texture(arr):
    h, w, _ = arr.shape
    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, w, h, GL_RGB, GL_UNSIGNED_BYTE, arr.tobytes())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tid


def tex_floor():
    s, n = 512, 8
    rng = np.random.default_rng(1)
    img = np.zeros((s, s, 3))
    pw = s // n
    base = np.array([0.80, 0.74, 0.66])
    for i in range(n):
        j = int(rng.integers(80, 430))
        for ya, yb in ((0, j), (j, s)):
            img[ya:yb, i * pw:(i + 1) * pw] = base * (1 + rng.uniform(-0.06, 0.06))
        img[:, i * pw:i * pw + 2] *= 0.80
        img[j - 1:j + 1, i * pw:(i + 1) * pw] *= 0.80
    img += rng.normal(0, 0.012, (s, s, 1))
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def tex_wall():
    s = 256
    rng = np.random.default_rng(2)
    img = np.ones((s, s, 3)) * np.array(WALL_GREY)
    img += rng.normal(0, 0.01, (s, s, 1))
    img[:, :2] *= 0.78
    img[:2, :] *= 0.78
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def tex_ceiling():
    s = 128
    rng = np.random.default_rng(3)
    img = np.ones((s, s, 3)) * np.array([0.12, 0.12, 0.13])
    img += rng.normal(0, 0.02, (s, s, 1))
    img[:, :3] *= 0.45
    img[:3, :] *= 0.45
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def tex_terrazzo():
    s = 256
    rng = np.random.default_rng(5)
    img = np.ones((s, s, 3)) * np.array([0.80, 0.80, 0.81])
    for _ in range(1500):
        x = int(rng.integers(0, s - 3))
        y = int(rng.integers(0, s - 3))
        w = int(rng.integers(1, 4))
        h = int(rng.integers(1, 4))
        img[y:y + h, x:x + w] = rng.uniform(0.35, 0.95)
    img += rng.normal(0, 0.01, (s, s, 1))
    img[:, :2] = 0.93
    img[:2, :] = 0.93
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def tex_front_wall():
    s = 256
    rng = np.random.default_rng(6)
    img = np.ones((s, s, 3)) * np.array([0.93, 0.94, 0.92])
    img += rng.normal(0, 0.008, (s, s, 1))
    img[:, :2] *= 0.82
    img[:2, :] *= 0.82
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


SIGN_FACE = [None]


def tex_sign():
    w, h = 540, 480
    rng = np.random.default_rng(11)
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    split = 0.445
    wave = 0.90 - 0.03 * np.cos(2 * np.pi * 0.9 * xs)
    g = 0.86 - 0.34 * np.exp(-(ys / 0.20) ** 2) - 0.14 * np.clip((xs - 0.45) / 0.55, 0, 1)
    g = g + 0 * xs
    top = np.stack([g * 0.99, g, g * 1.01], axis=2)
    gb = 0.86 - 0.10 * xs + 0 * ys
    bot = np.stack([gb * 0.97, gb * 0.94, gb * 0.89], axis=2)
    bot += rng.normal(0, 0.008, (h, w, 1))
    t = np.clip((ys - wave) / 0.09, 0, 1)
    gs = 0.95 - 0.50 * t ** 0.8 - 0.12 * xs
    strip = np.stack([gs, gs, gs * 1.01], axis=2)
    img = np.where(ys[..., None] < split, top, np.where(ys[..., None] < wave[..., None], bot, strip))
    img = np.where(np.abs(ys - split)[..., None] < 0.004, 0.50, img)
    img = np.where(np.abs(ys - wave)[..., None] < 0.0035, 0.55, img)
    e = 0.012
    edge = (xs < e) | (xs > 1 - e) | (ys < e) | (ys > 1 - e)
    img = np.where(edge[..., None], 0.46, img)
    img = np.flipud(img)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def room_shell(tex):
    floor, wall, ceil = tex
    t = 1.2
    tquad(floor, [(0, 0, 0), (W, 0, 0), (W, 0, D), (0, 0, D)],
          [(0, 0), (W / t, 0), (W / t, D / t), (0, D / t)])
    tquad(ceil, [(0, H, 0), (W, H, 0), (W, H, D), (0, H, D)],
          [(0, 0), (W / 0.6, 0), (W / 0.6, D / 0.6), (0, D / 0.6)])
    tquad(wall, [(0, 0, 0), (W, 0, 0), (W, H, 0), (0, H, 0)],
          [(0, 0), (W / t, 0), (W / t, H / t), (0, H / t)], (0.95,) * 3)
    for (xa, xb, ya, yb) in wall_pieces(0, W, 0.0, H, WALL_HOLES):
        tquad(wall, [(xa, ya, D), (xb, ya, D), (xb, yb, D), (xa, yb, D)],
              [(xa / t, ya / t), (xb / t, ya / t), (xb / t, yb / t), (xa / t, yb / t)], (1.0,) * 3)
    tquad(wall, [(0, 0, 0), (0, 0, D), (0, H, D), (0, H, 0)],
          [(0, 0), (D / t, 0), (D / t, H / t), (0, H / t)], (0.85,) * 3)
    tquad(wall, [(W, 0, 0), (W, 0, D), (W, H, D), (W, H, 0)],
          [(0, 0), (D / t, 0), (D / t, H / t), (0, H / t)], (0.90,) * 3)
    skirt = (0.42, 0.44, 0.48)
    box(0, 0, 0, W, 0.09, 0.02, skirt)
    box(0, 0, D - 0.02, DOOR_A, 0.09, D, skirt)
    box(DOOR_B, 0, D - 0.02, W, 0.09, D, skirt)
    box(0, 0, 0, 0.02, 0.09, D, skirt)
    box(W - 0.02, 0, 0, W, 0.09, D, skirt)


def ceiling_fixtures():
    bw = 0.37
    box(W / 2 - bw / 2, H - BEAM_HANG, 0, W / 2 + bw / 2, H, D, (0.07, 0.07, 0.08))
    for x in (1.9, 5.85):
        for k in range(5):
            z = 1.0 + k * 1.75
            box(x - 0.10, H - 0.07, z - 0.6, x + 0.10, H, z + 0.6, (0.95, 0.97, 1.0), flat=True)
    for x in (3.0, 4.75):
        for k in range(4):
            cylinder(x, H - 0.16, 1.6 + k * 1.9, 0.05, 0.16, (0.05, 0.05, 0.05), 10)


def sky_glass(x0, x1, y0, y1, z, blind_bottom):
    gquad([(x0, y0, z), (x1, y0, z), (x1, blind_bottom, z), (x0, blind_bottom, z)],
          [(0.58, 0.64, 0.60), (0.58, 0.64, 0.60), (0.80, 0.85, 0.90), (0.80, 0.85, 0.90)])
    gquad([(x0, blind_bottom, z), (x1, blind_bottom, z), (x1, y1, z), (x0, y1, z)],
          [(0.40, 0.41, 0.44)] * 4)


def window_wall():
    sill, top = 0.78, 0.78 + 1.93
    pier = (0.49, 0.51, 0.55)
    secs = [(0.255, 0.255 + 3.42), (W - 0.255 - 3.42, W - 0.255)]
    for (a, b) in secs:
        sky_glass(a, b, sill, top, 0.012, 1.55)
        n = 6
        for i in range(n + 1):
            x = a + (b - a) * i / n
            box(x - 0.02, sill, 0.0, x + 0.02, top, 0.06, (0.30, 0.32, 0.35))
        box(a, top, 0.0, b, top + 0.04, 0.06, (0.30, 0.32, 0.35))
        box(a - 0.02, sill - 0.04, 0.0, b + 0.02, sill, 0.16, (0.86, 0.87, 0.88))
    box(W / 2 - 0.20, 0, 0, W / 2 + 0.20, H, 0.10, pier)
    box(0, 0, 0, 0.255, H, 0.10, pier)
    box(W - 0.255, 0, 0, W, H, 0.10, pier)


def door_wall():
    z = D - 0.02
    fr = (0.90, 0.90, 0.90)
    for (a, b) in ((0.48, 2.78), (5.22, 7.52)):
        for i in range(3):
            x = a + (b - a) * i / 2
            box(x - 0.025, 2.08, z - 0.03, x + 0.025, 2.60, D, (0.28, 0.30, 0.33))
        box(a, 2.08, z - 0.03, b, 2.12, D, (0.28, 0.30, 0.33))
        box(a, 2.56, z - 0.03, b, 2.60, D, (0.28, 0.30, 0.33))
    ga, gb = 2.85, 4.93
    for x in (ga, gb):
        box(x - 0.025, 0, z - 0.04, x + 0.025, 2.60, D, fr)
    for x in (3.32, W / 2, 4.46):
        box(x - 0.025, DOOR_OPEN_H, z - 0.04, x + 0.025, 2.60, D, fr)
    box(ga, DOOR_OPEN_H, z - 0.04, gb, DOOR_OPEN_H + 0.05, D, fr)
    box(ga, 2.56, z - 0.04, gb, 2.60, D, fr)
    box(2.20, 2.0, z - 0.08, 5.58, 2.03, z - 0.05, STEEL)
    for (a, b) in ((2.23, DOOR_A - 0.03), (DOOR_B + 0.03, 5.55)):
        n = 6
        for i in range(n):
            x0 = a + (b - a) * i / n
            x1 = a + (b - a) * (i + 1) / n
            s = 1.0 if i % 2 == 0 else 0.82
            d = 0.10 if i % 2 == 0 else 0.07
            box(x0, 0.03, z - d, x1, 2.0, z - 0.04, tuple(v * s for v in CURTAIN))


def east_wall():
    n = 60
    for i in range(n):
        z0 = D * i / n
        z1 = D * (i + 1) / n
        s = 1.0 if i % 2 == 0 else 0.80
        d = 0.14 if i % 2 == 0 else 0.09
        box(W - d, 0.03, z0, W - 0.02, 2.36, z1, tuple(v * s for v in CURTAIN))
    box(W - 0.12, 2.36, 0, W - 0.02, 2.52, D, (0.30, 0.32, 0.35))
    box(W - 0.05, 2.34, 0, W - 0.02, 2.36, D, STEEL)


def front_shell(ter, fwall):
    L = CORR_X1 - CORR_X0
    tquad(ter, [(CORR_X0, 0, FZ), (CORR_X1, 0, FZ), (CORR_X1, 0, ZW), (CORR_X0, 0, ZW)],
          [(0, 0), (L / 1.2, 0), (L / 1.2, CORR_W / 1.2), (0, CORR_W / 1.2)])
    gquad([(CORR_X0, H, FZ), (CORR_X1, H, FZ), (CORR_X1, H, ZW), (CORR_X0, H, ZW)],
          [(0.90, 0.91, 0.92)] * 4)
    for (xa, xb, ya, yb) in wall_pieces(CORR_X0, CORR_X1, 0.0, H, WALL_HOLES):
        tquad(fwall, [(xa, ya, FZ), (xb, ya, FZ), (xb, yb, FZ), (xa, yb, FZ)],
              [((xa - PANEL_X0) / PANEL_W, ya / 1.2), ((xb - PANEL_X0) / PANEL_W, ya / 1.2),
               ((xb - PANEL_X0) / PANEL_W, yb / 1.2), ((xa - PANEL_X0) / PANEL_W, yb / 1.2)])
    tquad(fwall, [(CORR_X0, 0, ZW), (CORR_X1, 0, ZW), (CORR_X1, H, ZW), (CORR_X0, H, ZW)],
          [(CORR_X0 / 1.2, 0), (CORR_X1 / 1.2, 0), (CORR_X1 / 1.2, H / 1.2), (CORR_X0 / 1.2, H / 1.2)])
    tquad(fwall, [(CORR_X0, 0, FZ), (CORR_X0, 0, ZW), (CORR_X0, H, ZW), (CORR_X0, H, FZ)],
          [(0, 0), (CORR_W / 1.2, 0), (CORR_W / 1.2, H / 1.2), (0, H / 1.2)])
    gquad([(CORR_X1, 0, FZ), (CORR_X1, 0, ZW), (CORR_X1, H, ZW), (CORR_X1, H, FZ)],
          [(0.80, 0.64, 0.42)] * 4)
    box(CORR_X1 - 0.08, 0.0, FZ, CORR_X1, H, FZ + 0.10, (0.35, 0.17, 0.08))


def front_door():
    fr = (0.90, 0.90, 0.90)
    for x in (DOOR_A, DOOR_B):
        box(x - FRAME_HALF, 0.0, FZ, x + FRAME_HALF, DOOR_TOP, FZ + 0.04, fr)
    for x in (3.32, W / 2, 4.46):
        box(x - FRAME_HALF, DOOR_OPEN_H, FZ, x + FRAME_HALF, DOOR_TOP, FZ + 0.04, fr)
    box(DOOR_A, DOOR_OPEN_H, FZ, DOOR_B, DOOR_OPEN_H + 0.05, FZ + 0.04, fr)
    box(DOOR_A, DOOR_TOP - 0.04, FZ, DOOR_B, DOOR_TOP, FZ + 0.04, fr)
    box(DOOR_A, 0.0, D, DOOR_A + FRAME_HALF, DOOR_OPEN_H, FZ, fr)
    box(DOOR_B - FRAME_HALF, 0.0, D, DOOR_B, DOOR_OPEN_H, FZ, fr)
    box(DOOR_A, DOOR_OPEN_H - 0.02, D, DOOR_B, DOOR_OPEN_H, FZ, fr)
    box(DOOR_A, 0.0, D, DOOR_B, 0.015, FZ, (0.55, 0.55, 0.57))


def front_strip_windows():
    for (a, b) in STRIP_X:
        for i in range(3):
            x = a + (b - a) * i / 2
            box(x - 0.025, STRIP_Y0 - 0.02, FZ, x + 0.025, STRIP_Y1 + 0.02, FZ + 0.03, (0.50, 0.52, 0.55))
        box(a, STRIP_Y0 - 0.02, FZ, b, STRIP_Y0 + 0.02, FZ + 0.03, (0.50, 0.52, 0.55))
        box(a, STRIP_Y1 - 0.02, FZ, b, STRIP_Y1 + 0.02, FZ + 0.03, (0.50, 0.52, 0.55))


def wall_glass():
    for (xa, xb, ya, yb) in WALL_HOLES[1:]:
        glass_quad([(xa, ya, D), (xb, ya, D), (xb, yb, D), (xa, yb, D)])
        glass_quad([(xa, ya, FZ), (xb, ya, FZ), (xb, yb, FZ), (xa, yb, FZ)])
        glass_quad([(xa, ya, D), (xa, ya, FZ), (xa, yb, FZ), (xa, yb, D)])
        glass_quad([(xb, ya, D), (xb, ya, FZ), (xb, yb, FZ), (xb, yb, D)])
        glass_quad([(xa, yb, D), (xb, yb, D), (xb, yb, FZ), (xa, yb, FZ)])
        glass_quad([(xa, ya, D), (xb, ya, D), (xb, ya, FZ), (xa, ya, FZ)])


def front_baseboard():
    box(BASE_X0, 0.0, FZ, BASE_X0 + BASE_L, BASE_H, FZ + BASE_T, (0.38, 0.40, 0.42))


def front_shoe_racks():
    wood = (0.76, 0.54, 0.32)
    edge = (0.80, 0.80, 0.42)
    x = RACK_X0
    for L in RACK_LENS:
        xa, xb = x, x + L
        for (px0, px1) in ((xa, xa + RACK_T), (xb - RACK_T, xb)):
            box(px0, 0.0, FZ, px1, RACK_H, FZ + RACK_D, wood)
            box(px0, 0.0, FZ + RACK_D - 0.006, px1, RACK_H, FZ + RACK_D, edge)
        for k in range(RACK_RODS):
            y = RACK_ROD_Y0 + k * RACK_ROD_PITCH
            zc = FZ + 0.03 + 0.10 * (1 - k / (RACK_RODS - 1))
            xcyl(xa + RACK_T, xb - RACK_T, y, zc, RACK_ROD_R, STEEL, 10)
        x = xb


def front_sign(code_tex, name_tex):
    x0 = DOOR_B + FRAME_HALF + SIGN_GAP
    x1 = x0 + SIGN_W
    zs = FZ + SIGN_T
    zf = zs + 0.0004
    box(x0, SIGN_Y0, FZ, x1, SIGN_Y1, zs, (0.50, 0.52, 0.55))
    tquad(SIGN_FACE[0], [(x0, SIGN_Y0, zf), (x1, SIGN_Y0, zf), (x1, SIGN_Y1, zf), (x0, SIGN_Y1, zf)],
          [(0, 0), (1, 0), (1, 1), (0, 1)])
    xm = (x0 + x1) / 2
    _logo_decal(code_tex, xm, SIGN_Y1 - 0.22 * SIGN_H, zf + 0.0006, min(0.046, SIGN_W * 0.78 / code_tex[1]))
    _logo_decal(name_tex, xm, SIGN_Y1 - 0.70 * SIGN_H, zf + 0.0006, min(0.040, SIGN_W * 0.85 / name_tex[1]))


def front_window_wall():
    pier = (0.86, 0.87, 0.88)
    box(CORR_X0, 0.0, ZW - 0.03, CORR_X1, 0.12, ZW, (0.15, 0.16, 0.17))
    for k in range(FRONT_GROUPS):
        xr = CORR_X1 - 0.50 - k * (GROUP_W + PIER_W)
        xl = xr - GROUP_W
        zg = ZW - 0.004
        gquad([(xl, SILL_H, zg), (xr, SILL_H, zg), (xr, SILL_H + WIN_H, zg), (xl, SILL_H + WIN_H, zg)],
              [(0.80, 0.86, 0.90), (0.80, 0.86, 0.90), (0.96, 0.97, 0.98), (0.96, 0.97, 0.98)])
        for i in range(PANES + 1):
            x = xl + GROUP_W * i / PANES
            box(x - 0.02, SILL_H, ZW - 0.06, x + 0.02, SILL_H + WIN_H, ZW, FRAME_DARK)
        box(xl, SILL_H - 0.03, ZW - 0.06, xr, SILL_H + 0.01, ZW, FRAME_DARK)
        box(xl, SILL_H + WIN_H - 0.01, ZW - 0.06, xr, SILL_H + WIN_H + 0.03, ZW, FRAME_DARK)
        box(xl - 0.02, SILL_H - 0.04, ZW - 0.16, xr + 0.02, SILL_H, ZW, pier)
        gquad([(xl, CLERE_Y0, zg), (xr, CLERE_Y0, zg), (xr, CLERE_Y1, zg), (xl, CLERE_Y1, zg)],
              [(0.70, 0.76, 0.80)] * 4)
        for i in range(PANES + 1):
            x = xl + GROUP_W * i / PANES
            box(x - 0.015, CLERE_Y0, ZW - 0.05, x + 0.015, CLERE_Y1, ZW, FRAME_DARK)
        box(xl, CLERE_Y0 - 0.02, ZW - 0.05, xr, CLERE_Y0 + 0.02, ZW, FRAME_DARK)
        box(xl, CLERE_Y1 - 0.02, ZW - 0.05, xr, CLERE_Y1 + 0.02, ZW, FRAME_DARK)


def front_corridor(ter, fwall, sign_code, sign_name):
    front_shell(ter, fwall)
    front_door()
    front_strip_windows()
    wall_glass()
    front_baseboard()
    front_shoe_racks()
    front_sign(sign_code, sign_name)
    front_window_wall()
    COLLIDERS.append((RACK_X0, FZ, RACK_X0 + sum(RACK_LENS), FZ + RACK_D))


def update_door(cam, dt):
    near = math.hypot(cam.x - DOOR_MID, cam.z - DOOR_ZC) < DOOR_SENSE
    cur = DOOR_STATE[0]
    if near and cur <= 0.0:
        DOOR_DIR[0] = 1.0 if cam.z < DOOR_ZC else -1.0
    target = 1.0 if near else 0.0
    step = DOOR_SPEED * dt
    if cur < target:
        cur = min(target, cur + step)
    elif cur > target:
        cur = max(target, cur - step)
    DOOR_STATE[0] = cur


def draw_auto_door():
    o = DOOR_STATE[0]
    o = o * o * (3 - 2 * o)
    theta = DOOR_MAX_ANGLE * o * DOOR_DIR[0]
    leaf = (DOOR_B - DOOR_A) / 2 - FRAME_HALF
    fr = (0.90, 0.90, 0.90)
    hz = DOOR_T / 2
    h_top = DOOR_OPEN_H - 0.05
    glass = []
    for side in (-1, 1):
        hinge_x = DOOR_A + FRAME_HALF if side < 0 else DOOR_B - FRAME_HALF
        ang = -theta if side < 0 else theta
        d = 1.0 if side < 0 else -1.0
        glPushMatrix()
        glTranslatef(hinge_x, 0.0, DOOR_ZC)
        glRotatef(ang, 0, 1, 0)
        def seg(x0, x1, y0, y1, col):
            xa, xb = sorted((d * x0, d * x1))
            box(xa, y0, -hz, xb, y1, hz, col)
        seg(0.0, 0.04, 0.0, h_top, fr)
        seg(leaf - 0.04, leaf, 0.0, h_top, fr)
        seg(0.0, leaf, 0.0, 0.06, fr)
        seg(0.0, leaf, DOOR_OPEN_H - 0.09, h_top, fr)
        xa, xb = sorted((d * (leaf - 0.09), d * (leaf - 0.07)))
        box(xa, 0.90, hz, xb, 1.20, hz + 0.02, STEEL)
        box(xa, 0.90, -hz - 0.02, xb, 1.20, -hz, STEEL)
        glass.append((hinge_x, ang, d, leaf))
        glPopMatrix()
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.45, 0.62, 0.70, 0.30)
    for (hinge_x, ang, d, leaf) in glass:
        glPushMatrix()
        glTranslatef(hinge_x, 0.0, DOOR_ZC)
        glRotatef(ang, 0, 1, 0)
        x0, x1 = sorted((d * 0.04, d * (leaf - 0.04)))
        glBegin(GL_QUADS)
        glVertex3f(x0, 0.06, 0); glVertex3f(x1, 0.06, 0)
        glVertex3f(x1, DOOR_OPEN_H - 0.09, 0); glVertex3f(x0, DOOR_OPEN_H - 0.09, 0)
        glEnd()
        glPopMatrix()
    glDisable(GL_BLEND)
    glDepthMask(GL_TRUE)


def build_scene():
    COLLIDERS.clear()
    GLASS_QUADS.clear()
    tex = (upload_texture(tex_floor()), upload_texture(tex_wall()), upload_texture(tex_ceiling()))
    ter_tex = upload_texture(tex_terrazzo())
    fwall_tex = upload_texture(tex_front_wall())
    SIGN_FACE[0] = upload_texture(tex_sign())
    sign_code = make_text_tex("CB 30609", (26, 27, 30))
    sign_name = make_text_tex("Photo Studio", (250, 250, 252))
    lst = glGenLists(1)
    glNewList(lst, GL_COMPILE)
    room_shell(tex)
    ceiling_fixtures()
    window_wall()
    door_wall()
    east_wall()
    front_corridor(ter_tex, fwall_tex, sign_code, sign_name)
    draw_window_glass()
    glEndList()
    return lst


class Camera:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.z = START_POS
        self.y = EYE_HEIGHT
        self.yaw = START_YAW
        self.pitch = 0.0

    def forward(self):
        return math.sin(self.yaw), -math.cos(self.yaw)

    def right(self):
        return math.cos(self.yaw), math.sin(self.yaw)

    def look(self):
        cp = math.cos(self.pitch)
        fx, fz = self.forward()
        gluLookAt(self.x, self.y, self.z,
                  self.x + fx * cp, self.y + math.sin(self.pitch), self.z + fz * cp,
                  0, 1, 0)


def door_leaf_segments():
    o = DOOR_STATE[0]
    o = o * o * (3 - 2 * o)
    theta = DOOR_MAX_ANGLE * o * DOOR_DIR[0]
    leaf = (DOOR_B - DOOR_A) / 2 - FRAME_HALF
    segs = []
    for side in (-1, 1):
        hx = DOOR_A + FRAME_HALF if side < 0 else DOOR_B - FRAME_HALF
        ang = math.radians(-theta if side < 0 else theta)
        d = 1.0 if side < 0 else -1.0
        segs.append((hx, DOOR_ZC, hx + d * leaf * math.cos(ang), DOOR_ZC - d * leaf * math.sin(ang)))
    return segs


def door_clearance(x, z):
    best = 1e9
    for (ax, az, bx, bz) in door_leaf_segments():
        dx, dz = bx - ax, bz - az
        t = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(x - (ax + t * dx), z - (az + t * dz)))
    return best - (PLAYER_RADIUS + DOOR_T / 2)


def blocked(x, z):
    r = PLAYER_RADIUS
    if door_clearance(x, z) < 0:
        return True
    if z > D - r:
        if z < FZ + r:
            if x < DOOR_A + FRAME_HALF + r or x > DOOR_B - FRAME_HALF - r:
                return True
        if z > D and (x < CORR_X0 + r or x > CORR_X1 - r or z > ZW - r):
            return True
    elif x < r or x > W - r or z < r:
        return True
    for (x0, z0, x1, z1) in COLLIDERS:
        if x0 - r < x < x1 + r and z0 - r < z < z1 + r:
            return True
    return False


def move(cam, dx, dz):
    nx = cam.x + dx
    if not blocked(nx, cam.z) or (door_clearance(cam.x, cam.z) < 0 and door_clearance(nx, cam.z) >= door_clearance(cam.x, cam.z)):
        cam.x = nx
    nz = cam.z + dz
    if not blocked(cam.x, nz) or (door_clearance(cam.x, cam.z) < 0 and door_clearance(cam.x, nz) >= door_clearance(cam.x, cam.z)):
        cam.z = nz


class Overlay:
    """HUD ข้อความด้วย GLUT bitmap"""
    def __init__(self):
        self.lines = []

    def update(self, lines):
        self.lines = list(lines)

    def draw(self, sw, sh):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, sw, sh, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        w = 12 + 7 * max([len(t) for t in self.lines] + [1])
        h = 12 + 16 * len(self.lines)
        glColor4f(0, 0, 0, 0.55)
        glBegin(GL_QUADS)
        glVertex2f(10, 10); glVertex2f(10 + w, 10); glVertex2f(10 + w, 10 + h); glVertex2f(10, 10 + h)
        glEnd()
        glColor3f(1, 1, 1)
        for i, t in enumerate(self.lines):
            glRasterPos2f(18, 28 + 16 * i)
            for ch in t:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


FOV = 70.0
SW, SH = 1280, 720
SHIFT_KEYS = (112, 113)          # freeglut: GLUT_KEY_SHIFT_L / R
APP = {}


def setup_gl(sw, sh):
    glViewport(0, 0, sw, max(sh, 1))
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.06, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, sw / max(sh, 1), 0.03, 60)
    glMatrixMode(GL_MODELVIEW)


def render(cam, scene):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    cam.look()
    glCallList(scene)
    draw_auto_door()


def _update():
    a = APP
    now = glutGet(GLUT_ELAPSED_TIME)
    dt = min((now - a["last"]) / 1000.0, 0.05)
    a["last"] = now
    cam, keys, arrows = a["cam"], a["keys"], a["arrows"]
    if GLUT_KEY_LEFT in arrows: cam.yaw -= 1.8 * dt
    if GLUT_KEY_RIGHT in arrows: cam.yaw += 1.8 * dt
    if GLUT_KEY_UP in arrows: cam.pitch += 1.2 * dt
    if GLUT_KEY_DOWN in arrows: cam.pitch -= 1.2 * dt
    cam.pitch = max(-math.radians(85), min(math.radians(85), cam.pitch))
    fx, fz = cam.forward()
    rx, rz = cam.right()
    vx = vz = 0.0
    if b'w' in keys: vx += fx; vz += fz
    if b's' in keys: vx -= fx; vz -= fz
    if b'd' in keys: vx += rx; vz += rz
    if b'a' in keys: vx -= rx; vz -= rz
    n = math.hypot(vx, vz)
    if n > 0:
        speed = RUN_SPEED if a["shift"] else WALK_SPEED
        move(cam, vx / n * speed * dt, vz / n * speed * dt)
    update_door(cam, dt)
    glutPostRedisplay()


def _display():
    a = APP
    cam = a["cam"]
    render(cam, a["scene"])
    a["overlay"].update(["x=%.2f  z=%.2f  (m)" % (cam.x, cam.z),
                         "WASD walk | Shift run | Mouse/Arrows look | R reset | F room/corridor | Esc quit"])
    a["overlay"].draw(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    glutSwapBuffers()


def _reshape(w, h):
    setup_gl(w, h)


def _mods():
    try:
        APP["shift"] = bool(glutGetModifiers() & GLUT_ACTIVE_SHIFT)
    except Exception:
        pass


def _key_down(k, x, y):
    _mods()
    cam = APP["cam"]
    if k == b'\x1b':
        glutSetCursor(GLUT_CURSOR_INHERIT)
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
        return
    kl = k.lower()
    if kl == b'r':
        cam.reset()
    elif kl == b'f':
        if cam.z > D:
            cam.reset()
        else:
            cam.x, cam.z = FRONT_START
            cam.yaw = FRONT_YAW
            cam.pitch = 0.0
    else:
        APP["keys"].add(kl)


def _key_up(k, x, y):
    _mods()
    APP["keys"].discard(k.lower())


def _special_down(k, x, y):
    if k in SHIFT_KEYS:
        APP["shift"] = True
    else:
        _mods()
        APP["arrows"].add(k)


def _special_up(k, x, y):
    if k in SHIFT_KEYS:
        APP["shift"] = False
    else:
        _mods()
        APP["arrows"].discard(k)


def _mouse_move(x, y):
    _mods()
    cx, cy = glutGet(GLUT_WINDOW_WIDTH) // 2, glutGet(GLUT_WINDOW_HEIGHT) // 2
    if APP["warp"]:
        APP["warp"] = False
        return
    dx, dy = x - cx, y - cy
    if dx == 0 and dy == 0:
        return
    cam = APP["cam"]
    cam.yaw += math.radians(dx * 0.12)
    cam.pitch = max(-math.radians(85), min(math.radians(85), cam.pitch - math.radians(dy * 0.12)))
    APP["warp"] = True
    glutWarpPointer(cx, cy)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SW, SH)
    glutCreateWindow(b"Studio Room Shell  (1 unit = 1 m)")
    setup_gl(SW, SH)
    APP.update(scene=build_scene(), overlay=Overlay(), cam=Camera(), keys=set(), arrows=set(),
               shift=False, warp=False, last=glutGet(GLUT_ELAPSED_TIME))
    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(_display)
    glutReshapeFunc(_reshape)
    glutIdleFunc(_update)
    glutKeyboardFunc(_key_down)
    glutKeyboardUpFunc(_key_up)
    glutSpecialFunc(_special_down)
    glutSpecialUpFunc(_special_up)
    glutPassiveMotionFunc(_mouse_move)
    glutMotionFunc(_mouse_move)
    glutIgnoreKeyRepeat(1)
    glutMainLoop()


if __name__ == "__main__":
    main()
