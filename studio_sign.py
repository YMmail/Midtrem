import math
import numpy as np
from OpenGL.GL import (
    GL_QUADS, GL_TRIANGLE_FAN, GL_TEXTURE_2D, GL_UNPACK_ALIGNMENT, GL_RGB, GL_UNSIGNED_BYTE,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR,
    glBegin, glEnd, glColor3f, glVertex3f, glTexCoord2f, glEnable, glDisable,
    glGenTextures, glBindTexture, glPixelStorei, glTexParameteri,
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef,
)
from OpenGL.GLU import gluBuild2DMipmaps

__all__ = ["SIGN_W", "SIGN_H", "SIGN_T", "prepare_sign", "room_sign", "draw_text", "text_width"]

SIGN_W, SIGN_H = 0.27, 0.24
SIGN_T = 0.004
BODY = (0.50, 0.52, 0.55)
CODE_COLOR = (0.10, 0.105, 0.12)
NAME_COLOR = (0.98, 0.98, 0.99)

SHADE_TOP, SHADE_BOT = 1.00, 0.55
SHADE_N, SHADE_S, SHADE_E, SHADE_W = 0.80, 0.90, 0.93, 0.72


def _box(x0, y0, z0, x1, y1, z1, c):
    r, g, b = c
    k = (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)
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


def _upload(arr):
    h, w, _ = arr.shape
    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, w, h, GL_RGB, GL_UNSIGNED_BYTE, arr.tobytes())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tid


def _face_image():
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


FONT_STROKE = 0.19
FONT_GAP = 0.13
FONT_SPACE = 0.34


def _L(*pts):
    return [tuple(p) for p in pts]


def _A(cx, cy, rx, ry, a0, a1, n=None):
    if n is None:
        n = max(4, int(abs(a1 - a0) / 9))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _P(*parts):
    out = []
    for part in parts:
        for p in part:
            if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
                out.append(p)
    return out


_P_BOWL = _P(_L((0.08, 0), (0.08, 1), (0.35, 1)), _A(0.35, 0.73, 0.25, 0.27, 90, -90), _L((0.35, 0.46), (0.08, 0.46)))

