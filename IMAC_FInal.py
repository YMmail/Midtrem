import math
import sys
 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
 
 
# ---------------------------------------------------------------------------
# ค่าและ helper
# ---------------------------------------------------------------------------
SHADE_TOP, SHADE_BOT = 1.00, 0.55  # เฉดด้านบน / ด้านล่าง
SHADE_S, SHADE_N = 0.92, 0.78      # เฉดด้านหน้า (+Z) / ด้านหลัง (-Z)
SHADE_E, SHADE_W = 0.85, 0.70      # เฉดด้านขวา (+X) / ด้านซ้าย (-X)
 
 
def _shade(color, k):
    return color[0] * k, color[1] * k, color[2] * k
 
 
def gquad(pts, cols):
    """สี่เหลี่ยม 4 จุด pts=[(x,y,z)]*4 พร้อมสีรายมุม cols=[(r,g,b)]*4"""
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()
 
 
def quad(pts, col):
    """สี่เหลี่ยมสีเดียว"""
    gquad(pts, [col] * 4)
 
 
def box(x0, y0, z0, x1, y1, z1, color):
    """กล่องจากมุม (x0,y0,z0) ถึง (x1,y1,z1) ทาเฉดสีตามทิศแต่ละด้าน"""
    quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], _shade(color, SHADE_TOP))
    quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], _shade(color, SHADE_BOT))
    quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], _shade(color, SHADE_S))
    quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], _shade(color, SHADE_N))
    quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], _shade(color, SHADE_E))
    quad([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], _shade(color, SHADE_W))
 
 
def cbox(cx, y0, z0, w, h, z1, color, flat=False):
    """กล่องที่กึ่งกลางแกน X อยู่ที่ cx กว้าง w สูง h จาก y0 และลึกจาก z0 ถึง z1
    flat=True = วาดเป็นแผ่นบางหน้าเดียว (หันไปทาง +Z) ที่ z1"""
    x0, x1 = cx - w / 2, cx + w / 2
    if flat:
        quad([(x0, y0, z1), (x1, y0, z1), (x1, y0 + h, z1), (x0, y0 + h, z1)], color)
    else:
        box(x0, y0, z0, x1, y0 + h, z1, color)
 
 
def cylinder(cx, y0, cz, r, h, color, seg=12):
    """ทรงกระบอกตั้งตรง ฐานอยู่ที่ความสูง y0 สูง h รัศมี r"""
    y1 = y0 + h
    angles = [2 * math.pi * i / seg for i in range(seg + 1)]
    glBegin(GL_QUAD_STRIP)  # ด้านข้าง: เฉดไล่จากด้านหลังไปด้านหน้าตามทิศ
    for a in angles:
        nx, nz = math.cos(a), math.sin(a)
        glColor3f(*_shade(color, (SHADE_S + SHADE_N) / 2 + (SHADE_S - SHADE_N) / 2 * nz))
        glVertex3f(cx + r * nx, y0, cz + r * nz)
        glVertex3f(cx + r * nx, y1, cz + r * nz)
    glEnd()
    for y, k in ((y1, SHADE_TOP), (y0, SHADE_BOT)):  # ฝาบนและฝาล่าง
        glColor3f(*_shade(color, k))
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(cx, y, cz)
        for a in angles:
            glVertex3f(cx + r * math.cos(a), y, cz + r * math.sin(a))
        glEnd()
 
 
def _strip_x(path, thick, x0, x1, color):
    """ริบบิ้นโลหะบางตามเส้นทาง path=[(y, z), ...] กว้างตามแกน X จาก x0 ถึง x1 หนา thick"""
    h = thick / 2
    a, b = [], []  # ผิวสองด้านของริบบิ้น
    for i, (y, z) in enumerate(path):
        (ya, za), (yb, zb) = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        dy, dz = yb - ya, zb - za
        n = math.hypot(dy, dz) or 1.0
        a.append((y - dz / n * h, z + dy / n * h))
        b.append((y + dz / n * h, z - dy / n * h))
    for i in range(len(path) - 1):
        for side, k in ((a, SHADE_S), (b, SHADE_N)):  # ผิวสองด้าน
            quad([(x0, *side[i]), (x1, *side[i]), (x1, *side[i + 1]), (x0, *side[i + 1])], _shade(color, k))
        for x, k in ((x0, SHADE_W), (x1, SHADE_E)):  # ขอบสองข้าง
            quad([(x, *a[i]), (x, *b[i]), (x, *b[i + 1]), (x, *a[i + 1])], _shade(color, k))
 
 
