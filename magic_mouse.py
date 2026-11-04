import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------- ค่าคงที่ที่ไฟล์หลักเคยเตรียมไว้ให้
INCH = 0.0254  # 1 นิ้ว เป็นเมตร

_l = (-0.45, 0.80, 0.40)  # ทิศแสงสำหรับลงเฉดสี (ปรับได้ตามไฟล์หลัก)
_ln = math.sqrt(sum(c * c for c in _l))
LIGHT_N = tuple(c / _ln for c in _l)  # ทำให้เป็นเวกเตอร์หน่วย


# ---------------------------------------------------------------- โลโก้
def apple_logo_flat(cx, y, cz, size, col=(0.52, 0.53, 0.56), bg=(0.86, 0.86, 0.88)):  # สร้างสูตรวาดโลโก้ Apple บนผิวแนวนอน (เช่น หลังเมาส์)
    """โลโก้ Apple แปะบนผิวแนวนอน (มองจากด้านบน ยอดใบชี้ไปทาง -Z = ไกลตัว)
    cx, cz = จุดกึ่งกลาง  y = ความสูงผิว  size = ความสูงโลโก้ (เมตร)  bg = สีพื้นไว้เติมรอยกัด"""
    k = size / 1.13  # ตัวคูณปรับขนาด

    def disc(ox, oy, rx, ry, rot, color, off, n=24):  # วาดวงกลม/วงรี 1 วง บนพื้นผิวแนวนอน
        a = math.radians(rot)
        glColor3f(*color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(cx + ox * k, y + off, cz - oy * k)  # จุดกึ่งกลางวง (-oy เพราะด้านบนของโลโก้ชี้ไป -Z)
        for i in range(n + 1):
            t = 2 * math.pi * i / n
            ex, ey = rx * math.cos(t), ry * math.sin(t)
            px = ox + ex * math.cos(a) - ey * math.sin(a)
            py = oy + ex * math.sin(a) + ey * math.cos(a)
            glVertex3f(cx + px * k, y + off, cz - py * k)
        glEnd()

    disc(-0.15, -0.02, 0.34, 0.34, 0, col, 0.0003)  # ตัวแอปเปิ้ล วงซ้ายบน
    disc(0.15, -0.02, 0.34, 0.34, 0, col, 0.0003)   # วงขวาบน
    disc(-0.14, -0.27, 0.26, 0.26, 0, col, 0.0003)  # ก้น วงซ้ายล่าง
    disc(0.14, -0.27, 0.26, 0.26, 0, col, 0.0003)   # วงขวาล่าง
    disc(0.47, 0.02, 0.17, 0.17, 0, bg, 0.0006)     # รอยกัด (วงสีพื้นทับ)
    disc(0.10, 0.50, 0.19, 0.08, 38, col, 0.0003)   # ใบ


# ---------------------------------------------------------------- เมาส์
def magic_mouse(cx, y0, cz, yaw=0.0, L=5 * INCH, Wd=2 * INCH, Hm=0.0216):  # สร้างสูตรวาดเมาส์ Apple Magic Mouse (ตำแหน่ง มุมหมุน ยาว กว้าง สูง)
    """Apple Magic Mouse ขนาด 5 x 2 inch (ตามที่วัด) สูงประมาณ 2.2 cm ตัวโค้งมนสีขาว มีโลโก้ Apple บนหลังเมาส์
    ปลายด้านหน้า (ปลายนิ้ว) หันไปทาง -Z (ทางหน้าจอ)  yaw = หมุนรอบแกนตั้ง (องศา)"""
    N, M = 16, 12  # แบ่ง 16 ท่อนตามความยาว และ 12 ชิ้นรอบหน้าตัด
    hw = Wd / 2  # ครึ่งหนึ่งของความกว้าง
    peak = 0.62  # จุดที่เมาส์นูนสูงสุด (62% ของความยาว ค่อนไปทางท้าย)

    def prof(v):  # ความกว้างและความสูง ณ ตำแหน่ง v (0..1)
        t = 2 * v - 1
        w = hw * math.sqrt(max(0.0, 1 - abs(t) ** 3.2))  # ความกว้างตามแปลน (ปลายมน)
        u = (v - peak) / (peak if v < peak else (1 - peak))
        h = Hm * math.sqrt(max(0.0, 1 - u * u))  # ความสูงตามแนวยาว
        return w, h

    def pt(k, m):  # จุดบนผิวเมาส์ (ท่อนที่ k ชิ้นที่ m)
        v = k / N
        w, h = prof(v)
        ph = math.pi * m / M  # มุมรอบหน้าตัด
        return (w * math.cos(ph), h * (math.sin(ph) ** 0.55), -L / 2 + v * L)  # ยกกำลัง 0.55 ให้หลังเมาส์ป้านขึ้น

    glPushMatrix()
    glTranslatef(cx, y0, cz)
    glRotatef(yaw, 0, 1, 0)
    body = (0.95, 0.95, 0.97)  # สีขาวของตัวเมาส์
    glBegin(GL_QUADS)
    for k in range(N):
        for m in range(M):
            p00, p01, p11, p10 = pt(k, m), pt(k, m + 1), pt(k + 1, m + 1), pt(k + 1, m)
            e1 = (p01[0] - p00[0], p01[1] - p00[1], p01[2] - p00[2])
            e2 = (p10[0] - p00[0], p10[1] - p00[1], p10[2] - p00[2])
            n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])  # ทิศผิว (cross product)
            ctr = ((p00[0] + p11[0]) / 2, (p00[1] + p11[1]) / 2 - 0.006, (p00[2] + p11[2]) / 2)  # จุดกลางแผ่น ใช้ตัดสินทิศเข้า/ออก
            if n[0] * ctr[0] + n[1] * ctr[1] + n[2] * ctr[2] < 0:
                n = (-n[0], -n[1], -n[2])  # กลับให้หันออกนอก
            nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
            sh = 0.55 + 0.45 * max(0.0, (n[0] * LIGHT_N[0] + n[1] * LIGHT_N[1] + n[2] * LIGHT_N[2]) / nl)  # ความสว่างตามทิศแสง
            glColor3f(body[0] * sh, body[1] * sh, body[2] * sh)
            glVertex3f(*p00); glVertex3f(*p01); glVertex3f(*p11); glVertex3f(*p10)
    glEnd()
    vz = 0.58  # ตำแหน่งโลโก้ที่ 58% ของความยาว
    apple_logo_flat(0.0, prof(vz)[1] + 0.0004, -L / 2 + vz * L, 0.016)  # โลโก้ 1.6 ซม. ลอยเหนือผิว 0.4 มม.
    glPopMatrix()