GLYPHS = {
    "0": [_A(0.31, 0.5, 0.28, 0.5, 0, 360, 40)],
    "1": [_L((0.06, 0.8), (0.3, 1.0), (0.3, 0))],
    "2": [_P(_A(0.3, 0.72, 0.26, 0.28, 165, -35), _L((0.03, 0), (0.6, 0)))],
    "3": [_A(0.3, 0.76, 0.25, 0.24, 155, -90), _A(0.3, 0.26, 0.28, 0.26, 90, -155)],
    "4": [_L((0.45, 0), (0.45, 1.0), (0.02, 0.3), (0.62, 0.3))],
    "5": [_L((0.56, 1), (0.12, 1), (0.08, 0.56)), _A(0.31, 0.33, 0.28, 0.33, 140, -150)],
    "6": [_A(0.31, 0.33, 0.28, 0.33, 0, 360, 40), _A(0.47, 0.42, 0.44, 0.58, 72, 182)],
    "7": [_L((0.03, 1), (0.6, 1), (0.2, 0))],
    "8": [_A(0.31, 0.76, 0.24, 0.24, 0, 360, 36), _A(0.31, 0.26, 0.28, 0.26, 0, 360, 36)],
    "9": [_A(0.31, 0.67, 0.28, 0.33, 0, 360, 40), _A(0.15, 0.58, 0.44, 0.58, -108, 2)],
    "A": [_L((0.0, 0), (0.34, 1), (0.68, 0)), _L((0.13, 0.32), (0.55, 0.32))],
    "B": [_P(_L((0.38, 0.52), (0.08, 0.52), (0.08, 1), (0.36, 1)), _A(0.36, 0.76, 0.24, 0.24, 90, -90)),
          _P(_L((0.08, 0.52), (0.08, 0), (0.38, 0)), _A(0.38, 0.26, 0.26, 0.26, -90, 90), _L((0.38, 0.52), (0.08, 0.52)))],
    "C": [_A(0.4, 0.5, 0.38, 0.5, 42, 318)],
    "D": [_P(_L((0.08, 0), (0.08, 1), (0.3, 1)), _A(0.3, 0.5, 0.36, 0.5, 90, -90), _L((0.3, 0), (0.08, 0)))],
    "E": [_L((0.58, 1), (0.08, 1), (0.08, 0), (0.58, 0)), _L((0.08, 0.52), (0.5, 0.52))],
    "F": [_L((0.58, 1), (0.08, 1), (0.08, 0)), _L((0.08, 0.52), (0.5, 0.52))],
    "G": [_P(_A(0.4, 0.5, 0.38, 0.5, 42, 340), _L((0.76, 0.44), (0.46, 0.44)))],
    "H": [_L((0.08, 0), (0.08, 1)), _L((0.62, 0), (0.62, 1)), _L((0.08, 0.52), (0.62, 0.52))],
    "I": [_L((0.08, 0), (0.08, 1))],
    "J": [_P(_L((0.46, 1), (0.46, 0.3)), _A(0.25, 0.3, 0.21, 0.3, 0, -170))],
    "K": [_L((0.08, 0), (0.08, 1)), _L((0.6, 1), (0.08, 0.4)), _L((0.26, 0.6), (0.62, 0))],
    "L": [_L((0.08, 1), (0.08, 0), (0.54, 0))],
    "M": [_L((0.08, 0), (0.08, 1), (0.41, 0.28), (0.74, 1), (0.74, 0))],
    "N": [_L((0.08, 0), (0.08, 1), (0.62, 0), (0.62, 1))],
    "O": [_A(0.42, 0.5, 0.38, 0.5, 0, 360, 44)],
    "P": [_P_BOWL],
    "Q": [_A(0.42, 0.5, 0.38, 0.5, 0, 360, 44), _L((0.5, 0.24), (0.82, -0.06))],
    "R": [_P_BOWL, _L((0.32, 0.46), (0.62, 0))],
    "S": [_A(0.31, 0.75, 0.25, 0.25, 25, 270), _A(0.31, 0.26, 0.28, 0.26, 90, -155)],
    "T": [_L((0.0, 1), (0.62, 1)), _L((0.31, 1), (0.31, 0))],
    "U": [_P(_L((0.08, 1), (0.08, 0.34)), _A(0.35, 0.34, 0.27, 0.34, 180, 360), _L((0.62, 0.34), (0.62, 1)))],
    "V": [_L((0.0, 1), (0.33, 0), (0.66, 1))],
    "W": [_L((0.0, 1), (0.2, 0), (0.43, 0.74), (0.66, 0), (0.86, 1))],
    "X": [_L((0.02, 1), (0.62, 0)), _L((0.62, 1), (0.02, 0))],
    "Y": [_L((0.0, 1), (0.32, 0.5), (0.64, 1)), _L((0.32, 0.5), (0.32, 0))],
    "Z": [_L((0.04, 1), (0.6, 1), (0.04, 0), (0.62, 0))],
    "a": [_A(0.29, 0.34, 0.26, 0.34, 0, 360, 36), _L((0.56, 0.68), (0.56, 0))],
    "b": [_L((0.08, 1), (0.08, 0)), _A(0.35, 0.34, 0.27, 0.34, 0, 360, 36)],
    "c": [_A(0.32, 0.34, 0.29, 0.34, 40, 320)],
    "d": [_A(0.29, 0.34, 0.26, 0.34, 0, 360, 36), _L((0.56, 1), (0.56, 0))],
    "e": [_P(_L((0.05, 0.36), (0.6, 0.36)), _A(0.32, 0.34, 0.28, 0.34, 5, 320))],
    "f": [_P(_A(0.42, 0.84, 0.18, 0.16, 20, 180), _L((0.24, 0.84), (0.24, 0))), _L((0.04, 0.66), (0.46, 0.66))],
    "g": [_A(0.29, 0.36, 0.26, 0.32, 0, 360, 36), _P(_L((0.56, 0.68), (0.56, -0.04)), _A(0.3, -0.04, 0.26, 0.22, 0, -165))],
    "h": [_L((0.08, 1), (0.08, 0)), _P(_A(0.32, 0.42, 0.24, 0.26, 175, 0), _L((0.56, 0.42), (0.56, 0)))],
    "i": [_L((0.08, 0), (0.08, 0.68)), _L((0.08, 0.9), (0.08, 0.91))],
    "j": [_P(_L((0.2, 0.68), (0.2, -0.08)), _A(0.02, -0.08, 0.18, 0.18, 0, -110)), _L((0.2, 0.9), (0.2, 0.91))],
    "k": [_L((0.08, 1), (0.08, 0)), _L((0.52, 0.68), (0.08, 0.24)), _L((0.24, 0.4), (0.54, 0))],
    "l": [_L((0.08, 1), (0.08, 0))],
    "m": [_L((0.08, 0), (0.08, 0.68)), _P(_A(0.25, 0.44, 0.17, 0.24, 175, 0), _L((0.42, 0.44), (0.42, 0))),
          _P(_A(0.59, 0.44, 0.17, 0.24, 175, 0), _L((0.76, 0.44), (0.76, 0)))],
    "n": [_L((0.08, 0), (0.08, 0.68)), _P(_A(0.32, 0.42, 0.24, 0.26, 175, 0), _L((0.56, 0.42), (0.56, 0)))],
    "o": [_A(0.32, 0.34, 0.28, 0.34, 0, 360, 36)],
    "p": [_L((0.08, 0.68), (0.08, -0.3)), _A(0.35, 0.34, 0.27, 0.34, 0, 360, 36)],
    "q": [_A(0.29, 0.34, 0.26, 0.34, 0, 360, 36), _L((0.56, 0.68), (0.56, -0.3))],
    "r": [_L((0.08, 0), (0.08, 0.68)), _A(0.32, 0.42, 0.24, 0.24, 172, 62)],
    "s": [_A(0.28, 0.52, 0.21, 0.16, 30, 270), _A(0.28, 0.18, 0.23, 0.18, 90, -150)],
    "t": [_P(_L((0.22, 0.92), (0.22, 0.16)), _A(0.38, 0.16, 0.16, 0.16, 180, 290)), _L((0.03, 0.66), (0.44, 0.66))],
    "u": [_P(_L((0.08, 0.68), (0.08, 0.26)), _A(0.32, 0.26, 0.24, 0.26, 180, 360)), _L((0.56, 0.68), (0.56, 0))],
    "v": [_L((0.0, 0.68), (0.29, 0), (0.58, 0.68))],
    "w": [_L((0.0, 0.68), (0.17, 0), (0.37, 0.54), (0.57, 0), (0.74, 0.68))],
    "x": [_L((0.03, 0.68), (0.54, 0)), _L((0.54, 0.68), (0.03, 0))],
    "y": [_L((0.0, 0.68), (0.29, 0)), _L((0.58, 0.68), (0.2, -0.3))],
    "z": [_L((0.04, 0.68), (0.52, 0.68), (0.04, 0), (0.54, 0))],
    "-": [_L((0.06, 0.4), (0.42, 0.4))],
    ".": [_L((0.08, 0.0), (0.08, 0.01))],
    ":": [_L((0.08, 0.0), (0.08, 0.01)), _L((0.08, 0.58), (0.08, 0.59))],
    "/": [_L((0.0, -0.05), (0.42, 1.05))],
}