# ---------------------------------------------------------------------------
# Logo Apple
# ---------------------------------------------------------------------------
# Logo Apple (พิกัดเรขาคณิต Apple แท้ 100% พร้อมใบไม้ทรงโค้งอวบสมส่วน)
# ---------------------------------------------------------------------------
def _eval_cubic_bezier(p0, p1, p2, p3, steps=16):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1.0 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _triangulate_concave_poly(pts):
    def is_inside(a, b, c, p):
        ax, ay = b[0] - a[0], b[1] - a[1]
        bx, by = c[0] - b[0], c[1] - b[1]
        cx, cy = a[0] - c[0], a[1] - c[1]
        c1 = ax * (p[1] - a[1]) - ay * (p[0] - a[0])
        c2 = bx * (p[1] - b[1]) - by * (p[0] - b[0])
        c3 = cx * (p[1] - c[1]) - cy * (p[0] - c[0])
        return (c1 >= 0 and c2 >= 0 and c3 >= 0) or (c1 <= 0 and c2 <= 0 and c3 <= 0)

    indices = list(range(len(pts)))
    triangles = []
    area = sum((pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]) for i in range(len(pts)))
    if area < 0:
        indices.reverse()

    count = 0
    while len(indices) > 2 and count < 800:
        count += 1
        n = len(indices)
        clipped = False
        for i in range(n):
            u = indices[(i - 1 + n) % n]
            v = indices[i]
            w = indices[(i + 1) % n]
            a, b, c = pts[u], pts[v], pts[w]

            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if cross <= 0:
                continue

            ear = True
            for k in range(n):
                if k not in ((i - 1 + n) % n, i, (i + 1) % n):
                    if is_inside(a, b, c, pts[indices[k]]):
                        ear = False
                        break
            if ear:
                triangles.append((a, b, c))
                del indices[i]
                clipped = True
                break
        if not clipped:
            break
    return triangles


