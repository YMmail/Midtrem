import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------------------
# helper วาดรูปทรงพื้นฐาน รองรับ Normal สำหรับ OpenGL Lighting
# ---------------------------------------------------------------------------
def box(x0, y0, z0, x1, y1, z1, color):
    """กล่องจากมุม (x0,y0,z0) ถึง (x1,y1,z1) พร้อมสี (r,g,b)"""
    glColor3f(*color)
    glBegin(GL_QUADS)
    # -X
    glNormal3f(-1, 0, 0)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    # +X
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


def cylinder(cx, y0, cz, r, h, color, seg=16):
    """ทรงกระบอกตั้งตรง ฐานอยู่ที่ความสูง y0 สูง h รัศมี r"""
    glColor3f(*color)
    y1 = y0 + h
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


def gquad(pts, cols):
    """สี่เหลี่ยมไล่สีที่แต่ละมุม (สำหรับหน้าจอ/พื้นผิวแบน)"""
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()


def xcyl(x0, x1, cy, cz, r, col, seg=24):
    """ทรงกระบอกนอนตามแนวแกน X (ใช้ทำล้อลำโพง)"""
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        for (x, a) in ((x0, a0), (x1, a0), (x1, a1), (x0, a1)):
            sa, ca = math.sin(a), math.cos(a)
            glNormal3f(0, sa, ca)
            glColor3f(*col)
            glVertex3f(x, cy + r * sa, cz + r * ca)
    glEnd()


def xring(x, cy, cz, r0, r1, col, seg=24):
    """วงแหวนแบนในระนาบ X"""
    glColor3f(*col)
    glBegin(GL_QUADS)
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        glNormal3f(1.0 if x > 0 else -1.0, 0, 0)
        for (r, a) in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
            glVertex3f(x, cy + r * math.sin(a), cz + r * math.cos(a))
    glEnd()


def _poly_prism(pts, y0, y1, col, top=True):
    """แท่งปริซึมจากรูปหลายเหลี่ยมนูน (x, z) สำหรับทำตัวถังลำโพง"""
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    mz = sum(p[1] for p in pts) / n
    glBegin(GL_QUADS)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ez) or 1.0
        nx, nz = ez / L, -ex / L
        if nx * ((a[0] + b[0]) / 2 - mx) + nz * ((a[1] + b[1]) / 2 - mz) < 0:
            nx, nz = -nx, -nz
        glNormal3f(nx, 0, nz)
        glColor3f(*col)
        glVertex3f(a[0], y0, a[1]); glVertex3f(b[0], y0, b[1])
        glVertex3f(b[0], y1, b[1]); glVertex3f(a[0], y1, a[1])
    glEnd()
    if top:
        glNormal3f(0, 1, 0)
        glColor3f(*col)
        glBegin(GL_POLYGON)
        for p in pts:
            glVertex3f(p[0], y1, p[1])
        glEnd()


# ---------------------------------------------------------------------------
# ฟังก์ชันวาดเครื่องหมายตกใจ (!)
# ---------------------------------------------------------------------------
def draw_exclamation_logo(x, y, z, width=0.18, facing=1, text_color=(0.70, 0.72, 0.75)):
    glNormal3f(0, 0, 1)
    glColor3f(*text_color)
    aspect = 0.35
    height = width * aspect
    zt = z + (0.0010 * facing)
    s = height

    excl_x = x

    glBegin(GL_TRIANGLES)
    glVertex3f(excl_x - 0.12 * s * facing, y + 0.65 * s, zt)
    glVertex3f(excl_x + 0.12 * s * facing, y + 0.65 * s, zt)
    glVertex3f(excl_x, y + 0.05 * s, zt)
    glEnd()

    dot_r = 0.12 * s
    dot_cy = y - 0.20 * s
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(excl_x, dot_cy, zt)
    for i in range(17):
        a = 2 * math.pi * i / 16
        glVertex3f(excl_x + dot_r * math.cos(a), dot_cy + dot_r * math.sin(a), zt)
    glEnd()


