import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------------------
# helper วาดรูปทรงพื้นฐาน
# ---------------------------------------------------------------------------
def box(x0, y0, z0, x1, y1, z1, color, solid=False):
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
# ตัวเครื่องปรับอากาศ
# ---------------------------------------------------------------------------
def portable_ac(cx, cz):
    """เครื่องปรับอากาศแบบตั้งพื้น (portable) หน้าเครื่องหันเข้าห้อง (-X) มีล้อ ช่องดูดลม ช่องเป่าลมแบบมีครีบ
    แผงควบคุมด้านบน (หน้าจอ LED + ปุ่ม + ช่องลมบน) มือจับข้างเครื่อง ช่องดูระดับน้ำ"""
    sx, sz = 0.28, 0.45  # ขนาดตัวเครื่องบนพื้น: ลึก 28 ซม. (ซ้าย-ขวา) x กว้าง 45 ซม. (หน้า-หลัง)
    xf, xb = cx - sx / 2, cx + sx / 2  # ตำแหน่งด้านหน้า (xf) และด้านหลัง (xb) ของเครื่อง
    z0, z1 = cz - sz / 2, cz + sz / 2  # ตำแหน่งขอบด้านหนึ่ง (z0) และอีกด้านหนึ่ง (z1) ของเครื่อง
    cream, grey = (0.92, 0.91, 0.86), (0.40, 0.41, 0.44)  # สีครีมของตัวเครื่อง และสีเทาเข้มของฝาบน
    dark, slat = (0.09, 0.09, 0.10), (0.58, 0.59, 0.61)  # สีเกือบดำ (ช่องลม/ล้อ) และสีเทาอ่อน (ซี่กริล)
    
    # วาดล้อ 4 ล้อ
    for dx in (-0.09, 0.09):  
        for dz in (-0.17, 0.17):  
            cylinder(cx + dx, 0.0, cz + dz, 0.022, 0.04, dark, 10)  
            
    box(xf + 0.008, 0.035, z0 + 0.008, xb - 0.008, 0.075, z1 - 0.008, (0.55, 0.55, 0.58))   # ฐานแบนๆ สีเทาเหนือล้อ
    box(xf, 0.075, z0, xb, 0.60, z1, cream, solid=True)                                    # ตัวเครื่องหลักสีครีม
    box(xf - 0.006, 0.60, z0 - 0.006, xb + 0.006, 0.628, z1 + 0.006, grey)                 # ฝาบนสีเทา
    ty = 0.6285  # ความสูงผิวหน้าฝาบน

    def rect(xa, xb_, za, zb, col, y=ty + 0.0005):  
        glBegin(GL_QUADS)
        glColor3f(*col)
        glNormal3f(0, 1, 0)
        glVertex3f(xa, y, za); glVertex3f(xb_, y, za); glVertex3f(xb_, y, zb); glVertex3f(xa, y, zb)
        glEnd()

    rect(xf + 0.03, xf + 0.085, cz - 0.14, cz + 0.14, (0.05, 0.06, 0.07), ty)             # หน้าจอแสดงผลเป็นแผ่นดำ
    led = (0.95, 0.30, 0.18)  # สีส้มแดงของตัวเลขไฟ LED
    
    for zc in (cz - 0.090, cz - 0.055):                                                    
        rect(xf + 0.071, xf + 0.075, zc - 0.009, zc + 0.009, led)  
        rect(xf + 0.0565, xf + 0.0585, zc - 0.009, zc + 0.009, led)  
        rect(xf + 0.040, xf + 0.044, zc - 0.009, zc + 0.009, led)  
        rect(xf + 0.040, xf + 0.075, zc - 0.009, zc - 0.0065, led)  
        rect(xf + 0.040, xf + 0.075, zc + 0.0065, zc + 0.009, led)  
        
    for k, c in enumerate(((0.2, 0.9, 0.3), (0.2, 0.6, 0.95), (0.95, 0.75, 0.2))):         
        rect(xf + 0.045, xf + 0.052, cz + 0.02 + 0.035 * k, cz + 0.032 + 0.035 * k, c)  
        
    for k in range(5):                                                                      
        cylinder(xf + 0.115, ty, cz - 0.12 + 0.06 * k, 0.011, 0.004, (0.78, 0.79, 0.80), 14)  
        
    rect(xf + 0.15, xb - 0.03, cz - 0.15, cz + 0.15, dark, ty)                              # ช่องลมออกด้านบน
    
    for k in range(7):  
        x = xf + 0.16 + k * 0.0145  
        box(x, ty, cz - 0.15, x + 0.006, ty + 0.006, cz + 0.15, slat)  

    # ---- ด้านหน้า (หันเข้าห้อง) ----
    xp = xf - 0.001  
    box(xp, 0.47, cz - 0.17, xp, 0.57, cz + 0.17, dark)  # ช่องเป่าลมออกด้านหน้า
    
    for k in range(5):                                                                      
        yy = 0.485 + k * 0.017  
        box(xf - 0.012, yy, cz - 0.17, xf, yy + 0.007, cz + 0.17, cream)  
        
    box(xp, 0.14, cz - 0.18, xp, 0.40, cz + 0.18, dark)  # ช่องดูดลมด้านล่าง
    
    for k in range(15):                                                                     
        yy = 0.145 + k * 0.017  
        box(xf - 0.006, yy, cz - 0.18, xf, yy + 0.007, cz + 0.18, slat)  
        
    for dz in (-0.06, 0.06):  
        box(xf - 0.007, 0.14, cz + dz - 0.003, xf, 0.40, cz + dz + 0.003, cream)  
        
    box(xf - 0.008, 0.40, cz - 0.19, xf, 0.41, cz + 0.19, cream)                            
    box(xf - 0.008, 0.13, cz - 0.19, xf, 0.14, cz + 0.19, cream)  
    box(xf - 0.008, 0.14, cz - 0.19, xf, 0.40, cz - 0.18, cream)  
    box(xf - 0.008, 0.14, cz + 0.18, xf, 0.40, cz + 0.19, cream)  
    
    box(xp, 0.423, cz - 0.07, xp, 0.447, cz + 0.07, (0.76, 0.78, 0.81))  # ป้ายชื่อแบรนด์
    
    for (za, zb) in ((-0.055, -0.030), (-0.022, 0.010), (0.018, 0.050)):  
        box(xp - 0.0005, 0.431, cz + za, xp - 0.0005, 0.439, cz + zb, (0.20, 0.21, 0.24))  
               
    box(xp, 0.09, cz + 0.08, xp, 0.12, cz + 0.17, (0.35, 0.60, 0.80))  # ช่องดูระดับน้ำ
    box(xf - 0.015, 0.095, cz - 0.16, xf, 0.115, cz - 0.13, dark)                           # จุกระบายน้ำ
    
    for zz in (z0 - 0.001, z1 + 0.001):                                                     
        box(cx - 0.07, 0.40, zz, cx + 0.07, 0.47, zz, (0.12, 0.12, 0.13))  # มือจับข้างเครื่อง
        box(cx - 0.07, 0.397, zz, cx + 0.07, 0.40, zz, (0.70, 0.70, 0.68))


# ---------------------------------------------------------------------------
# ส่วนทดสอบ: ทำงานเฉพาะตอนรันไฟล์นี้ตรงๆ (ตอน import จะไม่รันส่วนนี้)
# ---------------------------------------------------------------------------
class _View:
    yaw = math.pi      # เริ่มมองจากฝั่ง -X ให้เห็นหน้าเครื่อง
    pitch = 0.35
    dist = 2.0
    last = None


def _display():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # เปลี่ยนพื้นหลังเป็นสีดำ
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    tx, ty, tz = 0.0, 0.3, 0.0
    ex = tx + _View.dist * math.cos(_View.pitch) * math.cos(_View.yaw)
    ey = ty + _View.dist * math.sin(_View.pitch)
    ez = tz + _View.dist * math.cos(_View.pitch) * math.sin(_View.yaw)
    gluLookAt(ex, ey, ez, tx, ty, tz, 0, 1, 0)

    glLightfv(GL_LIGHT0, GL_POSITION, (-1.0, 2.0, 1.0, 0.0))

    # ลบพื้นห้องออกแล้ว
    portable_ac(0.0, 0.0)

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
    glutCreateWindow(b"Portable AC - test")

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