def my_logo(x, y, z, size, facing=1, col=(0.60, 0.60, 0.63)):
    """วาดโลโก้ Apple คมกริบ สัดส่วนแท้ 100% พร้อมรอยกัดและใบไม้"""
    z_offset = z + (0.0008 * facing)
    glColor3f(*col)

    # ---------------------------------------------------------
    # 1. ใบไม้ (Apple Leaf) สัดส่วนแท้: รูปทรงเลนส์เอียง 45 องศา โค้งมนไม่ลีบ
    # ---------------------------------------------------------
    # ปลายแหลมล่างของใบอยู่ที่ประมาณ (0.00, 0.28) และปลายบนชี้ไปที่ (0.24, 0.52)
    leaf_p0 = (0.000, 0.280)  # โคนใบไม้ด้านล่าง
    leaf_p2 = (0.240, 0.520)  # ปลายใบไม้ด้านบน
    
    # เส้นโค้งฝั่งซ้ายบน (พองออกด้านซ้ายบน)
    leaf_c1_top = (-0.015, 0.430)
    leaf_c2_top = (0.110, 0.535)
    
    # เส้นโค้งฝั่งขวาล่าง (พองออกด้านขวาล่าง)
    leaf_c2_bot = (0.255, 0.370)
    leaf_c1_bot = (0.130, 0.265)

    leaf_curve_a = _eval_cubic_bezier(leaf_p0, leaf_c1_top, leaf_c2_top, leaf_p2, steps=16)
    leaf_curve_b = _eval_cubic_bezier(leaf_p2, leaf_c2_bot, leaf_c1_bot, leaf_p0, steps=16)
    leaf_pts = leaf_curve_a[:-1] + leaf_curve_b[:-1]

    # ---------------------------------------------------------
    # 2. ผลแอปเปิ้ล (Apple Body) พร้อมรอยกัดและรอยหยักบน-ล่าง
    # ---------------------------------------------------------
    curves = [
        # จากร่องบุ๋มบน (0, 0.235) ไปยังโหนกขวา
        (( 0.000,  0.235), ( 0.045,  0.245), ( 0.125,  0.305), ( 0.235,  0.305)),
        # จากโหนกขวาโค้งลงมาถึงจุดเริ่มต้นรอยกัด
        (( 0.235,  0.305), ( 0.355,  0.305), ( 0.435,  0.210), ( 0.440,  0.080)),
        # รอยกัด (Bite Cutout) โค้งเว้าเข้าหาแกนกลาง
        (( 0.440,  0.080), ( 0.325,  0.070), ( 0.250, -0.065), ( 0.305, -0.205)),
        (( 0.305, -0.205), ( 0.345, -0.265), ( 0.395, -0.295), ( 0.445, -0.295)),
        # โค้งใต้รอยกัดลงไปหาก้นขวา
        (( 0.445, -0.295), ( 0.430, -0.405), ( 0.345, -0.495), ( 0.230, -0.495)),
        # บุ๋มล่าง (ฝั่งขวาเข้าสู่ศูนย์กลาง)
        (( 0.230, -0.495), ( 0.145, -0.495), ( 0.090, -0.455), ( 0.000, -0.455)),
        # บุ๋มล่าง (จากศูนย์กลางไปฝั่งซ้าย)
        (( 0.000, -0.455), (-0.090, -0.455), (-0.145, -0.495), (-0.230, -0.495)),
        # จากก้นซ้ายโค้งขึ้นมาที่สะโพกซ้าย
        ((-0.230, -0.495), (-0.345, -0.495), (-0.445, -0.380), (-0.445, -0.200)),
        # จากสะโพกซ้ายขึ้นไปหาโหนกซ้าย
        ((-0.445, -0.200), (-0.445,  0.050), (-0.370,  0.305), (-0.235,  0.305)),
        # จากโหนกซ้ายกลับลงมาร่องบุ๋มบน
        ((-0.235,  0.305), (-0.125,  0.305), (-0.045,  0.245), ( 0.000,  0.235)),
    ]

    apple_pts = []
    for c in curves:
        pts = _eval_cubic_bezier(c[0], c[1], c[2], c[3], steps=12)
        apple_pts.extend(pts[:-1])

    # ---------------------------------------------------------
    # 3. เรนเดอร์ด้วย GL_TRIANGLES
    # ---------------------------------------------------------
    # ใบไม้
    leaf_tris = _triangulate_concave_poly(leaf_pts)
    glBegin(GL_TRIANGLES)
    for a, b, c in leaf_tris:
        for pt in (a, b, c):
            glVertex3f(x + (pt[0] * size * facing), y + (pt[1] * size), z_offset)
    glEnd()

    # ผลแอปเปิ้ล
    apple_tris = _triangulate_concave_poly(apple_pts)
    glBegin(GL_TRIANGLES)
    for a, b, c in apple_tris:
        for pt in (a, b, c):
            glVertex3f(x + (pt[0] * size * facing), y + (pt[1] * size), z_offset)
    glEnd()