# ---------------------------------------------------------------------------
# ฟังก์ชันวาดตัวอักษร JBL ขนาดใหญ่
# ---------------------------------------------------------------------------
def draw_jbl_text_logo(x, y, z, width=0.18, facing=1, text_color=(0.70, 0.72, 0.75)):
    glNormal3f(0, 0, 1)
    glColor3f(*text_color)
    aspect = 0.35
    height = width * aspect
    zt = z + (0.0010 * facing)
    s = height

    # ตัว J
    jx = x - 0.25 * width * facing
    glBegin(GL_QUADS)
    glVertex3f(jx + 0.03 * s * facing, y - 0.22 * s, zt)
    glVertex3f(jx + 0.10 * s * facing, y - 0.22 * s, zt)
    glVertex3f(jx + 0.10 * s * facing, y + 0.35 * s, zt)
    glVertex3f(jx + 0.03 * s * facing, y + 0.35 * s, zt)

    glVertex3f(jx - 0.10 * s * facing, y - 0.35 * s, zt)
    glVertex3f(jx + 0.10 * s * facing, y - 0.35 * s, zt)
    glVertex3f(jx + 0.10 * s * facing, y - 0.22 * s, zt)
    glVertex3f(jx - 0.10 * s * facing, y - 0.22 * s, zt)

    glVertex3f(jx - 0.10 * s * facing, y - 0.35 * s, zt)
    glVertex3f(jx - 0.03 * s * facing, y - 0.35 * s, zt)
    glVertex3f(jx - 0.03 * s * facing, y - 0.05 * s, zt)
    glVertex3f(jx - 0.10 * s * facing, y - 0.05 * s, zt)
    glEnd()

    # ตัว B
    bx = x
    bw, bh = 0.23 * s, 0.70 * s
    glBegin(GL_QUADS)
    glVertex3f(bx - bw / 2, y - bh / 2, zt)
    glVertex3f(bx - bw / 2 + 0.07 * s * facing, y - bh / 2, zt)
    glVertex3f(bx - bw / 2 + 0.07 * s * facing, y + bh / 2, zt)
    glVertex3f(bx - bw / 2, y + bh / 2, zt)

    glVertex3f(bx - bw / 2, y + bh / 2 - 0.07 * s, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y + bh / 2 - 0.07 * s, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y + bh / 2, zt)
    glVertex3f(bx - bw / 2, y + bh / 2, zt)

    glVertex3f(bx - bw / 2, y - 0.035 * s, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y - 0.035 * s, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y + 0.035 * s, zt)
    glVertex3f(bx - bw / 2, y + 0.035 * s, zt)

    glVertex3f(bx - bw / 2, y - bh / 2, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y - bh / 2, zt)
    glVertex3f(bx + bw / 2 - 0.03 * s * facing, y - bh / 2 + 0.07 * s, zt)
    glVertex3f(bx - bw / 2, y - bh / 2 + 0.07 * s, zt)

    glVertex3f(bx + bw / 2 - 0.07 * s * facing, y + 0.02 * s, zt)
    glVertex3f(bx + bw / 2, y + 0.02 * s, zt)
    glVertex3f(bx + bw / 2, y + bh / 2 - 0.04 * s, zt)
    glVertex3f(bx + bw / 2 - 0.07 * s * facing, y + bh / 2 - 0.04 * s, zt)

    glVertex3f(bx + bw / 2 - 0.07 * s * facing, y - bh / 2 + 0.04 * s, zt)
    glVertex3f(bx + bw / 2, y - bh / 2 + 0.04 * s, zt)
    glVertex3f(bx + bw / 2, y - 0.02 * s, zt)
    glVertex3f(bx + bw / 2 - 0.07 * s * facing, y - 0.02 * s, zt)
    glEnd()

    # ตัว L
    lx = x + 0.25 * width * facing
    lw, lh = 0.19 * s, 0.70 * s
    glBegin(GL_QUADS)
    glVertex3f(lx - lw / 2, y - lh / 2, zt)
    glVertex3f(lx - lw / 2 + 0.07 * s * facing, y - lh / 2, zt)
    glVertex3f(lx - lw / 2 + 0.07 * s * facing, y + lh / 2, zt)
    glVertex3f(lx - lw / 2, y + lh / 2, zt)

    glVertex3f(lx - lw / 2, y - lh / 2, zt)
    glVertex3f(lx + lw / 2, y - lh / 2, zt)
    glVertex3f(lx + lw / 2, y - lh / 2 + 0.07 * s, zt)
    glVertex3f(lx - lw / 2, y - lh / 2 + 0.07 * s, zt)
    glEnd()


