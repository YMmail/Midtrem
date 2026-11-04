import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ======================================================================
# furniture module (PyOpenGL) - ไฟล์ย่อย ให้ไฟล์ห้องใหญ่ import ไปเรียกใช้
#   from office_chair import office_chair, stool_stack_positions
#   office_chair(x, z, facing=1, colliders=COLLIDERS)
# ไม่มี main() / glutInit ตอนถูก import จะไม่เปิดหน้าต่างซ้อน
# ======================================================================
INCH = 0.0254            # 1 นิ้ว = 0.0254 เมตร

__all__ = ["office_chair", "stool_stack_positions",
           "STOOL_STACK_N", "STOOL_PITCH"]


# ======================================================================
# ฟังก์ชันวาดพื้นฐาน (helper) ชื่อขึ้นต้นด้วย _ กันชนกับ box/cylinder ของไฟล์ใหญ่
# ======================================================================
def _box(x0, y0, z0, x1, y1, z1, color, solid=False):
    """กล่องสี่เหลี่ยมจากมุมต่ำสุดไปมุมสูงสุด"""
    glColor3f(*color)
    glBegin(GL_QUADS)
    glNormal3f(0, 0, -1); glVertex3f(x0, y0, z0); glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y0, z0)
    glNormal3f(0, 0, 1);  glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glNormal3f(-1, 0, 0); glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    glNormal3f(1, 0, 0);  glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x1, y0, z1)
    glNormal3f(0, 1, 0);  glVertex3f(x0, y1, z0); glVertex3f(x0, y1, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    glNormal3f(0, -1, 0); glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    glEnd()


def _cylinder(x, y, z, r, h, color, seg=14):
    """ทรงกระบอกตั้ง ฐานอยู่ที่ y สูงขึ้นไป h"""
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


def _tube(p0, p1, r, color, seg=8):
    """ท่อกลมเชื่อมจากจุด p0 ไป p1"""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-9:
        return
    glPushMatrix()
    glTranslatef(*p0)
    ax, ay = -dy, dx
    ang = math.degrees(math.acos(max(-1.0, min(1.0, dz / length))))
    if abs(ax) > 1e-9 or abs(ay) > 1e-9:
        glRotatef(ang, ax, ay, 0)
    elif dz < 0:
        glRotatef(180, 1, 0, 0)
    glColor3f(*color)
    q = gluNewQuadric()
    gluCylinder(q, r, r, length, seg, 1)
    gluDeleteQuadric(q)
    glPopMatrix()


def _ball(x, y, z, r, color, slices=10, stacks=6):
    """ลูกบอล"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    q = gluNewQuadric()
    gluSphere(q, r, slices, stacks)
    gluDeleteQuadric(q)
    glPopMatrix()


# ======================================================================
# เก้าอี้สำนักงาน
# ======================================================================
def office_chair(cx, cz, facing=1, colliders=None):
    """เก้าอี้หนังผู้บริหารพนักสูง (facing=1 หันไปทาง -Z)"""
    brown, brown2 = (0.45, 0.24, 0.12), (0.41, 0.21, 0.10)
    blk, pad = (0.08, 0.08, 0.09), (0.13, 0.13, 0.14)
    steel = (0.62, 0.64, 0.67)
    if colliders is not None:
        colliders.append((cx - 0.30, cz - 0.30, cx + 0.30, cz + 0.30))
    glPushMatrix()
    glTranslatef(cx, 0, cz)
    if facing < 0:
        glRotatef(180, 0, 1, 0)
    sw = 18 * INCH
    sh = 18.5 * INCH
    h2 = sw / 2
    ya = 26.5 * INCH

    # ---------- เบาะนั่ง ----------
    _box(-h2 + 0.01, sh - 0.0635, -h2, h2 - 0.01, sh - 0.02, h2, blk)
    _box(-h2 - 0.005, sh - 0.075, -h2 - 0.005, h2 + 0.005, sh - 0.0635, h2 + 0.005, blk)
    gap = 0.008
    band = (sw - 3 * gap) / 4
    for i in range(4):
        za = -h2 + i * (band + gap)
        top = sh - 0.012 if i == 0 else sh
        _box(-h2, sh - 0.0635, za, h2, top, za + band, brown if i % 2 == 0 else brown2)
    _box(-h2 - 0.006, sh - 0.0635, -h2, -h2 + 0.006, sh - 0.004, h2, blk)
    _box(h2 - 0.006, sh - 0.0635, -h2, h2 + 0.006, sh - 0.004, h2, blk)

    # ---------- กลไกใต้เบาะ + ก้านปรับ ----------
    _box(-0.12, sh - 0.125, -0.12, 0.12, sh - 0.075, 0.12, blk)
    _box(-0.26, sh - 0.095, -0.03, 0.26, sh - 0.075, 0.03, blk)
    _tube((0.10, sh - 0.105, 0.0), (0.20, sh - 0.115, -0.10), 0.006, blk, 8)
    _ball(0.20, sh - 0.115, -0.10, 0.011, blk, 8, 6)

    # ---------- ที่วางแขน ----------
    for sx in (-0.262, 0.262):
        _box(sx - 0.012, sh - 0.095, -0.17, sx + 0.012, sh - 0.075, 0.12, blk)
        _tube((sx, sh - 0.085, 0.10), (sx, sh + 0.05, 0.115), 0.013, blk, 10)
        _tube((sx, sh + 0.05, 0.115), (sx, ya - 0.02, 0.09), 0.013, blk, 10)
        _ball(sx, sh + 0.05, 0.115, 0.013, blk, 10, 6)
        _tube((sx, sh - 0.085, -0.16), (sx, sh + 0.06, -0.175), 0.013, blk, 10)
        _tube((sx, sh + 0.06, -0.175), (sx, ya - 0.02, -0.19), 0.013, blk, 10)
        _ball(sx, sh + 0.06, -0.175, 0.013, blk, 10, 6)
        _box(sx - 0.026, ya - 0.02, -0.19, sx + 0.026, ya + 0.022, 0.15, pad)
        _cylinder(sx, ya - 0.02, -0.19, 0.026, 0.042, pad, 14)
        _box(sx - 0.020, ya + 0.022, -0.17, sx + 0.020, ya + 0.026, 0.12, (0.18, 0.18, 0.19))

    # ---------- พนักพิง (เอนหลัง 8 องศา) ----------
    zp = h2 - 0.03
    glPushMatrix()
    glTranslatef(0, sh, zp)
    glRotatef(8, 1, 0, 0)
    BH = 0.526
    hw = 0.245
    _box(-0.035, -0.10, -0.03, 0.035, 0.06, 0.03, blk)
    _box(-hw, 0.03, 0.02, hw, BH, 0.05, blk)
    _box(-hw, 0.03, -0.05, hw, 0.05, 0.05, blk)
    _box(-hw, BH - 0.026, -0.05, hw, BH, 0.05, blk)
    _box(-hw, 0.03, -0.05, -hw + 0.024, BH, 0.05, blk)
    _box(hw - 0.024, 0.03, -0.05, hw, BH, 0.05, blk)
    iw = hw - 0.024
    y_a, y_b = 0.05, BH - 0.026
    n, g = 5, 0.010
    ph = (y_b - y_a - (n - 1) * g) / n
    for i in range(n):
        ya_i = y_a + i * (ph + g)
        _box(-iw, ya_i, -0.055, iw, ya_i + ph, 0.02, brown if i % 2 == 0 else brown2)
    _box(-0.004, y_a, -0.057, 0.004, y_b, -0.040, blk)
    glPopMatrix()

    # ---------- แกนยกระดับ + ขา 5 แฉก + ล้อ ----------
    _cylinder(0, 0.14, 0, 0.036, 0.17, blk, 14)
    _cylinder(0, 0.31, 0, 0.026, sh - 0.125 - 0.31, (0.30, 0.30, 0.32), 14)
    _cylinder(0, 0.31, 0, 0.032, 0.015, steel, 14)
    _cylinder(0, 0.105, 0, 0.050, 0.040, blk, 14)
    for k in range(5):
        a = math.radians(18 + 72 * k)
        ca, sa = math.cos(a), math.sin(a)
        tip = (0.33 * ca, 0.085, 0.33 * sa)
        _tube((0.0, 0.125, 0.0), tip, 0.021, blk, 8)
        _ball(tip[0], tip[1], tip[2], 0.021, blk, 8, 6)
        _cylinder(tip[0], 0.060, tip[2], 0.009, 0.040, steel, 8)
        _box(tip[0] - 0.012, 0.050, tip[2] - 0.020, tip[0] + 0.012, 0.062, tip[2] + 0.020, blk)
        glPushMatrix()
        glTranslatef(tip[0], 0, tip[2])
        glRotatef(-math.degrees(a), 0, 1, 0)
        for dz in (-0.014, 0.014):
            _ball(0.0, 0.026, dz, 0.026, (0.05, 0.05, 0.06), 10, 6)
        glPopMatrix()
    glPopMatrix()


# ======================================================================
# ตำแหน่งกองสตูล (รับความลึกห้องจากไฟล์ใหญ่ ไม่ต้องมีตัวแปร D ในไฟล์นี้)
# ======================================================================
STOOL_STACK_N = 5        # จำนวนสตูลต่อกอง
STOOL_PITCH = 0.14       # ระยะห่างแนวตั้งของสตูลในกอง (เมตร)


def stool_stack_positions(room_depth):
    """คืนรายการ (x, z) ของ 3 กอง ชิดผนังตะวันตก เริ่มจากมุมใกล้ประตู"""
    D = room_depth
    return [(0.30, D - 0.30), (0.30, D - 0.82), (0.30, D - 1.34)]


# ======================================================================
# ตัวดูโมเดลไว้ทดสอบเดี่ยว (ทำงานเฉพาะตอนรัน python office_chair.py)
# ======================================================================
cam = {"yaw": 150.0, "pitch": 15.0, "dist": 2.6}
last = {"x": 0, "y": 0}


def display():
    glClearColor(0.85, 0.87, 0.90, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, cam["dist"], 0, 0, 0, 0, 1, 0)
    glRotatef(cam["pitch"], 1, 0, 0)
    glRotatef(cam["yaw"], 0, 1, 0)
    glTranslatef(0, -0.5, 0)            # หมุนรอบกลางตัวเก้าอี้
    glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 2.0, 2.0, 0.0))
    office_chair(0, 0)
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.05, 50)
    glMatrixMode(GL_MODELVIEW)


def zoom(delta):
    cam["dist"] = max(0.8, min(10.0, cam["dist"] + delta))
    glutPostRedisplay()


def mouse(button, state, x, y):
    last["x"], last["y"] = x, y
    if state == GLUT_DOWN and button == 3:
        zoom(-0.15)
    elif state == GLUT_DOWN and button == 4:
        zoom(0.15)


def wheel(wheel_no, direction, x, y):
    zoom(-0.15 if direction > 0 else 0.15)


def motion(x, y):
    cam["yaw"] += (x - last["x"]) * 0.5
    cam["pitch"] = max(-89, min(89, cam["pitch"] + (y - last["y"]) * 0.5))
    last["x"], last["y"] = x, y
    glutPostRedisplay()


def keyboard(key, x, y):
    if key in (b"q", b"Q", b"\x1b"):
        sys.exit(0)
    if key in (b"3", b"+", b"="):
        zoom(-0.15)
    elif key in (b"4", b"-"):
        zoom(0.15)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 700)
    glutCreateWindow(b"Office Chair")
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
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    try:
        glutMouseWheelFunc(wheel)
    except Exception:
        pass
    glutMainLoop()


if __name__ == "__main__":
    main()