# ---------------------------------------------------------------- viewer
# ใช้เฉพาะตอนรันไฟล์นี้ตรงๆ เพื่อดูตัวอย่าง (ไฟล์หลักของเพื่อน import แค่ magic_mouse ก็พอ)
cam = {"yaw": 25.0, "pitch": 40.0, "dist": 0.30, "drag": None}


def display():
    glClearColor(0.55, 0.60, 0.68, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    yaw, pitch, dist = math.radians(cam["yaw"]), math.radians(cam["pitch"]), cam["dist"]
    ex = dist * math.cos(pitch) * math.sin(yaw)
    ey = dist * math.sin(pitch)
    ez = dist * math.cos(pitch) * math.cos(yaw)
    gluLookAt(ex, ey, ez, 0, 0.01, 0, 0, 1, 0)
    magic_mouse(0.0, 0.0, 0.0)  # วางเมาส์ที่จุดกำเนิด
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, w / h, 0.005, 10.0)
    glMatrixMode(GL_MODELVIEW)


def zoom(f):
    cam["dist"] = max(0.08, min(3.0, cam["dist"] * f))
    glutPostRedisplay()


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        cam["drag"] = (x, y) if state == GLUT_DOWN else None
    elif state == GLUT_DOWN and button in (3, 4):  # ล้อเมาส์ (freeglut)
        zoom(0.9 if button == 3 else 1.1)


def motion(x, y):
    if cam["drag"]:
        lx, ly = cam["drag"]
        cam["yaw"] -= (x - lx) * 0.4
        cam["pitch"] = max(-89, min(89, cam["pitch"] + (y - ly) * 0.4))
        cam["drag"] = (x, y)
        glutPostRedisplay()


def key(k, x, y):
    if k in (b'q', b'Q', b'\x1b'):
        sys.exit(0)
    elif k in (b'3', b'+', b'='):
        zoom(0.9)
    elif k in (b'4', b'-'):
        zoom(1.1)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 600)
    glutCreateWindow(b"Magic Mouse")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(key)
    glutMainLoop()


if __name__ == "__main__":
    main()