# ---------------------------------------------------------------------------
# โค้ดโมเดลลำโพง JBL PartyBox 310
# ---------------------------------------------------------------------------
SPK_W, SPK_H, SPK_D = 0.3256, 0.6877, 0.3678
SPK_ORANGE = (0.95, 0.40, 0.08)


def _chamf_rect(hw, hd, c):
    """สี่เหลี่ยมตัดมุมเฉียง (แปลนตัวลำโพง)"""
    return [(-hw + c, -hd), (hw - c, -hd), (hw, -hd + c), (hw, hd - c),
            (hw - c, hd), (-hw + c, hd), (-hw, hd - c), (-hw, -hd + c)]


def _bar(cx, cy, dx, dy, z, length, width, col):
    """แท่งสี่เหลี่ยมเอียงบนผิวหน้า ทำคลิปส้มที่มุมตะแกรง"""
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    hl, hw = length / 2, width / 2
    gquad([(cx - dx * hl - px * hw, cy - dy * hl - py * hw, z),
           (cx + dx * hl - px * hw, cy + dy * hl - py * hw, z),
           (cx + dx * hl + px * hw, cy + dy * hl + py * hw, z),
           (cx - dx * hl + px * hw, cy - dy * hl + py * hw, z)], [col] * 4)


def _spk_grille(z, hx, y0, y1, logo_type=None):
    """แผงตะแกรง: พื้นดำ + เส้นตะแกรงถี่ + คลิปส้ม 4 มุม (+ โลโก้ตามประเภท)"""
    gquad([(-hx, y0, z), (hx, y0, z), (hx, y1, z), (-hx, y1, z)], [(0.035, 0.035, 0.04)] * 4)
    zz = z + 0.0006
    n = int((y1 - y0) / 0.0065)
    for k in range(n):
        yy = y0 + 0.003 + k * 0.0065
        gquad([(-hx + 0.006, yy, zz), (hx - 0.006, yy, zz),
               (hx - 0.006, yy + 0.0022, zz), (-hx + 0.006, yy + 0.0022, zz)], [(0.13, 0.13, 0.14)] * 4)
    for (sx, sy) in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        cx = sx * (hx - 0.020)
        cy = (y1 - 0.030) if sy > 0 else (y0 + 0.030)
        _bar(cx, cy, sx * -1.0, -sy * 1.0, zz + 0.0006, 0.050, 0.013, SPK_ORANGE)
    
    if logo_type == 'jbl':
        draw_jbl_text_logo(0.0, (y0 + y1) / 2, zz + 0.0012, width=0.18)
    elif logo_type == 'exclamation':
        draw_exclamation_logo(0.0, (y0 + y1) / 2, zz + 0.0012, width=0.18)


