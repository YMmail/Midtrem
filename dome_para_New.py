import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------------------
# helper วาดรูปทรงพื้นฐาน
# ---------------------------------------------------------------------------
def box(x0, y0, z0, x1, y1, z1, color, solid=False):
    """กล่องจากมุม (x0,y0,z0) ถึง (x1,y1,z1) พร้อมสี (r,g,b)
    solid ไม่มีผลกับการวาด (เผื่อไฟล์หลักใช้ไว้ทำ collision)"""
    glColor3f(*color)
    glBegin(GL_QUADS)
    # -X (หน้าเครื่อง)
    glNormal3f(-1, 0, 0)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    # +X (หลังเครื่อง)
    glNormal3f(1, 0, 0)
    glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x1, y0, z1)
    # -Y (ล่าง)
    glNormal3f(0, -1, 0)
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    # +Y (บน)
    glNormal3f(0, 1, 0)
    glVertex3f(x0, y1, z0); glVertex3f(x0, y1, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    # -Z
    glNormal3f(0, 0, -1)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y0, z0)
    # +Z
    glNormal3f(0, 0, 1)
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glEnd()


def cylinder(cx, y0, cz, r, h, color, seg=12):
    """ทรงกระบอกตั้งตรง ฐานอยู่ที่ความสูง y0 สูง h รัศมี r"""
    glColor3f(*color)
    y1 = y0 + h
    # ด้านข้าง
    glBegin(GL_QUAD_STRIP)
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        nx, nz = math.cos(a), math.sin(a)
        glNormal3f(nx, 0, nz)
        glVertex3f(cx + r * nx, y0, cz + r * nz)
        glVertex3f(cx + r * nx, y1, cz + r * nz)
    glEnd()
    # ฝาบน
    glNormal3f(0, 1, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx, y1, cz)
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        glVertex3f(cx + r * math.cos(a), y1, cz + r * math.sin(a))
    glEnd()
    # ฝาล่าง
    glNormal3f(0, -1, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx, y0, cz)
    for i in range(seg + 1):
        a = -2 * math.pi * i / seg
        glVertex3f(cx + r * math.cos(a), y0, cz + r * math.sin(a))
    glEnd()


# ---------------------------------------------------------------------------
# ตัวซอฟต์บ็อกซ์ทรงโดมกลม (Nanlite / Parabolic Softbox)
# ---------------------------------------------------------------------------
LIGHT_DIR = (0.35, 0.80, 0.45)  # ทิศทางแสงสมมติ (ขวา บน หน้า) สำหรับคำนวณแสงเงา
COLLIDERS = []                  # สมุดจดสิ่งกีดขวาง (จำลองเผื่อไฟล์หลักเรียกใช้)