# ---------------------------------------------------------------------------
# iMac
# ---------------------------------------------------------------------------
def imac(ix, ty, iz, iw, ih, tilt=8.0, lift=0.085, logo=None):
    """iMac ตามรูปด้านข้าง: จอแผ่นบางเอนไปด้านหลัง (tilt องศา) หลังจอป่องที่ปลายล่าง
    แขนโค้งโลหะจากหลังจอลงมาที่ฐานแบน ฐานยื่นไปด้านหลังและไปใต้จอ (หน้าจอหันไปทาง +Z)
    ix, iz = กึ่งกลางจอ  ty = ผิวโต๊ะ  iw, ih = กว้าง x สูงของแผ่นจอ  lift = ขอบล่างจอสูงจากโต๊ะ
    logo = (ไม่บังคับ) ฟังก์ชันวาดป้ายที่คางหน้าจอและหลังจอ รับ (x, y, z, size, facing) ถ้าไม่ส่งมาจะไม่วาดอะไร"""
    body = (0.88, 0.88, 0.90)   # สีตัวเครื่อง (เงินอ่อน)
    metal = (0.80, 0.80, 0.82)  # สีโลหะของแขนและฐาน
    t_top, t_bot = 0.008, 0.028  # ความหนาแผ่นจอ: ปลายบนบาง 8 มม. ปลายล่างหนา 28 มม.
    hw = iw / 2
    th = math.radians(tilt)
 
    def back_z(y):  # ผิวหลังจอที่ความสูง y (พิกัดบนแผ่นจอ) ไล่ความหนาจากบนบางไปล่างหนา
        return -(t_top + (t_bot - t_top) * (1 - y / ih))
 
    def to_world(y, z):  # พิกัดบนแผ่นจอ -> (ความสูง, z) จริง โดยหมุนจอเอนหลังรอบจุดล่างหน้า
        return (ty + lift + y * math.cos(th) + z * math.sin(th),
                iz - y * math.sin(th) + z * math.cos(th))
 
    # ---------- ฐาน + แขน (พิกัดโลก) ----------
    fh, fr = 0.012, 0.075  # ฐานหนา 1.2 ซม. ปลายมนรัศมี 7.5 ซม. (สั้นพอไม่ให้เกินขอบโต๊ะ)
    zc = iz - 0.095        # กึ่งกลางปลายมนด้านหลัง
    cylinder(ix, ty, zc, fr, fh, metal, 28)                       # ปลายมนของฐาน
    box(ix - fr, ty, zc, ix + fr, ty + fh, iz + 0.10, metal)      # ส่วนสี่เหลี่ยมที่ยื่นไปใต้จอ
    ay, az = to_world(0.46 * ih, back_z(0.46 * ih) + 0.010)       # จุดที่แขนยึดหลังจอ (46% ของความสูงจอ)
    p0 = (ty + fh * 0.5, zc - 0.035)                              # โคนแขนที่ฐาน
    p1 = (p0[0] + 0.22 * (ay - p0[0]), p0[1])                     # จุดคุมโค้ง ให้แขนตั้งขึ้นก่อนแล้วค่อยเฉียงเข้าหาจอ
    path = []  # เส้นโค้งเบซิเยร์ 17 จุดจากโคนแขนถึงหลังจอ
    for i in range(17):
        t = i / 16
        path.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * ay,
                     (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * az))
    _strip_x(path, 0.009, ix - 0.05, ix + 0.05, metal)  # แขนโลหะบางกว้าง 10 ซม.
 
    # ---------- แผ่นจอ (พิกัดบนแผ่นจอ: เอนหลังรอบแกน X ที่ขอบล่างหน้า) ----------
    glPushMatrix()
    glTranslatef(ix, ty + lift, iz)  # ไปที่ขอบล่างของจอ
    glRotatef(-tilt, 1, 0, 0)        # เอนจอไปด้านหลัง
    bt, bb = back_z(ih), back_z(0)   # ผิวหลังจอที่ขอบบน / ขอบล่าง
    quad([(-hw, 0, 0), (hw, 0, 0), (hw, ih, 0), (-hw, ih, 0)], _shade(body, SHADE_S))     # หน้า
    quad([(-hw, 0, bb), (hw, 0, bb), (hw, ih, bt), (-hw, ih, bt)], _shade(body, SHADE_N))  # หลัง (เอียงเพราะล่างหนากว่าบน)
    quad([(-hw, ih, bt), (hw, ih, bt), (hw, ih, 0), (-hw, ih, 0)], _shade(body, SHADE_TOP))  # ขอบบน
    quad([(-hw, 0, bb), (hw, 0, bb), (hw, 0, 0), (-hw, 0, 0)], _shade(body, SHADE_BOT))      # ขอบล่าง
    for x, k in ((-hw, SHADE_W), (hw, SHADE_E)):  # ขอบข้าง (สี่เหลี่ยมคางหมู)
        quad([(x, 0, bb), (x, 0, 0), (x, ih, 0), (x, ih, bt)], _shade(body, k))
    cbox(0, 0.055, 0.0006, iw - 0.03, ih - 0.075, 0.0006, (0.02, 0.02, 0.03), flat=True)  # พื้นจอดำ เว้นขอบ 1.5 ซม. และคางล่าง
    gquad([(-hw + 0.015, 0.055, 0.0016), (hw - 0.015, 0.055, 0.0016),                    # เงาสะท้อนบนจอ: ล่างมืด บนฟ้าจางๆ
           (hw - 0.015, ih - 0.02, 0.0016), (-hw + 0.015, ih - 0.02, 0.0016)],
          [(0.01, 0.01, 0.015), (0.01, 0.01, 0.015), (0.07, 0.08, 0.11), (0.03, 0.035, 0.05)])
    if logo:  # ป้ายที่คางล่างหน้าจอ และหลังจอ (ตามระนาบหลังที่เอียงนิดๆ ที่ 62% ของความสูง)
        logo(0.0, 0.027, 0.0, 0.026, facing=1)
        glPushMatrix()
        glTranslatef(0.0, ih * 0.62, back_z(ih * 0.62))
        glRotatef(math.degrees(math.atan((t_bot - t_top) / ih)), 1, 0, 0)  # เอียงขนานผิวหลังจอ
        logo(0.0, 0.0, 0.0, 0.060, facing=-1)  # ขนาด 6 ซม. หันไปด้านหลัง
        glPopMatrix()
    glPopMatrix()
 
 
