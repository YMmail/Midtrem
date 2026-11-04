import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

LIGHT_DIR = (0.577, 0.577, 0.577)
COLLIDERS = []

def stool(cx, y_off, cz, dots=False, solid=False):
    """สตูลเหล็กกลมสีขาว: ที่นั่ง Ø32 cm เจาะรู ขาท่อ 4 ขากางออก ปลายขามียางรอง สูง 45 cm"""

    def _cylinder(cx, y0, cz, r, h, c, seg=18, solid=False):
        """สูตรวาดทรงกระบอก (ผนังข้าง GL_QUADS + ฝาบน GL_TRIANGLE_FAN)"""
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

    def _tube(p0, p1, r, c, seg=8):
        """สูตรวาดท่อกลมระหว่างจุด p0 -> p1 (Cross Product และแสง LIGHT_DIR)"""
        d = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        L = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) or 1.0
        d = (d[0] / L, d[1] / L, d[2] / L)
        ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
        u = (d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0])
        ul = math.sqrt(u[0] ** 2 + u[1] ** 2 + u[2] ** 2) or 1.0
        u = (u[0] / ul, u[1] / ul, u[2] / ul)
        v = (d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0])

        glBegin(GL_QUADS)
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            am = (a0 + a1) / 2
            n = (math.cos(am) * u[0] + math.sin(am) * v[0],
                 math.cos(am) * u[1] + math.sin(am) * v[1],
                 math.cos(am) * u[2] + math.sin(am) * v[2])
            sh = 0.55 + 0.45 * max(0.0, n[0] * LIGHT_DIR[0] + n[1] * LIGHT_DIR[1] + n[2] * LIGHT_DIR[2])
            glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)
            for (a, p) in ((a0, p0), (a1, p0), (a1, p1), (a0, p1)):
                ca, sa = math.cos(a), math.sin(a)
                glVertex3f(p[0] + r * (ca * u[0] + sa * v[0]),
                           p[1] + r * (ca * u[1] + sa * v[1]),
                           p[2] + r * (ca * u[2] + sa * v[2]))
        glEnd()

    def _ball(cx, cy, cz, r, c, seg=12, rings=8):
        """สูตรวาดลูกบอลทรงกลม (ใส่เฉดสีหลอกให้ดูมีมิติ)"""
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
                    glVertex3f(cx + r * math.sin(t) * math.cos(a),
                               cy + r * math.cos(t),
                               cz + r * math.sin(t) * math.sin(a))
        glEnd()

    def _gquad(vertices, colors):
        glBegin(GL_QUADS)
        for v, col in zip(vertices, colors):
            glColor3f(*col)
            glVertex3f(*v)
        glEnd()

    wht = (0.93, 0.93, 0.94)
    cap = (0.62, 0.63, 0.65)
    hs = 0.45

    # 1. ที่นั่งสตูลทรงกระบอกแบน (Ø32 cm, หนา 4 cm)
    _cylinder(cx, y_off + hs - 0.04, cz, 0.16, 0.04, wht, seg=28, solid=solid)

    # 2. จุดรูระบายอากาศบนที่นั่ง
    if dots:
        yy = y_off + hs + 0.002
        dc = (0.55, 0.56, 0.58)
        step, sz = 0.026, 0.0065
        for i in range(-5, 6):
            for j in range(-5, 6):
                dx, dz = i * step, j * step
                if math.hypot(dx, dz) > 0.125 or abs(dx) < 0.012 or abs(dz) < 0.012:
                    continue
                _gquad([(cx + dx - sz, yy, cz + dz - sz),
                        (cx + dx + sz, yy, cz + dz - sz),
                        (cx + dx + sz, yy, cz + dz + sz),
                        (cx + dx - sz, yy, cz + dz + sz)], [dc] * 4)

    # 3. ขาท่อเหล็ก 4 ขาพร้อมข้อต่อทรงกลมและยางรองขา
    for k in range(4):
        a = math.radians(45 + 90 * k)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (cx + 0.135 * ca, y_off + hs - 0.03, cz + 0.135 * sa)
        p1 = (cx + 0.160 * ca, y_off + hs - 0.07, cz + 0.160 * sa)
        p2 = (cx + 0.230 * ca, y_off + 0.045, cz + 0.230 * sa)

        _tube(p0, p1, 0.0125, wht, seg=8)
        _ball(p1[0], p1[1], p1[2], 0.0125, wht, seg=8, rings=6)
        _tube(p1, p2, 0.0125, wht, seg=8)
        _cylinder(p2[0], y_off, p2[2], 0.0145, 0.045, cap, seg=8, solid=False)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # มุมมองกล้องคงที่
    glTranslatef(0.0, -0.22, -1.35)
    glRotatef(22.0, 1, 0, 0)
    glRotatef(-30.0, 0, 1, 0)

    # แสดงผลสตูลเดี่ยวพร้อมเจาะรู
    stool(cx=0.0, y_off=0.0, cz=0.0, dots=True, solid=True)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 750)
    glutCreateWindow(b"Stool with Integrated Ball, Tube, and Cylinder")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (900 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()