def jbl_speaker(cx, cz, yaw):
    """สร้างโมเดลลำโพง JBL PartyBox 310 ทั้งตัว"""
    hw, hd, H = SPK_W / 2, SPK_D / 2, SPK_H
    blk = (0.055, 0.055, 0.06)
    glPushMatrix()
    glTranslatef(cx, 0, cz)
    glRotatef(yaw, 0, 1, 0)

    # ตัวถัง
    _poly_prism(_chamf_rect(hw, hd, 0.050), 0.018, H - 0.085, blk, top=False)
    _poly_prism(_chamf_rect(hw * 1.03, hd * 1.025, 0.054), H - 0.085, H, blk)
    box(-hw + 0.03, 0.0, hd - 0.08, -hw + 0.09, 0.02, hd - 0.03, (0.04, 0.04, 0.045))
    box(hw - 0.09, 0.0, hd - 0.08, hw - 0.03, 0.02, hd - 0.03, (0.04, 0.04, 0.045))

    # ตะแกรงหน้าหลัก (หันไปทาง +Z) -> ปล่อยโล่ง
    _spk_grille(hd + 0.002, 0.125, 0.075, H - 0.125, logo_type=None)
    
    # ตะแกรงข้างขวา (หันไปทาง +X) -> แสดงตัวอักษร JBL
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    _spk_grille(hw + 0.002, 0.140, 0.075, H - 0.125, logo_type='jbl')
    glPopMatrix()
    
    # ตะแกรงข้างซ้าย (หันไปทาง -X) -> แสดงเครื่องหมายตกใจ (!)
    glPushMatrix()
    glRotatef(-90, 0, 1, 0)
    _spk_grille(hw + 0.002, 0.140, 0.075, H - 0.125, logo_type='exclamation')
    glPopMatrix()
    
    # ตะแกรงหลัง
    glPushMatrix()
    glRotatef(180, 0, 1, 0)
    _spk_grille(hd + 0.002, 0.125, 0.075, H - 0.125, logo_type=None)
    zp = hd + 0.0035
    gquad([(-0.065, 0.20, zp), (0.065, 0.20, zp), (0.065, 0.36, zp), (-0.065, 0.36, zp)], [(0.16, 0.16, 0.17)] * 4)
    for (px, py) in ((-0.03, 0.31), (0.03, 0.31), (-0.03, 0.25), (0.03, 0.25)):
        gquad([(px - 0.011, py - 0.011, zp + 0.0006), (px + 0.011, py - 0.011, zp + 0.0006),
               (px + 0.011, py + 0.011, zp + 0.0006), (px - 0.011, py + 0.011, zp + 0.0006)], [(0.02, 0.02, 0.025)] * 4)
    glPopMatrix()

    # ล้อหลัง
    wr, wz = 0.055, -hd + 0.040
    for sgn in (1, -1):
        xa, xb = sgn * (hw - 0.012), sgn * (hw + 0.030)
        x0, x1 = min(xa, xb), max(xa, xb)
        xcyl(x0, x1, wr, wz, wr, (0.04, 0.04, 0.045), 24)
        xo = xb + sgn * 0.0006
        xring(xo, wr, wz, 0.0, wr, (0.05, 0.05, 0.055), 24)
        xring(xo + sgn * 0.0006, wr, wz, 0.008, 0.026, (0.35, 0.36, 0.38), 20)

    # ด้านบน (แผงควบคุมและหูหิ้ว)
    yt = H + 0.0012
    gquad([(-0.100, yt, 0.075), (0.100, yt, 0.075), (0.100, yt, 0.150), (-0.100, yt, 0.150)], [(0.015, 0.015, 0.02)] * 4)
    for (bx, bz) in ((-0.045, 0.020), (0.0, 0.020), (0.045, 0.020), (-0.045, -0.025), (0.0, -0.025), (0.045, -0.025)):
        cylinder(bx, H, bz, 0.010, 0.003, (0.30, 0.31, 0.33), 14)
    cylinder(-0.105, H, -0.005, 0.014, 0.003, (0.30, 0.31, 0.33), 16)
    cylinder(0.105, H, -0.005, 0.014, 0.003, (0.30, 0.31, 0.33), 16)
    gquad([(-0.085, yt + 0.0004, -0.150), (0.085, yt + 0.0004, -0.150), (0.085, yt + 0.0004, -0.108), (-0.085, yt + 0.0004, -0.108)], [(0.40, 0.41, 0.43)] * 4)
    gquad([(-0.085, yt + 0.0004, -0.108), (0.085, yt + 0.0004, -0.108), (0.085, yt + 0.0004, -0.096), (-0.085, yt + 0.0004, -0.096)], [SPK_ORANGE] * 4)
    glPopMatrix()


def jbl_speaker_station(cx=0.0, cz=0.0, yaw=0):
    """ฟังก์ชันหลักสำหรับเรียกใช้วางลำโพง"""
    jbl_speaker(cx, cz, yaw)


# ---------------------------------------------------------------------------
# ส่วนทดสอบ: รันไฟล์นี้เดี่ยวๆ เพื่อดูโมเดลลำโพง 3 มิติ
# ---------------------------------------------------------------------------
class _View:
    yaw = math.pi / 4
    pitch = 0.35
    dist = 2.0
    last = None


def _display():
    # เปลี่ยนพื้นหลัง (BG) เป็นสีดำสนิท
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

    # ลบโค้ดวาดพื้น (Floor) ออกแล้ว คงเหลือแต่โมเดลลำโพง
    jbl_speaker_station(0.0, 0.0, yaw=0)

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
    elif state == GLUT_DOWN and button in (3, 4):
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
    if key in (b"\x1b", b"q"):
        sys.exit(0)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 650)
    glutCreateWindow(b"JBL Speaker Clean BG - test")

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