# ---------------------------------------------------------------------------
# หน้าต่างดูโมเดล: ทำงานเฉพาะตอนรันไฟล์นี้ตรงๆ (ตอน import จะไม่รัน)
# ---------------------------------------------------------------------------
class _View:  # กล้องหมุนรอบเครื่อง เริ่มจากด้านหน้า (+Z) เห็นหน้าจอ
    yaw, pitch, dist = math.pi / 2, 0.2, 1.3
    last = None
 
 
def _display():
    glClearColor(0.18, 0.18, 0.20, 1)  # พื้นหลังสีเทาเข้มเรียบๆ
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    ty = 0.25  # มองที่กลางตัวเครื่อง
    gluLookAt(_View.dist * math.cos(_View.pitch) * math.cos(_View.yaw),
              ty + _View.dist * math.sin(_View.pitch),
              _View.dist * math.cos(_View.pitch) * math.sin(_View.yaw),
              0, ty, 0, 0, 1, 0)
    
    # เรียกใช้ imac พร้อมส่งฟังก์ชัน my_logo เข้าไปวาดที่ตำแหน่งหน้าจอและหลังจอ
    imac(0.0, 0.0, 0.0, 0.547, 0.37, logo=my_logo)
    
    glutSwapBuffers()
 
 
def _reshape(w, h):
    glViewport(0, 0, w, max(h, 1))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, w / max(h, 1), 0.05, 60)
    glMatrixMode(GL_MODELVIEW)
 
 
def _mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        _View.last = (x, y) if state == GLUT_DOWN else None
    elif state == GLUT_DOWN and button in (3, 4):  # ล้อเมาส์ ซูมเข้า/ออก
        _View.dist = min(max(_View.dist * (0.9 if button == 3 else 1.1), 0.4), 10)
        glutPostRedisplay()
 
 
def _motion(x, y):
    if _View.last is None:
        return
    lx, ly = _View.last
    _View.yaw += (x - lx) * 0.01
    _View.pitch = min(max(_View.pitch + (y - ly) * 0.01, -1.4), 1.4)
    _View.last = (x, y)
    glutPostRedisplay()
 
 
def _keyboard(key, x, y):
    if key in (b"\x1b", b"q"):
        sys.exit(0)
 
 
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 650)
    glutCreateWindow(b"iMac")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(_display)
    glutReshapeFunc(_reshape)
    glutMouseFunc(_mouse)
    glutMotionFunc(_motion)
    glutKeyboardFunc(_keyboard)
    glutMainLoop()
 
 
if __name__ == "__main__":
    main()