import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ค่าสัมประสิทธิ์ความสว่าง 6 ทิศทางของ box
SHADE_TOP = 1.08
SHADE_BOT = 0.65
SHADE_N = 0.75   # (-Z) เหนือ
SHADE_S = 1.00   # (+Z) ใต้
SHADE_W = 0.85   # (-X) ตะวันตก
SHADE_E = 0.90   # (+X) ตะวันออก

LIGHT_DIR = (0.577, 0.577, 0.577)
COLLIDERS = []

# ค่าคงที่ตำแหน่งและมิติห้อง/ผนัง
W = 6.0          # ความกว้างห้อง
D = 0.0          # ระนาบหน้าผนังฝั่งในห้อง
FZ = -0.12       # ระนาบหน้าผนังฝั่งทางเดิน (ผนังหนา 12 cm)
FAN_CY = 2.20    # ความสูงศูนย์กลางพัดลมจากพื้น

def box(x0, y0, z0, x1, y1, z1, c, solid=False, flat=False):
    """กล่องสี่เหลี่ยม (มุมต่ำ -> มุมสูง) solid=True คือให้เดินชนได้"""
    if solid:
        COLLIDERS.append((min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)))

    r, g, b = c
    k = (1, 1, 1, 1, 1, 1) if flat else (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)

    glBegin(GL_QUADS)
    # top (+Y)
    glColor3f(r * k[0], g * k[0], b * k[0])
    glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)

    # bottom (-Y)
    glColor3f(r * k[1], g * k[1], b * k[1])
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)

    # north (-Z)
    glColor3f(r * k[2], g * k[2], b * k[2])
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x0, y1, z0)

    # south (+Z)
    glColor3f(r * k[3], g * k[3], b * k[3])
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)

    # west (-X)
    glColor3f(r * k[4], g * k[4], b * k[4])
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)

    # east (+X)
    glColor3f(r * k[5], g * k[5], b * k[5])
    glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    glEnd()

def tube(p0, p1, r, c, seg=8):
    """ท่อกลมระหว่างจุด p0 -> p1 (Cross Product และแสง LIGHT_DIR)"""
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

def ball(cx, cy, cz, r, c, seg=12, rings=8):
    """ลูกบอลทรงกลม (ใส่เฉดสีหลอกให้ดูมีมิติ)"""
    glBegin(GL_QUADS)
    for k in range(rings):
        t0, t1 = math.pi * k / rings, math.pi * (k + 1) / rings
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            tm, am = (t0 + t1) / 2, (a0 + a1) / 2
            nx, ny, nz = math.sin(tm) * math.cos(am), math.cos(tm), math.sin(tm) * math.sin(am)
            sh = 0.55 + 0.45 * max(0.0, 0.35 * nx + 0.8 * ny + 0.45 * nz)
            glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)
            for (t, a) in ((t0, a0), (t0, a1), (t1, a1), (t1, a0)):
                glVertex3f(cx + r * math.sin(t) * math.cos(a),
                           cy + r * math.cos(t),
                           cz + r * math.sin(t) * math.sin(a))
    glEnd()

def cable(pts, r=0.008, col=(0.05, 0.05, 0.06), seg=6):
    """สายไฟต่อเนื่องผ่านหลายจุด (ท่อกลมระหว่างจุด + ลูกบอลเล็กที่ข้อต่อให้เนียน)"""
    for p, q in zip(pts[:-1], pts[1:]):
        tube(p, q, r, col, seg)
    for p in pts[1:-1]:
        ball(p[0], p[1], p[2], r * 1.05, col, 6, 4)

