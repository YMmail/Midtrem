import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


INCH = 0.0254  # 1 นิ้ว เป็นเมตร


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
    solid ไว้ให้ signature ตรงกับไฟล์หลัก ไม่มีผลต่อการวาด"""
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


def cbox(cx, y0, cz, w, h, d, color, solid=False):
    """กล่องแบบระบุจุดกึ่งกลาง: (cx, cz) = กึ่งกลางฐาน, y0 = ระดับฐาน,
    w = กว้างแกน x, h = สูง, d = ลึกแกน z"""
    box(cx - w / 2, y0, cz - d / 2, cx + w / 2, y0 + h, cz + d / 2, color, solid)


# ---------------------------------------------------------------- โต๊ะดำ
def black_table(cx=0.0, cz=0.0):  # สร้างสูตรวาดโต๊ะผ้าดำ (cx, cz = ตำแหน่งกึ่งกลางโต๊ะ)
    """โต๊ะผ้าดำ 60 x 23.5 inch สูง 29.5 inch (วาดเฉพาะตัวโต๊ะ ไม่มีของวางบนโต๊ะ)
    ไฟล์หลักเดิมใช้ cx = 2.62 และ cz = BLACK_TABLE_Z"""
    ty = 29.5 * INCH  # ความสูงผิวโต๊ะ 29.5 นิ้ว
    cbox(cx, 0, cz, 60 * INCH, ty, 23.5 * INCH, (0.05, 0.05, 0.06), solid=True)  # ตัวโต๊ะเป็นกล่องทึบ 60 x 23.5 นิ้ว


# ---------------------------------------------------------------- viewer
# ใช้เฉพาะตอนรันไฟล์นี้ตรงๆ เพื่อดูตัวอย่าง (ไฟล์หลักของเพื่อน import แค่ black_table ก็พอ)
cam = {"yaw": 30.0, "pitch": 30.0, "dist": 3.2, "drag": None}


def display():
    glClearColor(0.78, 0.81, 0.85, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    yaw, pitch, dist = math.radians(cam["yaw"]), math.radians(cam["pitch"]), cam["dist"]
    ex = dist * math.cos(pitch) * math.sin(yaw)
    ey = dist * math.sin(pitch)
    ez = dist * math.cos(pitch) * math.cos(yaw)
    gluLookAt(ex, ey, ez, 0, 0.375, 0, 0, 1, 0)
    black_table()  # วางโต๊ะที่จุดกำเนิด
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, w / h, 0.05, 50.0)
    glMatrixMode(GL_MODELVIEW)


def zoom(f):
    cam["dist"] = max(0.5, min(15.0, cam["dist"] * f))
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
    glutCreateWindow(b"Black Table")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(key)
    glutMainLoop()


if __name__ == "__main__":
    main()
