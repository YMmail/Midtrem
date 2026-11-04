import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

LIGHT_DIR = (0.577, 0.577, 0.577)
COLLIDERS = []

def bar_stool(cx, cz, yaw=0.0):
    """สตูลบาร์เปลือกพลาสติกขาว + ขาไม้โอ๊ค 4 ขากางออก + ที่พักเท้าเหล็กดำ (แบบ About A Stool)
    ที่นั่งสูง ~65 cm  พนักโค้งอยู่ด้าน +Z  yaw = หมุนรอบแกนตั้ง (องศา)"""

    def _tube(p0, p1, r, c, seg=8):
        """สูตรวาดท่อกลมระหว่างจุด p0 -> p1 (Cross Product และคำนวณแสง LIGHT_DIR)"""
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

    COLLIDERS.append((cx - 0.27, cz - 0.27, cx + 0.27, cz + 0.27))
    white, oak, blk = (0.93, 0.94, 0.97), (0.80, 0.62, 0.38), (0.05, 0.05, 0.06)
    rx, rz, y_c = 0.235, 0.205, 0.625
    seg, rings = 56, 12
    ld = math.sqrt(sum(v * v for v in LIGHT_DIR))
    L = tuple(v / ld for v in LIGHT_DIR)

    def P(a, t, dy=0.0):
        back = max(0.0, math.sin(a)) ** 2
        y = y_c + 0.03 * t ** 2 + 0.11 * back * t ** 3 + dy
        return (rx * t * math.cos(a), y, rz * t * math.sin(a))

    def shade(a, t, sign=1.0):
        t = min(max(t, 0.03), 1.0)
        e = 1e-3
        pa0, pa1 = P(a - e, t), P(a + e, t)
        pt0, pt1 = P(a, max(t - e, 0.0)), P(a, min(t + e, 1.0))
        u = [pa1[j] - pa0[j] for j in range(3)]
        v = [pt1[j] - pt0[j] for j in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        nl = math.sqrt(sum(c * c for c in n)) or 1.0
        n = [sign * c / nl for c in n]
        if n[1] < 0:
            n = [-c for c in n]
        return 0.62 + 0.38 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])

    def vtx(a, t, dy=0.0, k=1.0):
        s = shade(a, t) * k
        glColor3f(white[0] * s, white[1] * s, white[2] * s)
        glVertex3f(*P(a, t, dy))

    glPushMatrix()
    glTranslatef(cx, 0, cz)
    glRotatef(yaw, 0, 1, 0)

    # 1. วาดเปลือกเบาะที่นั่งพลาสติก (ผิวบน ผิวล่าง และขอบหนา)
    glPushMatrix()
    glTranslatef(0.0, -0.033, 0.0)
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        for k in range(rings):
            t0, t1 = k / rings, (k + 1) / rings
            # ผิวบน
            for (a, t) in ((a0, t0), (a1, t0), (a1, t1), (a0, t1)):
                vtx(a, t)
            # ผิวด้านล่าง
            for (a, t) in ((a0, t0), (a0, t1), (a1, t1), (a1, t0)):
                vtx(a, t, -0.037, 0.62)
        # ขอบข้าง
        for (a, dy) in ((a0, 0.0), (a1, 0.0), (a1, -0.037), (a0, -0.037)):
            vtx(a, 1.0, dy, 0.92)
    glEnd()
    glPopMatrix()

    # 2. ขาไม้โอ๊ค 4 ขา
    legs = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            top = (sx * 0.150, 0.612, sz * 0.110)
            bot = (sx * 0.255, 0.0, sz * (0.185 if sz < 0 else 0.250))
            _tube(top, bot, 0.020, oak, 14)
            f = (0.612 - 0.26) / 0.612
            legs.append(tuple(top[j] + (bot[j] - top[j]) * f for j in range(3)))

    # 3. ที่พักเท้าโครงเหล็กดำ
    for (i, j) in ((0, 1), (1, 3), (3, 2), (2, 0)):
        _tube(legs[i], legs[j], 0.006, blk, 10)

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # ตั้งกล้องมุมมองเฉียงหน้าลงต่ำเพื่อให้เห็นพนักพิงหลัง ท้องเบาะ และโครงขา
    glTranslatef(0.0, -0.38, -1.8)
    glRotatef(18.0, 1, 0, 0)
    glRotatef(-35.0, 0, 1, 0)

    # วาดสตูลบาร์ไว้ตรงกลาง (cx=0, cz=0)
    bar_stool(cx=0.0, cz=0.0, yaw=0.0)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 750)
    glutCreateWindow(b"Static Bar Stool Preview")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (900 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()