"""studio_gfx.py - ตัวช่วยวาดพื้นฐาน (PyOpenGL ล้วน) ใช้ร่วมกันในไฟล์ studio_whiteboard / studio_wall_details"""
import math
from OpenGL.GL import *

LIGHT_DIR = (0.35, 0.80, 0.45)
SHADE_TOP, SHADE_BOT = 1.00, 0.55
SHADE_N, SHADE_S, SHADE_E, SHADE_W = 0.80, 0.90, 0.93, 0.72


def box(x0, y0, z0, x1, y1, z1, c):
    k = (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)
    faces = (((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)),
             ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
             ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)),
             ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)),
             ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)),
             ((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)))
    glBegin(GL_QUADS)
    for f, s in zip(faces, k):
        glColor3f(c[0] * s, c[1] * s, c[2] * s)
        for p in f:
            glVertex3f(*p)
    glEnd()


def gquad(pts, cols):
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()


def ball(cx, cy, cz, r, c, seg=12, rings=8):
    glBegin(GL_QUADS)
    for k in range(rings):
        t0, t1 = math.pi * k / rings, math.pi * (k + 1) / rings
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            tm, am = (t0 + t1) / 2, (a0 + a1) / 2
            nx, ny, nz = math.sin(tm) * math.cos(am), math.cos(tm), math.sin(tm) * math.sin(am)
            sh = 0.55 + 0.45 * max(0.0, 0.35 * nx + 0.8 * ny + 0.45 * nz)
            glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)
            for (t, a) in ((t0, a0), (t0, a1), (t1, a1), (t1, a0)):
                glVertex3f(cx + r * math.sin(t) * math.cos(a), cy + r * math.cos(t),
                           cz + r * math.sin(t) * math.sin(a))
    glEnd()


def tube(p0, p1, r, c, seg=8):
    d = [p1[i] - p0[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d)) or 1.0
    d = [v / L for v in d]
    ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = (d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0])
    ul = math.sqrt(sum(v * v for v in u)) or 1.0
    u = tuple(v / ul for v in u)
    v = (d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0])
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        am = (a0 + a1) / 2
        n = [math.cos(am) * u[j] + math.sin(am) * v[j] for j in range(3)]
        sh = 0.55 + 0.45 * max(0.0, sum(n[j] * LIGHT_DIR[j] for j in range(3)))
        glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)
        for (a, p) in ((a0, p0), (a1, p0), (a1, p1), (a0, p1)):
            ca, sa = math.cos(a), math.sin(a)
            glVertex3f(*[p[j] + r * (ca * u[j] + sa * v[j]) for j in range(3)])
    glEnd()


def cable(pts, r=0.008, col=(0.05, 0.05, 0.06), seg=6):
    for p, q in zip(pts[:-1], pts[1:]):
        tube(p, q, r, col, seg)
    for p in pts[1:-1]:
        ball(p[0], p[1], p[2], r * 1.05, col, 6, 4)


def vcylinder(cx, y0, cz, r, h, c, seg=14):
    """ทรงกระบอกตั้ง (แกน Y) ฐานที่ y0 สูง h"""
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        s = 0.7 + 0.3 * math.cos((a0 + a1) / 2 - 0.8)
        glColor3f(c[0] * s, c[1] * s, c[2] * s)
        for (a, y) in ((a0, y0), (a1, y0), (a1, y0 + h), (a0, y0 + h)):
            glVertex3f(cx + r * math.cos(a), y, cz + r * math.sin(a))
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(*c)
    glVertex3f(cx, y0 + h, cz)
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        glVertex3f(cx + r * math.cos(a), y0 + h, cz + r * math.sin(a))
    glEnd()