def _advance(ch):
    if ch not in GLYPHS:
        return FONT_SPACE
    return max(p[0] for path in GLYPHS[ch] for p in path) + FONT_STROKE / 2 + FONT_GAP


def text_width(text):
    return sum(_advance(c) for c in text) - FONT_GAP


def _stroke_quads(path, t):
    h = t / 2
    n = len(path)
    if n < 2:
        return [], [path[0]]
    closed = abs(path[0][0] - path[-1][0]) < 1e-6 and abs(path[0][1] - path[-1][1]) < 1e-6
    dirs = []
    for i in range(n - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        ln = math.hypot(dx, dy) or 1.0
        dirs.append((dx / ln, dy / ln))
    left, right, joints = [], [], []
    for i in range(n):
        if i == 0 and not closed:
            d0 = d1 = dirs[0]
        elif i == n - 1 and not closed:
            d0 = d1 = dirs[-1]
        else:
            d0 = dirs[i - 1] if i > 0 else dirs[-1]
            d1 = dirs[i] if i < n - 1 else dirs[0]
        mx, my = -(d0[1] + d1[1]), d0[0] + d1[0]
        ml = math.hypot(mx, my)
        if ml < 1e-6:
            mx, my, scale = -d0[1], d0[0], h
        else:
            mx, my = mx / ml, my / ml
            cos_half = mx * -d0[1] + my * d0[0]
            scale = h / max(cos_half, 0.5)
            if cos_half < 0.97:
                joints.append(path[i])
        left.append((path[i][0] + mx * scale, path[i][1] + my * scale))
        right.append((path[i][0] - mx * scale, path[i][1] - my * scale))
    quads = [(left[i], left[i + 1], right[i + 1], right[i]) for i in range(n - 1)]
    if not closed:
        joints += [path[0], path[-1]]
    return quads, joints


def _split_sharp(path):
    if len(path) < 3:
        return [path]
    parts, cur = [], [path[0]]
    for i in range(1, len(path) - 1):
        cur.append(path[i])
        ax, ay = path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]
        bx, by = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        if la > 0 and lb > 0 and (ax * bx + ay * by) / (la * lb) < 0.8:
            parts.append(cur)
            cur = [path[i]]
    cur.append(path[-1])
    parts.append(cur)
    return parts


