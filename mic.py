import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ======================================================================
# furniture module (PyOpenGL) - ไฟล์ย่อย ให้ไฟล์ห้องใหญ่ import ไปเรียกใช้
#   from mic import mic
#   mic(x, y, z, yaw)      # y = ระดับแกนไมค์ (ผิวโต๊ะ + ~0.034 ให้หัวไมค์วางพอดี)
# ไม่มี main() / glutInit ตอนถูก import จะไม่เปิดหน้าต่างซ้อน
# ======================================================================
__all__ = ["mic"]


# ======================================================================
# ฟังก์ชันวาดพื้นฐาน (helper) ชื่อขึ้นต้นด้วย _ กันชนกับ cylinder/ball ของไฟล์ใหญ่
# ======================================================================
def _cylinder(x, y, z, r, h, color, seg=14):
    """ทรงกระบอกตั้ง ฐานอยู่ที่ y สูงขึ้นไป h (มีฝาปิดบนล่าง)"""
    glColor3f(*color)
    glBegin(GL_QUAD_STRIP)
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        nx, nz = math.cos(a), math.sin(a)
        glNormal3f(nx, 0, nz)
        glVertex3f(x + r * nx, y, z + r * nz)
        glVertex3f(x + r * nx, y + h, z + r * nz)
    glEnd()
    for yy, ny in ((y, -1), (y + h, 1)):
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, ny, 0)
        glVertex3f(x, yy, z)
        for i in range(seg + 1):
            a = 2 * math.pi * i / seg
            glVertex3f(x + r * math.cos(a), yy, z + r * math.sin(a))
        glEnd()


def _ball(x, y, z, r, color, slices=14, stacks=10):
    """ลูกบอล"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    q = gluNewQuadric()
    gluSphere(q, r, slices, stacks)
    gluDeleteQuadric(q)
    glPopMatrix()


# ======================================================================
# ไมค์
# ======================================================================
def mic(x, y, z, yaw):
    """ไมค์ไร้สายแบบมือถือ (แบบ JBL ในรูป) วางนอนบนโต๊ะ ยาวประมาณ 25 cm
    ก่อนหมุนหัวไมค์ชี้ไปทาง +X  yaw = หมุนรอบแกนตั้ง (องศา)"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(yaw, 0, 1, 0)                                           # หมุนรอบแกนตั้ง
    glRotatef(-90, 0, 0, 1)                                           # ล้มไมค์ลงนอน แกนยาวชี้ไปทาง +X
    _cylinder(0, 0.000, 0, 0.0175, 0.130, (0.07, 0.07, 0.08), 14)     # ด้ามจับสีดำ
    _cylinder(0, 0.130, 0, 0.0185, 0.045, (0.12, 0.12, 0.13), 14)     # ส่วนต่อหัว
    _cylinder(0, 0.055, 0, 0.0185, 0.012, (0.95, 0.45, 0.10), 14)     # แถบสีส้ม (ป้ายแบรนด์)
    _cylinder(0, 0.175, 0, 0.0245, 0.012, (0.60, 0.62, 0.65), 14)     # วงแหวนโลหะ
    _ball(0, 0.215, 0, 0.034, (0.30, 0.31, 0.33))                     # หัวไมค์ตะแกรง
    glPopMatrix()


# ======================================================================
# ตัวดูโมเดลไว้ทดสอบเดี่ยว (ทำงานเฉพาะตอนรัน python mic.py)
# ======================================================================
cam = {"yaw": 0.0, "pitch": 20.0, "dist": 0.7}
last = {"x": 0, "y": 0}


def display():
    glClearColor(0.85, 0.87, 0.90, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, cam["dist"], 0, 0, 0, 0, 1, 0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.5, 1.0, 1.0, 0.0))
    glRotatef(cam["pitch"], 1, 0, 0)
    glRotatef(cam["yaw"], 0, 1, 0)
    glTranslatef(-0.12, -0.034, 0)                       # หมุนรอบกลางตัวไมค์
    mic(0, 0.034, 0, 0)
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)


def zoom(delta):
    cam["dist"] = max(0.2, min(5.0, cam["dist"] + delta))
    glutPostRedisplay()


def on_mouse(button, state, x, y):
    last["x"], last["y"] = x, y
    if state == GLUT_DOWN and button == 3:
        zoom(-0.05)
    elif state == GLUT_DOWN and button == 4:
        zoom(0.05)


def on_wheel(wheel_no, direction, x, y):
    zoom(-0.05 if direction > 0 else 0.05)


def on_motion(x, y):
    cam["yaw"] += (x - last["x"]) * 0.5
    cam["pitch"] = max(-89, min(89, cam["pitch"] + (y - last["y"]) * 0.5))
    last["x"], last["y"] = x, y
    glutPostRedisplay()


def on_key(key, x, y):
    if key in (b"q", b"Q", b"\x1b"):
        sys.exit(0)
    if key in (b"3", b"+", b"="):
        zoom(-0.05)
    elif key in (b"4", b"-"):
        zoom(0.05)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 600)
    glutCreateWindow(b"Microphone")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.45, 0.45, 0.45, 1))
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(on_mouse)
    glutMotionFunc(on_motion)
    glutKeyboardFunc(on_key)
    try:
        glutMouseWheelFunc(on_wheel)
    except Exception:
        pass
    glutMainLoop()


if __name__ == "__main__":
    main()
