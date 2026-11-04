import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def front_shoe_racks():
    """ชั้นวางรองเท้าไม้ + ท่อสแตนเลส 3 ชั้นเรียงติดกัน (รวมค่าคงที่และฟังก์ชันย่อยไว้ในตัว)"""
    # --- 1. การกำหนดค่าคงที่เฉพาะของโมเดล ---
    FZ = 0.0                      # ระนาบผนัง
    RACK_X0 = 0.0                 # จุดเริ่มวางชั้นแรก
    RACK_LENS = [0.80, 0.70, 0.60] # ความยาวแต่ละช่วง
    RACK_T = 0.018                # ความหนาแผ่นไม้ (1.8 ซม.)
    RACK_H = 0.49                 # ความสูงแผ่นข้าง (49 ซม.)
    RACK_D = 0.15                 # ความลึกแผ่นข้าง (15 ซม.)
    RACK_RODS = 7                 # จำนวนแถวท่อ
    RACK_ROD_Y0 = 0.06            # ระดับความสูงท่อล่างสุด
    RACK_ROD_PITCH = 0.065         # ระยะห่างความสูงระหว่างท่อ
    RACK_ROD_R = 0.007            # รัศมีท่อสแตนเลส
    
    WOOD = (0.76, 0.54, 0.32)     # สีเนื้อไม้
    EDGE = (0.80, 0.80, 0.42)     # สีขอบแผ่นไม้
    STEEL = (0.85, 0.87, 0.90)    # สีสแตนเลส

    SHADE_TOP = 1.08
    SHADE_BOT = 0.65
    SHADE_N = 0.75
    SHADE_S = 1.00
    SHADE_W = 0.85
    SHADE_E = 0.90

    # --- 2. ฟังก์ชันเรขาคณิตย่อยเฉพาะตัว ---
    def _box(x0, y0, z0, x1, y1, z1, c):
        r, g, b = c
        k = (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)
        glBegin(GL_QUADS)
        glColor3f(r * k[0], g * k[0], b * k[0])
        glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
        glColor3f(r * k[1], g * k[1], b * k[1])
        glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
        glColor3f(r * k[2], g * k[2], b * k[2])
        glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x0, y1, z0)
        glColor3f(r * k[3], g * k[3], b * k[3])
        glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
        glColor3f(r * k[4], g * k[4], b * k[4])
        glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
        glColor3f(r * k[5], g * k[5], b * k[5])
        glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
        glEnd()

    def _xcyl(x0, x1, cy, cz, r, c, seg=10):
        rr, gg, bb = c
        glBegin(GL_QUAD_STRIP)
        for i in range(seg + 1):
            a = 2.0 * math.pi * i / seg
            dy, dz = r * math.sin(a), r * math.cos(a)
            sh = 0.65 + 0.35 * max(0.0, 0.70 * (dy / r) + 0.70 * (dz / r))
            glColor3f(rr * sh, gg * sh, bb * sh)
            glVertex3f(x0, cy + dy, cz + dz)
            glVertex3f(x1, cy + dy, cz + dz)
        glEnd()

    # --- 3. การประกอบและวาดชิ้นงาน ---
    x = RACK_X0
    for L in RACK_LENS:
        xa, xb = x, x + L
        for (px0, px1) in ((xa, xa + RACK_T), (xb - RACK_T, xb)):
            _box(px0, 0.0, FZ, px1, RACK_H, FZ + RACK_D, WOOD)
            _box(px0, 0.0, FZ + RACK_D - 0.006, px1, RACK_H, FZ + RACK_D, EDGE)

        for k in range(RACK_RODS):
            y = RACK_ROD_Y0 + k * RACK_ROD_PITCH
            zc = FZ + 0.03 + 0.10 * (1.0 - k / float(RACK_RODS - 1))
            _xcyl(xa + RACK_T, xb - RACK_T, y, zc, RACK_ROD_R, STEEL, 10)

        x = xb

def display():
    glClearColor(0.95, 0.95, 0.96, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # จัดมุมกล้องแบบภาพนิ่งตรงหน้าชั้นวาง
    glTranslatef(-1.05, -0.24, -2.5)
    glRotatef(20.0, 1, 0, 0)
    glRotatef(-25.0, 0, 1, 0)

    # เรียกใช้ฟังก์ชันเดี่ยวได้ทันที
    front_shoe_racks()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(950, 700)
    glutCreateWindow(b"Encapsulated Shoe Racks Preview")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (950 / 700), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()