def exhaust_fan(cx):
    """ตัวเรือนสี่เหลี่ยมฝังในผนัง มีท่อลมกลมทะลุ + ตะแกรงทั้งสองหน้า"""
    cy = FAN_CY
    zr = D - 0.002
    zc = FZ + 0.002
    hw, ho = 0.15, 0.108
    plate = (0.90, 0.90, 0.88)
    grille = (0.88, 0.88, 0.86)

    # กรอบตัวเรือน 4 ด้าน
    box(cx - hw, cy - hw, D, cx - ho, cy + hw, FZ, plate)
    box(cx + ho, cy - hw, D, cx + hw, cy + hw, FZ, plate)
    box(cx - ho, cy + ho, D, cx + ho, cy + hw, FZ, plate)
    box(cx - ho, cy - hw, D, cx + ho, cy - ho, FZ, plate)

    # ผนังทรงกระบอกด้านในของท่อลม
    glColor3f(0.12, 0.12, 0.13)
    glBegin(GL_QUAD_STRIP)
    for i in range(33):
        a = 2 * math.pi * i / 32
        glVertex3f(cx + ho * math.cos(a), cy + ho * math.sin(a), D)
        glVertex3f(cx + ho * math.cos(a), cy + ho * math.sin(a), FZ)
    glEnd()

    # แผงปิดมุมระหว่างวงกลมกับช่องสี่เหลี่ยมทั้งสองหน้า
    for zf in (zr, zc):
        glColor3f(*plate)
        glBegin(GL_QUADS)
        for i in range(32):
            a0, a1 = 2 * math.pi * i / 32, 2 * math.pi * (i + 1) / 32
            q0 = ho / max(abs(math.cos(a0)), abs(math.sin(a0)))
            q1 = ho / max(abs(math.cos(a1)), abs(math.sin(a1)))
            glVertex3f(cx + ho * math.cos(a0), cy + ho * math.sin(a0), zf)
            glVertex3f(cx + q0 * math.cos(a0), cy + q0 * math.sin(a0), zf)
            glVertex3f(cx + q1 * math.cos(a1), cy + q1 * math.sin(a1), zf)
            glVertex3f(cx + ho * math.cos(a1), cy + ho * math.sin(a1), zf)
        glEnd()

    # ตะแกรงทั้งสองฝั่ง (วงแหวน + กากบาท)
    for zf, sg in ((zr, -1.0), (zc, 1.0)):
        zg = zf + sg * 0.010
        for r in (0.108, 0.070):
            glColor3f(*grille)
            glBegin(GL_QUAD_STRIP)
            for i in range(33):
                a = 2 * math.pi * i / 32
                for rr in (r - 0.003, r + 0.003):
                    glVertex3f(cx + rr * math.cos(a), cy + rr * math.sin(a), zg)
            glEnd()
        box(cx - ho, cy - 0.0035, zg - 0.002, cx + ho, cy + 0.0035, zg + 0.002, grille)
        box(cx - 0.0035, cy - ho, zg - 0.002, cx + 0.0035, cy + ho, zg + 0.002, grille)

    # สายไฟพัดลม (เรียกใช้ฟังก์ชัน cable สูตรดั้งเดิมของคุณ)
    zf = D - 0.067
    s = 1.0 if cx < W / 2 else -1.0
    xc = W / 2 - s * 0.010
    cable([(cx + s * 0.11, cy + 0.13, D - 0.012),
           (xc, cy + 0.13, zf),
           (xc, 2.605, zf),
           (xc, 2.64, D - 0.018),
           (xc, 2.65, D - 0.015)], r=0.004, col=(0.05, 0.05, 0.06), seg=6)

def fan_blades(angle_deg, cx):
    """ใบพัดหมุน 5 ใบ พร้อมดุมตรงกลาง"""
    glPushMatrix()
    glTranslatef(cx, FAN_CY, (D + FZ) / 2)
    glRotatef(angle_deg, 0, 0, 1)

    for k in range(5):
        a0 = 2 * math.pi * k / 5
        a1 = a0 + 0.62
        am = a0 + 0.20
        shade = 1.0 if k % 2 == 0 else 0.86

        glColor3f(0.64 * shade, 0.66 * shade, 0.69 * shade)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(0.100 * math.cos(a0), 0.100 * math.sin(a0), 0)
        glVertex3f(0.098 * math.cos(am), 0.098 * math.sin(am), 0)
        glEnd()

        glColor3f(0.50 * shade, 0.52 * shade, 0.55 * shade)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(0.098 * math.cos(am), 0.098 * math.sin(am), 0)
        glVertex3f(0.100 * math.cos(a1), 0.100 * math.sin(a1), 0)
        glEnd()

    glColor3f(0.85, 0.86, 0.87)
    for dz in (-0.002, 0.002):
        glPushMatrix()
        glTranslatef(0, 0, dz)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(15):
            a = 2 * math.pi * i / 14
            glVertex3f(0.022 * math.cos(a), 0.022 * math.sin(a), 0)
        glEnd()
        glPopMatrix()

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    cx_fan = 1.5
    # ตั้งกล้องมองเฉียงด้านหน้าเพื่อให้เห็นตัวเรือน ตะแกรง และแนวสายไฟ cable
    glTranslatef(0.0, -0.2, -1.0)
    glRotatef(12.0, 1, 0, 0)
    glRotatef(-25.0, 0, 1, 0)
    glTranslatef(-cx_fan, -FAN_CY, -(D + FZ) / 2)

    exhaust_fan(cx=cx_fan)
    fan_blades(angle_deg=0.0, cx=cx_fan)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 750)
    glutCreateWindow(b"Exhaust Fan with Native Cable, Tube, Ball and Box")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (900 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()