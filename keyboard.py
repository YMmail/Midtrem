import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------- helpers
def gquad(pts, cols):
    """วาดสี่เหลี่ยม 1 แผ่น pts = 4 จุด, cols = สี 4 จุด"""
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()


def box(x0, y0, z0, x1, y1, z1, color, solid=False):
    """กล่องสี่เหลี่ยม ทาสีเฉดตามทิศหน้า (ไม่ใช้ไฟ OpenGL)
    solid ไว้ให้ signature ตรงกับไฟล์หลัก ไม่มีผลในไฟล์นี้"""
    r, g, b = color
    shade = lambda k: (r * k, g * k, b * k)
    faces = [
        (1.00, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),  # บน
        (0.55, [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),  # ล่าง
        (0.88, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),  # หน้า
        (0.70, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]),  # หลัง
        (0.75, [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)]),  # ซ้าย
        (0.90, [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)]),  # ขวา
    ]
    for k, pts in faces:
        gquad(pts, [shade(k)] * 4)


# ---------------------------------------------------------------- keyboard
def keyboard(cx, y0, cz, w=0.279, d=0.115):  # สร้างสูตรวาดคีย์บอร์ด Apple (ตำแหน่ง กว้าง ลึก)
    """คีย์บอร์ดแบบ Apple Magic Keyboard ขนาดจริง 279 x 115 mm ตัวเอียงสูง 10.8 -> 4.1 mm
    แถวฟังก์ชันอยู่ไกลตัว (z น้อย) แถวสเปซบาร์อยู่ใกล้ตัว (z มาก)  แต่ละปุ่มมีสัญลักษณ์เล็กๆ บนหน้าปุ่ม"""
    x0, x1 = cx - w / 2, cx + w / 2  # ขอบซ้ายและขวา
    z0, z1 = cz - d / 2, cz + d / 2  # ขอบหลังและขอบหน้า
    hb, hf = 0.0108, 0.0041  # ความสูงด้านหลัง / ด้านหน้า (ทรงลิ่ม)
    silver, keyc, leg = (0.82, 0.82, 0.84), (0.97, 0.97, 0.98), (0.13, 0.13, 0.15)  # สีตัวเครื่อง ปุ่ม และสัญลักษณ์

    def top_y(z):  # ความสูงของผิวคีย์บอร์ด ณ ตำแหน่ง z
        return y0 + hb + (hf - hb) * (z - z0) / d

    # ตัวเครื่องอะลูมิเนียมทรงลิ่ม
    glBegin(GL_QUADS)
    glColor3f(*silver)  # ด้านบน (ลาดเอียง)
    glVertex3f(x0, y0 + hb, z0); glVertex3f(x1, y0 + hb, z0); glVertex3f(x1, y0 + hf, z1); glVertex3f(x0, y0 + hf, z1)
    glColor3f(silver[0] * 0.85, silver[1] * 0.85, silver[2] * 0.85)  # ด้านหน้า
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y0 + hf, z1); glVertex3f(x0, y0 + hf, z1)
    glColor3f(silver[0] * 0.70, silver[1] * 0.70, silver[2] * 0.70)  # ด้านหลัง
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0 + hb, z0); glVertex3f(x0, y0 + hb, z0)
    glColor3f(silver[0] * 0.75, silver[1] * 0.75, silver[2] * 0.75)  # ด้านซ้าย
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y0 + hf, z1); glVertex3f(x0, y0 + hb, z0)
    glColor3f(silver[0] * 0.90, silver[1] * 0.90, silver[2] * 0.90)  # ด้านขวา
    glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x1, y0 + hf, z1); glVertex3f(x1, y0 + hb, z0)
    glEnd()

    # (ความกว้างปุ่มเป็นหน่วย u, ชนิด)  ชนิด: None ปกติ / 'sp' สเปซบาร์ / 'ud' ลูกศรขึ้น-ลง (ครึ่งความสูง)
    n = lambda k: [(1.0, None)] * k
    rows = [
        (0.0115, [(1.5, None)] + n(13)),  # แถวฟังก์ชัน (เตี้ยกว่า)
        (0.0185, n(13) + [(1.5, None)]),  # แถวตัวเลข + delete
        (0.0185, [(1.5, None)] + n(13)),  # แถว tab
        (0.0185, [(1.75, None)] + n(11) + [(1.75, None)]),  # แถว caps lock
        (0.0185, [(2.25, None)] + n(10) + [(2.25, None)]),  # แถว shift
        (0.0185, [(1.0, None)] * 3 + [(1.25, None), (5.0, 'sp'), (1.25, None), (1.0, None),
                                      (1.0, None), (1.0, 'ud'), (1.0, None)]),  # แถวล่างสุด
    ]
    xa0 = x0 + 0.005  # จุดเริ่มวางปุ่มแนวนอน
    u = (w - 0.010) / 14.5  # ความกว้าง 1 หน่วยปุ่ม
    gap = 0.0016  # ช่องว่างระหว่างปุ่ม
    zc = z0 + 0.0055  # จุดเริ่มวางแถวแรก
    for (rh, keys) in rows:
        xc = xa0
        for (kw, kind) in keys:
            ka, kb = xc + gap / 2, xc + kw * u - gap / 2
            xc += kw * u
            cells = [(zc + gap / 2, zc + rh - gap / 2)]
            if kind == 'ud':  # ลูกศรขึ้น/ลง แบ่งครึ่ง
                mid = zc + rh / 2
                cells = [(zc + gap / 2, mid - gap / 4), (mid + gap / 4, zc + rh - gap / 2)]
            for (za, zb) in cells:
                yb = min(top_y(za), top_y(zb)) - 0.0008  # ก้นปุ่ม
                yt = max(top_y(za), top_y(zb)) + 0.0032  # หน้าปุ่ม
                box(ka, yb, za, kb, yt, zb, keyc)
                if kind != 'sp':  # สัญลักษณ์บนปุ่ม
                    mx, mz = (ka + kb) / 2, (za + zb) / 2
                    if kw < 1.2:
                        sx, sz = 0.0022, 0.0022
                        lx0, lz0 = mx - sx, mz - sz
                    else:
                        sx, sz = 0.0036, 0.0016
                        lx0, lz0 = ka + 0.0025, zb - 0.0045
                    gquad([(lx0, yt + 0.0004, lz0), (lx0 + 2 * sx, yt + 0.0004, lz0),
                           (lx0 + 2 * sx, yt + 0.0004, lz0 + 2 * sz), (lx0, yt + 0.0004, lz0 + 2 * sz)],
                          [leg] * 4)
        zc += rh


# ---------------------------------------------------------------- viewer
# ส่วนนี้ใช้เฉพาะตอนรันไฟล์นี้ตรงๆ เพื่อดูตัวอย่าง (ไฟล์หลักของเพื่อน import แค่ keyboard ก็พอ)
cam = {"yaw": 25.0, "pitch": 35.0, "dist": 0.55, "drag": None}


def display():
    glClearColor(0.55, 0.60, 0.68, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    yaw, pitch, dist = math.radians(cam["yaw"]), math.radians(cam["pitch"]), cam["dist"]
    ex = dist * math.cos(pitch) * math.sin(yaw)
    ey = dist * math.sin(pitch)
    ez = dist * math.cos(pitch) * math.cos(yaw)
    gluLookAt(ex, ey, ez, 0, 0.005, 0, 0, 1, 0)
    keyboard(0.0, 0.0, 0.0)  # วางคีย์บอร์ดที่จุดกำเนิด
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, w / h, 0.01, 10.0)
    glMatrixMode(GL_MODELVIEW)


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


def zoom(f):
    cam["dist"] = max(0.1, min(3.0, cam["dist"] * f))
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
    glutCreateWindow(b"Keyboard")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(key)
    glutMainLoop()


if __name__ == "__main__":
    main()