def text_polys(text, cap):
    t = FONT_STROKE
    quads, discs = [], []
    x = 0.0
    for ch in text:
        for path in GLYPHS.get(ch, []):
            moved = [(x + px, py) for px, py in path]
            for part in _split_sharp(moved):
                q, j = _stroke_quads(part, t)
                quads += q
                discs += j
        x += _advance(ch)
    return quads, discs, t / 2


def draw_text(text, cx, cy, z, cap, color, max_w=None):
    w = text_width(text)
    sc = cap
    if max_w is not None and w * sc > max_w:
        sc = max_w / w
    ox, oy = cx - w * sc / 2, cy - 0.5 * sc
    quads, discs, r = text_polys(text, cap)
    glColor3f(*color)
    glBegin(GL_QUADS)
    for q in quads:
        for px, py in q:
            glVertex3f(ox + px * sc, oy + py * sc, z)
    glEnd()
    for px, py in discs:
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(ox + px * sc, oy + py * sc, z)
        for k in range(13):
            a = 2 * math.pi * k / 12
            glVertex3f(ox + (px + r * math.cos(a)) * sc, oy + (py + r * math.sin(a)) * sc, z)
        glEnd()


def prepare_sign(code="CB 30609", name="Photo Studio"):
    return {"face": _upload(_face_image()), "code": code, "name": name}


def room_sign(x, y, z, textures, yaw=0.0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(yaw, 0, 1, 0)
    x0, x1 = -SIGN_W / 2, SIGN_W / 2
    y0, y1 = y, y + SIGN_H
    zf = SIGN_T + 0.0004
    _box(x0, y0, 0.0, x1, y1, SIGN_T, BODY)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures["face"])
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(x0, y0, zf)
    glTexCoord2f(1, 0); glVertex3f(x1, y0, zf)
    glTexCoord2f(1, 1); glVertex3f(x1, y1, zf)
    glTexCoord2f(0, 1); glVertex3f(x0, y1, zf)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    draw_text(textures["code"], 0.0, y1 - 0.22 * SIGN_H, zf + 0.0008, 0.040, CODE_COLOR, SIGN_W * 0.78)
    draw_text(textures["name"], 0.0, y1 - 0.70 * SIGN_H, zf + 0.0008, 0.030, NAME_COLOR, SIGN_W * 0.85)
    glPopMatrix()


