import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def aircon(cx, z0, y0, length=1.47, wd=0.65, ht=0.25):
    """ฟังก์ชันวาดโมเดลแอร์แขวนเพดาน (รวมฟังก์ชันคำนวณและวาดไว้ในตัว)"""
    def _gquad(vertices, colors):
        glBegin(GL_QUADS)
        for v, c in zip(vertices, colors):
            glColor3f(*c)
            glVertex3f(*v)
        glEnd()

    def _ac_profile(w, h, r_front=0.05, r_back=0.06, segments=6):
        pts = [(r_back, 0.0), (w - r_front, 0.0)]
        for i in range(segments + 1):
            th = -math.pi / 2 + (math.pi / 2) * (i / segments)
            pts.append((w - r_front + r_front * math.cos(th), r_front + r_front * math.sin(th)))
        pts.append((w, h - r_front))
        for i in range(segments + 1):
            th = (math.pi / 2) * (i / segments)
            pts.append((w - r_front + r_front * math.cos(th), h - r_front + r_front * math.sin(th)))
        pts.append((r_back, h))
        for i in range(segments + 1):
            th = math.pi / 2 + (math.pi / 2) * (i / segments)
            pts.append((r_back + r_back * math.cos(th), h - r_back + r_back * math.sin(th)))
        pts.append((0.0, r_back))
        for i in range(segments + 1):
            th = math.pi + (math.pi / 2) * (i / segments)
            pts.append((r_back + r_back * math.cos(th), r_back + r_back * math.sin(th)))
        return pts

    x0, x1 = cx - length / 2, cx + length / 2
    prof = _ac_profile(wd, ht, 0.05, 0.06)
    cream = (0.93, 0.91, 0.84)
    n = len(prof)

    # 1. ตัวเครื่องรอบนอก
    glBegin(GL_QUADS)
    for i in range(n):
        (za, ya), (zb, yb) = prof[i], prof[(i + 1) % n]
        dz, dy = zb - za, yb - ya
        ln = math.hypot(dz, dy) or 1.0
        nz, ny = dy / ln, -dz / ln
        sh = 0.60 + 0.40 * max(0.0, 0.85 * ny + 0.5 * nz)
        glColor3f(cream[0] * sh, cream[1] * sh, cream[2] * sh)
        glVertex3f(x0, y0 + ya, z0 + za)
        glVertex3f(x1, y0 + ya, z0 + za)
        glVertex3f(x1, y0 + yb, z0 + zb)
        glVertex3f(x0, y0 + yb, z0 + zb)
    glEnd()

    # 2. ฝาปิดหัว-ท้าย ซ้ายขวา
    for xx, sh in ((x0, 0.78), (x1, 0.88)):
        glColor3f(cream[0] * sh, cream[1] * sh, cream[2] * sh)
        glBegin(GL_POLYGON)
        for (zz, yy) in prof:
            glVertex3f(xx, y0 + yy, z0 + zz)
        glEnd()

    # 3. รายละเอียดด้านหน้า
    zf = z0 + wd + 0.004
    dark = (0.10, 0.10, 0.11)
    _gquad([(cx - 0.55, y0 + 0.075, zf), (cx + 0.55, y0 + 0.075, zf),
            (cx + 0.55, y0 + 0.115, zf), (cx - 0.55, y0 + 0.115, zf)], [dark] * 4)
    _gquad([(cx - 0.70, y0 + 0.150, zf), (cx + 0.70, y0 + 0.150, zf),
            (cx + 0.70, y0 + 0.153, zf), (cx - 0.70, y0 + 0.153, zf)], [(0.72, 0.70, 0.64)] * 4)
    _gquad([(cx + 0.58, y0 + 0.125, zf), (cx + 0.68, y0 + 0.125, zf),
            (cx + 0.68, y0 + 0.180, zf), (cx + 0.58, y0 + 0.180, zf)], [(0.12, 0.13, 0.15)] * 4)
    _gquad([(cx + 0.595, y0 + 0.145, zf + 0.001), (cx + 0.615, y0 + 0.145, zf + 0.001),
            (cx + 0.615, y0 + 0.160, zf + 0.001), (cx + 0.595, y0 + 0.160, zf + 0.001)],
           [(0.25, 0.85, 0.35)] * 4)

    # 4. รายละเอียดใต้ท้องเครื่อง (กริล + ป้ายเหลือง)
    yb = y0 - 0.003
    for k in range(9):
        zz = z0 + 0.13 + k * 0.048
        _gquad([(cx - 0.62, yb, zz), (cx + 0.40, yb, zz), 
                (cx + 0.40, yb, zz + 0.022), (cx - 0.62, yb, zz + 0.022)],
               [(0.20, 0.20, 0.21)] * 4)
    _gquad([(cx + 0.50, yb, z0 + 0.20), (cx + 0.62, yb, z0 + 0.20), 
            (cx + 0.62, yb, z0 + 0.30), (cx + 0.50, yb, z0 + 0.30)],
           [(0.95, 0.80, 0.20)] * 4)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # กำหนดมุมกล้องแบบคงที่ (มองเฉียง 3 มิติโดยไม่หมุน)
    glTranslatef(0.0, 0.0, -3.2)
    glRotatef(15.0, 1, 0, 0)
    glRotatef(-30.0, 0, 1, 0)
    
    # เรียกใช้ฟังก์ชันวาดแอร์
    aircon(cx=0.0, z0=-0.325, y0=-0.125)
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Static Air Conditioner")

    glEnable(GL_DEPTH_TEST)

    # ตั้งค่ามุมมอง Perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (1000 / 700), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()