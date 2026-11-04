from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# สีกำหนดมาตรฐาน
WOOD = (0.76, 0.60, 0.42)
WHITE = (0.92, 0.92, 0.94)

def training_table(x0, z0, length=1.8, depth=0.6):
    """โต๊ะพับ 1.8 x 0.6 m สูง 0.75 m (29.5 inch) มีแผงขาวเจาะรูด้านใต้โต๊ะ"""

    def _box(xa, ya, za, xb, yb, zb, color):
        """วาดกล่อง 3 มิติจากพิกัดมุมตรงข้าม (xa, ya, za) ถึง (xb, yb, zb)"""
        x_min, x_max = min(xa, xb), max(xa, xb)
        y_min, y_max = min(ya, yb), max(ya, yb)
        z_min, z_max = min(za, zb), max(za, zb)

        shading = {
            'top': 1.10,
            'front': 1.00,
            'back': 0.75,
            'left': 0.85,
            'right': 0.90,
            'bottom': 0.60
        }

        def set_col(factor):
            glColor3f(min(1.0, color[0] * factor),
                      min(1.0, color[1] * factor),
                      min(1.0, color[2] * factor))

        glBegin(GL_QUADS)
        # ด้านบน (+Y)
        set_col(shading['top'])
        glVertex3f(x_min, y_max, z_max); glVertex3f(x_max, y_max, z_max)
        glVertex3f(x_max, y_max, z_min); glVertex3f(x_min, y_max, z_min)

        # ด้านล่าง (-Y)
        set_col(shading['bottom'])
        glVertex3f(x_min, y_min, z_min); glVertex3f(x_max, y_min, z_min)
        glVertex3f(x_max, y_min, z_max); glVertex3f(x_min, y_min, z_max)

        # ด้านหน้า (+Z)
        set_col(shading['front'])
        glVertex3f(x_min, y_min, z_max); glVertex3f(x_max, y_min, z_max)
        glVertex3f(x_max, y_max, z_max); glVertex3f(x_min, y_max, z_max)

        # ด้านหลัง (-Z)
        set_col(shading['back'])
        glVertex3f(x_max, y_min, z_min); glVertex3f(x_min, y_min, z_min)
        glVertex3f(x_min, y_max, z_min); glVertex3f(x_max, y_max, z_min)

        # ด้านซ้าย (-X)
        set_col(shading['left'])
        glVertex3f(x_min, y_min, z_min); glVertex3f(x_min, y_min, z_max)
        glVertex3f(x_min, y_max, z_max); glVertex3f(x_min, y_max, z_min)

        # ด้านขวา (+X)
        set_col(shading['right'])
        glVertex3f(x_max, y_min, z_max); glVertex3f(x_max, y_min, z_min)
        glVertex3f(x_max, y_max, z_min); glVertex3f(x_max, y_max, z_max)
        glEnd()

    def _perforated_panel(xa, ya, za, xb, yb, zb, base_color):
        """วาดแผงกั้นพร้อมจุดรูพรุนสีเข้มเลียนแบบแผงเหล็กเจาะรู"""
        _box(xa, ya, za, xb, yb, zb, base_color)
        
        # จุดรูพรุนบนแผ่นระนาบ (+Z และ -Z)
        dot_color = (0.25, 0.25, 0.27)
        glPointSize(2.0)
        glColor3f(*dot_color)

        glBegin(GL_POINTS)
        x_start, x_end = min(xa, xb) + 0.04, max(xa, xb) - 0.04
        y_start, y_end = min(ya, yb) + 0.03, max(ya, yb) - 0.03
        z_front = max(za, zb) + 0.001
        z_back = min(za, zb) - 0.001

        curr_y = y_start
        while curr_y <= y_end:
            curr_x = x_start
            while curr_x <= x_end:
                glVertex3f(curr_x, curr_y, z_front)
                glVertex3f(curr_x, curr_y, z_back)
                curr_x += 0.04
            curr_y += 0.04
        glEnd()

    # 1. แผ่นหน้าโต๊ะลายไม้ หนา 3 ซม. สูง 0.72 - 0.75 m
    _box(x0, 0.72, z0, x0 + length, 0.75, z0 + depth, WOOD)

    # 2. ขาโต๊ะและคานเท้า 2 ฝั่ง (ซ้ายและขวา)
    for x in (x0 + 0.12, x0 + length - 0.12):
        _box(x - 0.02, 0.06, z0 + 0.04, x + 0.02, 0.72, z0 + 0.08, WHITE)
        _box(x - 0.02, 0.06, z0 + depth - 0.08, x + 0.02, 0.72, z0 + depth - 0.04, WHITE)
        _box(x - 0.02, 0.03, z0 + 0.03, x + 0.02, 0.07, z0 + depth - 0.03, WHITE)

    # 3. แผงขาวเจาะรูใต้โต๊ะ
    _perforated_panel(x0 + 0.05, 0.36, z0 + 0.03, x0 + length - 0.05, 0.69, z0 + 0.05, (0.88, 0.88, 0.90))

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # จัดกล้องมองมุมเฉียงจากด้านหน้าบน
    glTranslatef(0.0, -0.4, -2.6)
    glRotatef(20.0, 1, 0, 0)
    glRotatef(-35.0, 0, 1, 0)

    # จัดให้กึ่งกลางโต๊ะอยู่ที่จุดศูนย์กลาง (X=0, Z=0)
    training_table(x0=-0.9, z0=-0.3, length=1.8, depth=0.6)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 750)
    glutCreateWindow(b"Static Training Table Preview")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (1000 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()