def _preview():
    import os
    import sys
    import time
    from OpenGL.GL import (
        glViewport, glEnable, glClearColor, glMatrixMode, glLoadIdentity, glClear,
        glGenLists, glNewList, glEndList, glCallList,
        GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW, GL_COMPILE,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    )
    from OpenGL.GLU import gluPerspective, gluLookAt
    from OpenGL.GLUT import (
        glutInit, glutInitDisplayMode, glutInitWindowSize, glutCreateWindow,
        glutGetModifiers, glutWarpPointer, glutPostRedisplay, glutSwapBuffers,
        glutIgnoreKeyRepeat, glutSetCursor, glutKeyboardFunc, glutKeyboardUpFunc,
        glutSpecialFunc, glutSpecialUpFunc, glutPassiveMotionFunc, glutMotionFunc,
        glutReshapeFunc, glutDisplayFunc, glutIdleFunc, glutMainLoop,
        GLUT_DOUBLE, GLUT_RGBA, GLUT_DEPTH, GLUT_ACTIVE_SHIFT, GLUT_CURSOR_NONE,
        GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_KEY_DOWN,
    )

    SW, SH = 1280, 720
    EYE = 1.60
    SHIFT_KEYS = (112, 113)
    WALK, RUN = 0.6, 1.5
    START = [0.0, 0.9, 0.0, -0.29]
    BG = (0.35, 0.36, 0.38, 1)

    def blocked(px, pz):
        return pz < 0.05

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(SW, SH)
    glutCreateWindow(b"Studio Sign  (1 unit = 1 m)")

    def setup(w, h):
        glViewport(0, 0, w, h)
        glEnable(GL_DEPTH_TEST)
        glClearColor(*BG)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70.0, w / max(h, 1), 0.03, 60)
        glMatrixMode(GL_MODELVIEW)

    setup(SW, SH)
    scene = glGenLists(1)
    textures = prepare_sign()
    glNewList(scene, GL_COMPILE)
    room_sign(0.0, 1.21, 0.0, textures)
    glEndList()

    cam = list(START)
    st = {"keys": set(), "special": set(), "shift": False, "mdx": 0, "mdy": 0,
          "w": SW, "h": SH, "last": time.perf_counter()}

    def name(k):
        return (k.decode("latin-1") if isinstance(k, bytes) else str(k)).lower()

    def key_down(k, x, y):
        st["shift"] = bool(glutGetModifiers() & GLUT_ACTIVE_SHIFT)
        ch = name(k)
        if ch == "\x1b":
            os._exit(0)
        if ch == "r":
            cam[:] = START
        st["keys"].add(ch)

    def key_up(k, x, y):
        st["shift"] = bool(glutGetModifiers() & GLUT_ACTIVE_SHIFT)
        st["keys"].discard(name(k))

    def special_down(k, x, y):
        st["special"].add(k)
        if k in SHIFT_KEYS:
            st["shift"] = True

    def special_up(k, x, y):
        st["special"].discard(k)
        if k in SHIFT_KEYS:
            st["shift"] = False

    def mouse_move(x, y):
        cx, cy = st["w"] // 2, st["h"] // 2
        if x != cx or y != cy:
            st["mdx"] += x - cx
            st["mdy"] += y - cy
            glutWarpPointer(cx, cy)

    def reshape(w, h):
        st["w"], st["h"] = w, max(h, 1)
        setup(w, st["h"])

    def update():
        now = time.perf_counter()
        dt = min(now - st["last"], 0.05)
        st["last"] = now
        cam[2] += math.radians(st["mdx"] * 0.12)
        cam[3] -= math.radians(st["mdy"] * 0.12)
        st["mdx"] = st["mdy"] = 0
        sp, keys = st["special"], st["keys"]
        cam[2] += ((GLUT_KEY_RIGHT in sp) - (GLUT_KEY_LEFT in sp)) * 1.8 * dt
        cam[3] += ((GLUT_KEY_UP in sp) - (GLUT_KEY_DOWN in sp)) * 1.2 * dt
        cam[3] = max(-math.radians(85), min(math.radians(85), cam[3]))
        fx, fz = math.sin(cam[2]), -math.cos(cam[2])
        rx, rz = math.cos(cam[2]), math.sin(cam[2])
        f = ("w" in keys) - ("s" in keys)
        s = ("d" in keys) - ("a" in keys)
        vx, vz = fx * f + rx * s, fz * f + rz * s
        n = math.hypot(vx, vz)
        if n > 0:
            speed = RUN if st["shift"] else WALK
            dx, dz = vx / n * speed * dt, vz / n * speed * dt
            if not blocked(cam[0] + dx, cam[1]):
                cam[0] += dx
            if not blocked(cam[0], cam[1] + dz):
                cam[1] += dz
        glutPostRedisplay()

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        cp = math.cos(cam[3])
        gluLookAt(cam[0], EYE, cam[1],
                  cam[0] + math.sin(cam[2]) * cp, EYE + math.sin(cam[3]), cam[1] - math.cos(cam[2]) * cp,
                  0, 1, 0)
        glCallList(scene)
        glutSwapBuffers()

    glutIgnoreKeyRepeat(1)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutKeyboardFunc(key_down)
    glutKeyboardUpFunc(key_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutPassiveMotionFunc(mouse_move)
    glutMotionFunc(mouse_move)
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutWarpPointer(SW // 2, SH // 2)
    glutMainLoop()


if __name__ == "__main__":
    _preview()