def dome_para(cx, cz, d=0.762, h=0.42, ribs=True, seg=16, rings=14, solid=True):  # สร้างสูตรวาดซอฟต์บ็อกซ์ทรงโดมกลม (เส้นผ่านศูนย์กลาง d สูง h)
    """ซอฟต์บ็อกซ์ทรงโดมกลม (ครึ่งวงรี) Ø d  สูง h  วางคว่ำหน้าลงพื้น speed ring อยู่ด้านบน
    ปรับให้กลมขึ้น: h ยิ่งใกล้ d/2 ยิ่งเป็นครึ่งทรงกลม (ค่าเดิม 0.635 สูงและแหลมกว่า)
    ribs=True = ซี่สีขาว (แบบ Nanlite)  ribs=False = ซี่สีดำเหมือนผ้า"""
    r = d / 2  # รัศมี = ครึ่งหนึ่งของเส้นผ่านศูนย์กลาง
    th_top = math.acos(min(0.99, 0.085 / r))          # ตัดยอดตรงขนาด speed ring  # มุมที่ตัดยอดโดมทิ้ง ให้เหลือขนาดเท่าวงแหวนด้านบน
    if solid:  # ถ้าต้องเดินชนได้
        COLLIDERS.append((cx - r, cz - r, cx + r, cz + r))  # จดพื้นที่ของโดมลงสมุดสิ่งกีดขวาง
    body = (0.045, 0.045, 0.05)  # สีผ้าดำของโดม
    rib = (0.90, 0.90, 0.92) if ribs else (0.15, 0.15, 0.16)  # สีซี่: ขาวถ้า ribs เป็น True ไม่งั้นเป็นดำ
    delta = 0.03  # ความกว้างของซี่ (หน่วยมุม)
    glBegin(GL_QUADS)  # เริ่มวาดแผ่นสี่เหลี่ยมบนผิวโดม
    for k in range(rings):  # วนทีละวงจากขอบขึ้นยอด
        ta, tb = th_top * k / rings, th_top * (k + 1) / rings  # มุมเงยของขอบล่างและขอบบนของวงนี้
        rha, rhb = r * math.cos(ta), r * math.cos(tb)  # รัศมีแนวราบของขอบล่างและขอบบน
        ya, yb = h * math.sin(ta), h * math.sin(tb)  # ความสูงของขอบล่างและขอบบน
        tm = (ta + tb) / 2  # มุมตรงกลางของวงนี้
        nx, ny = math.cos(tm) / r, math.sin(tm) / h   # เวกเตอร์ตั้งฉากของวงรี  # ทิศที่ผิวหันไป (ตามสูตรวงรี)
        nl = math.hypot(nx, ny)  # ความยาวของทิศนั้น
        nh, nv = nx / nl, ny / nl  # ทำให้ยาว 1: แนวราบ (nh) และแนวตั้ง (nv)
        for i in range(seg):  # วนทีละช่วงรอบโดม
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg  # มุมเริ่มและมุมจบของช่วงนี้
            for (col, p, q) in ((body, a0 + delta, a1 - delta), (rib, a1 - delta, a1 + delta)):  # วาด 2 ชิ้นต่อช่วง: ผ้าดำ และซี่คั่น
                am = (p + q) / 2  # มุมตรงกลางของชิ้นนี้
                sh = 0.50 + 0.50 * max(0.0, 0.35 * nh * math.cos(am) + 0.8 * nv + 0.45 * nh * math.sin(am))  # ความสว่างตามทิศที่ผิวหัน
                glColor3f(col[0] * sh, col[1] * sh, col[2] * sh)  # เลือกสีชิ้นนี้
                for (aa, rho, yy) in ((p, rha, ya), (q, rha, ya), (q, rhb, yb), (p, rhb, yb)):  # วนทั้ง 4 มุมของชิ้น
                    glVertex3f(cx + rho * math.cos(aa), yy, cz + rho * math.sin(aa))  # ใส่ตำแหน่งมุมนั้น
    glEnd()  # วาดผิวโดมเสร็จ
    y_top = h * math.sin(th_top)  # ความสูงที่ยอดโดมที่ถูกตัด
    cylinder(cx, y_top - 0.01, cz, 0.09, 0.035, (0.68, 0.70, 0.73), 16)     # วงแหวน speed ring  # วาดวงแหวนโลหะสีเทาที่ยอด
    cylinder(cx, y_top + 0.022, cz, 0.062, 0.010, (0.05, 0.05, 0.06), 16)   # ช่องกลางสีดำ  # วาดช่องกลางสีดำบนวงแหวน


# ---------------------------------------------------------------------------
# ส่วนทดสอบ: ทำงานเฉพาะตอนรันไฟล์นี้ตรงๆ (ตอน import จะไม่รันส่วนนี้)
# ---------------------------------------------------------------------------
class _View:
    yaw = math.pi
    pitch = 0.35
    dist = 1.8
    last = None


def _display():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # เปลี่ยนพื้นหลังเป็นสีดำ
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    tx, ty, tz = 0.0, 0.2, 0.0
    ex = tx + _View.dist * math.cos(_View.pitch) * math.cos(_View.yaw)
    ey = ty + _View.dist * math.sin(_View.pitch)
    ez = tz + _View.dist * math.cos(_View.pitch) * math.sin(_View.yaw)
    gluLookAt(ex, ey, ez, tx, ty, tz, 0, 1, 0)

    glLightfv(GL_LIGHT0, GL_POSITION, (-1.0, 2.0, 1.0, 0.0))

    # ลบพื้นห้องออกแล้ว
    dome_para(0.0, 0.0, ribs=True)

    glutSwapBuffers()


def _reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, w / h, 0.05, 50)
    glMatrixMode(GL_MODELVIEW)


def _mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        _View.last = (x, y) if state == GLUT_DOWN else None
    elif state == GLUT_DOWN and button in (3, 4):  # ล้อเมาส์ ซูมเข้า/ออก
        _View.dist *= 0.9 if button == 3 else 1.1
        _View.dist = min(max(_View.dist, 0.4), 10)
        glutPostRedisplay()


def _motion(x, y):
    if _View.last is None:
        return
    lx, ly = _View.last
    _View.yaw += (x - lx) * 0.01
    _View.pitch += (y - ly) * 0.01
    _View.pitch = min(max(_View.pitch, -1.4), 1.4)
    _View.last = (x, y)
    glutPostRedisplay()


def _keyboard(key, x, y):
    if key in (b"\x1b", b"q"):  # ESC หรือ q = ออก
        sys.exit(0)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 650)
    glutCreateWindow(b"Dome Softbox - test")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.45, 0.45, 0.45, 1))
    glEnable(GL_NORMALIZE)

    glutDisplayFunc(_display)
    glutReshapeFunc(_reshape)
    glutMouseFunc(_mouse)
    glutMotionFunc(_motion)
    glutKeyboardFunc(_keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()