from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

INCH = 0.0254
BLACK_TABLE_Z = 0.0
COLLIDERS = []

def tv_stand(cx=0.0, pz=0.0):
    """ทีวี 49 x 28 inch ขอบล่างสูง 38 inch ยอดสูง 66 inch
    หน้าจอหันเข้าห้อง (+Z) เสาขาตั้งอยู่ด้านหลังจอ ชั้นวางยื่นมาด้านหน้า"""
    
    def _gquad(vertices, colors):
        glBegin(GL_QUADS)
        for v, c in zip(vertices, colors):
            glColor3f(*c)
            glVertex3f(*v)
        glEnd()

    def _cbox(x_center, y_bottom, z_center, w, h, d, color, solid=False):
        """วาดกล่อง 3D จากจุดกึ่งกลางแกน X, ขอบล่างแกน Y, จุดกึ่งกลางแกน Z"""
        x0, x1 = x_center - w / 2, x_center + w / 2
        y0, y1 = y_bottom, y_bottom + h
        z0, z1 = z_center - d / 2, z_center + d / 2

        # ปรับความสว่างแต่ละด้านเพื่อมิติแสงเงา
        shading = {
            'top': 1.15,
            'front': 1.0,
            'back': 0.75,
            'left': 0.85,
            'right': 0.90,
            'bottom': 0.60
        }

        def apply_col(factor):
            glColor3f(min(1.0, color[0] * factor),
                      min(1.0, color[1] * factor),
                      min(1.0, color[2] * factor))

        glBegin(GL_QUADS)
        # ด้านหน้า (+Z)
        apply_col(shading['front'])
        glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1)
        glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)

        # ด้านหลัง (-Z)
        apply_col(shading['back'])
        glVertex3f(x1, y0, z0); glVertex3f(x0, y0, z0)
        glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0)

        # ด้านบน (+Y)
        apply_col(shading['top'])
        glVertex3f(x0, y1, z1); glVertex3f(x1, y1, z1)
        glVertex3f(x1, y1, z0); glVertex3f(x0, y1, z0)

        # ด้านล่าง (-Y)
        apply_col(shading['bottom'])
        glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0)
        glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)

        # ด้านขวา (+X)
        apply_col(shading['right'])
        glVertex3f(x1, y0, z1); glVertex3f(x1, y0, z0)
        glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1)

        # ด้านซ้าย (-X)
        apply_col(shading['left'])
        glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1)
        glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
        glEnd()

    ty = 38 * INCH
    tw, th = 49 * INCH, 28 * INCH
    dark = (0.10, 0.10, 0.11)

    # 1. ฐานขาตั้ง
    _cbox(cx, 0, pz - 0.05, 23 * INCH, 0.04, 0.55, dark, solid=True)

    # 2. เสาขาตั้ง (หลังจอ) สูง 66 นิ้ว
    _cbox(cx, 0.04, pz - 0.085, 0.05, 66 * INCH - 0.04, 0.04, (0.14, 0.14, 0.15))

    # 3. ชั้นวางของยื่นหน้าเสา
    _cbox(cx, 0.60, pz + 0.03, 10 * INCH, 0.012, 0.22, dark)

    # 4. ตัวกรอบทีวี
    _cbox(cx, ty, pz - 0.035, tw, th, 0.05, dark)

    # 5. กล่องนูนฝาหลังทีวี (ยึดกับเสา)
    _cbox(cx, ty + 0.06, pz - 0.075, 0.60, 0.30, 0.03, (0.18, 0.18, 0.19))

    # 6. ผิวหน้าจอขอบดำ (ด้าน +Z)
    _cbox(cx, ty + 0.02, pz - 0.010, tw - 0.03, th - 0.04, 0.004, (0.015, 0.02, 0.03))

    # 7. แผ่นเงาสะท้อนกระจกหน้าจอ
    _gquad([(cx - tw / 2 + 0.015, ty + 0.02, pz - 0.0075),
            (cx + tw / 2 - 0.015, ty + 0.02, pz - 0.0075),
            (cx + tw / 2 - 0.015, ty + th - 0.02, pz - 0.0075),
            (cx - tw / 2 + 0.015, ty + th - 0.02, pz - 0.0075)],
           [(0.01, 0.01, 0.015), (0.01, 0.01, 0.015),
            (0.06, 0.07, 0.10), (0.03, 0.035, 0.05)])

    COLLIDERS.append((cx - tw / 2, pz - 0.105, cx + tw / 2, pz))

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # ตั้งกล้องมองเฉียงด้านหน้าเล็กน้อยเพื่อให้เห็นทั้งขาตั้ง จอ และมิติความหนา
    glTranslatef(0.0, -0.9, -2.8)
    glRotatef(12.0, 1, 0, 0)
    glRotatef(-25.0, 0, 1, 0)

    # วาดทีวีและขาตั้งไว้ที่พิกัดกลาง (0, 0)
    tv_stand(cx=0.0, pz=BLACK_TABLE_Z)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 750)
    glutCreateWindow(b"Static TV Stand Preview")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (1000 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()