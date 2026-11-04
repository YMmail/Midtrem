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
# ตัวซอฟต์บ็อกซ์สี่เหลี่ยม (Godox)
# ---------------------------------------------------------------------------
LIGHT_DIR = (0.35, 0.80, 0.45)  # ทิศทางแสงสมมติ (ขวา บน หน้า) สำหรับคำนวณแสงเงา
COLLIDERS = []                  # สมุดจดสิ่งกีดขวาง (จำลองเผื่อไฟล์หลักเรียกใช้)

def softbox_rect(cx, cz, yaw, w=0.991, d=0.686, h=0.457, solid=True):  # สร้างสูตรวาดซอฟต์บ็อกซ์สี่เหลี่ยม (ตำแหน่ง มุมหมุน กว้าง ลึก สูง)
    """ซอฟต์บ็อกซ์สี่เหลี่ยม (Godox) หน้าเปิด 39 x 27 inch ลึก 18 inch วางคว่ำหน้าลงพื้น
    ด้านยาว (w) ขนานแกน X ก่อนหมุน  yaw = หมุนรอบแกนตั้ง (องศา)"""
    a = 0.085  # ครึ่งหนึ่งของด้านสี่เหลี่ยมเล็กที่ยอด (ตรงที่ติดกับตัวยึดไฟ)
    B = [(-w / 2, 0, -d / 2), (w / 2, 0, -d / 2), (w / 2, 0, d / 2), (-w / 2, 0, d / 2)]  # มุมทั้ง 4 ของฐานใหญ่ (ที่ติดพื้น) นับจากจุดกึ่งกลาง
    T = [(-a, h, -a), (a, h, -a), (a, h, a), (-a, h, a)]  # มุมทั้ง 4 ของยอดเล็ก (ที่อยู่สูงจากพื้น h)
    if solid:  # ถ้าต้องเดินชนได้
        th = math.radians(yaw)  # แปลงมุมหมุนจากองศาเป็นเรเดียน
        cs, sn = math.cos(th), math.sin(th)  # ค่า cos และ sin ของมุมหมุน (ใช้คำนวณการหมุน)
        xs = [cx + p[0] * cs + p[2] * sn for p in B]  # ตำแหน่งแกน x ของมุมฐานทั้ง 4 หลังหมุนแล้ว
        zs = [cz - p[0] * sn + p[2] * cs for p in B]  # ตำแหน่งแกน z ของมุมฐานทั้ง 4 หลังหมุนแล้ว
        COLLIDERS.append((min(xs), min(zs), max(xs), max(zs)))  # จดสี่เหลี่ยมที่ครอบรอยฐานไว้ในสมุดสิ่งกีดขวาง
    glPushMatrix()  # เซฟตำแหน่งและมุมปัจจุบันไว้ก่อน
    glTranslatef(cx, 0, cz)  # ย้ายจุดอ้างอิงไปที่ตำแหน่งวางซอฟต์บ็อกซ์
    glRotatef(yaw, 0, 1, 0)  # หมุนรอบแกนตั้งตามมุมที่กำหนด
    glBegin(GL_QUADS)  # เริ่มวาดแผ่นสี่เหลี่ยม
    for i in range(4):  # วนทีละด้านข้างของซอฟต์บ็อกซ์ (มี 4 ด้าน)
        j = (i + 1) % 4  # มุมถัดไป (มุมสุดท้ายวนกลับไปมุมแรก)
        e1 = (B[j][0] - B[i][0], B[j][1] - B[i][1], B[j][2] - B[i][2])  # เส้นตามขอบฐานของด้านนี้
        e2 = (T[i][0] - B[i][0], T[i][1] - B[i][1], T[i][2] - B[i][2])  # เส้นเอียงจากฐานขึ้นไปยอด
        n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])  # หาทิศที่ผิวด้านนี้หันไป (cross product ของเส้นสองเส้นข้างบน)
        mx = (B[i][0] + B[j][0]) / 2  # จุดกึ่งกลางของขอบฐาน (แกน x)
        mz = (B[i][2] + B[j][2]) / 2  # จุดกึ่งกลางของขอบฐาน (แกน z)
        if n[0] * mx + n[2] * mz < 0:  # ตรวจว่าทิศนี้หันเข้าด้านในหรือเปล่า
            n = (-n[0], -n[1], -n[2])  # ถ้าหันเข้าด้านใน กลับทิศให้หันออกนอก
        nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0  # ความยาวของทิศ (กันไม่ให้เป็นศูนย์)
        sh = 0.55 + 0.45 * max(0.0, (n[0] * LIGHT_DIR[0] + n[1] * LIGHT_DIR[1] + n[2] * LIGHT_DIR[2]) / nl)  # ความสว่าง ยิ่งผิวหันเข้าหาแสงสมมติยิ่งสว่าง ต่ำสุด 55%
        glColor3f(0.10 * sh, 0.10 * sh, 0.11 * sh)  # เลือกสีผ้าดำ คูณด้วยความสว่าง
        glVertex3f(*B[i]); glVertex3f(*B[j]); glVertex3f(*T[j]); glVertex3f(*T[i])  # วาดด้านข้างโดยใช้ 4 มุม (ฐานสองมุม ยอดสองมุม)
    glColor3f(0.08, 0.08, 0.09)  # เลือกสีดำสำหรับฝาด้านบน
    for p in T:  # วนทั้ง 4 มุมของยอด
        glVertex3f(*p)  # ใส่เป็นมุมของฝาบน
    glEnd()  # วาดผิวเสร็จ
    white = (0.90, 0.90, 0.92)  # ขอบผ้าสีขาวรอบหน้าเปิด
    box(-w / 2, 0, -d / 2, w / 2, 0.025, -d / 2 + 0.02, white)  # ขอบขาวแถบที่ 1 (ด้านเหนือ)
    box(-w / 2, 0, d / 2 - 0.02, w / 2, 0.025, d / 2, white)  # ขอบขาวแถบที่ 2 (ด้านใต้)
    box(-w / 2, 0, -d / 2, -w / 2 + 0.02, 0.025, d / 2, white)  # ขอบขาวแถบที่ 3 (ด้านตะวันตก)
    box(w / 2 - 0.02, 0, -d / 2, w / 2, 0.025, d / 2, white)  # ขอบขาวแถบที่ 4 (ด้านตะวันออก)
    cylinder(0, h - 0.005, 0, 0.075, 0.035, (0.68, 0.70, 0.73), 16)  # speed ring (วงแหวนโลหะสีเทาที่ยอด)
    cylinder(0, h + 0.022, 0, 0.050, 0.010, (0.05, 0.05, 0.06), 16)  # ช่องกลางสีดำบนวงแหวน
    glPopMatrix()  # กลับไปยังตำแหน่งที่เซฟไว้ เพื่อไม่ให้กระทบสิ่งอื่นที่จะวาดต่อ


# ---------------------------------------------------------------------------
# ส่วนทดสอบ: ทำงานเฉพาะตอนรันไฟล์นี้ตรงๆ (ตอน import จะไม่รันส่วนนี้)
# ---------------------------------------------------------------------------
class _View:
    yaw = math.pi
    pitch = 0.35
    dist = 2.0
    last = None


def _display():
    # เปลี่ยนสีพื้นหลัง (BG) เป็นสีดำสนิท (0.0, 0.0, 0.0)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    tx, ty, tz = 0.0, 0.3, 0.0
    ex = tx + _View.dist * math.cos(_View.pitch) * math.cos(_View.yaw)
    ey = ty + _View.dist * math.sin(_View.pitch)
    ez = tz + _View.dist * math.cos(_View.pitch) * math.sin(_View.yaw)
    gluLookAt(ex, ey, ez, tx, ty, tz, 0, 1, 0)

    glLightfv(GL_LIGHT0, GL_POSITION, (-1.0, 2.0, 1.0, 0.0))

    # ลบโค้ดวาดพื้นห้อง (Floor) ออกแล้ว
    softbox_rect(0.0, 0.0, yaw=15)

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
    glutCreateWindow(b"Softbox Rect - test")

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