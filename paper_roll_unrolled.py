import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ---------------------------------------------------------------- helpers
def gquad(pts, cols):
    """วาดสี่เหลี่ยม 1 แผ่น pts = 4 จุด, cols = สี 4 จุด"""
    glBegin(GL_QUADS)
    for p, c in zip(pts, cols):
        glColor3f(*c)
        glVertex3f(*p)
    glEnd()


def xcyl(x0, x1, cy, cz, r, color, n=32):
    """ทรงกระบอกนอนตามแนว X (ไม่มีฝาปิด) จาก x0 ถึง x1 ศูนย์กลางที่ (cy, cz) รัศมี r
    ลงเฉดสีตามทิศผิวที่หันเข้าหาแสง"""
    glBegin(GL_QUADS)
    for i in range(n):
        a, b = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        m = (a + b) / 2
        sh = 0.60 + 0.40 * max(0.0, math.sin(m) * 0.8 + math.cos(m) * 0.4)  # ผิวหันขึ้น/หน้า สว่างกว่า
        glColor3f(color[0] * sh, color[1] * sh, color[2] * sh)
        glVertex3f(x0, cy + r * math.sin(a), cz + r * math.cos(a))
        glVertex3f(x1, cy + r * math.sin(a), cz + r * math.cos(a))
        glVertex3f(x1, cy + r * math.sin(b), cz + r * math.cos(b))
        glVertex3f(x0, cy + r * math.sin(b), cz + r * math.cos(b))
    glEnd()


def xring(x, cy, cz, ra, rb, color, n=32):
    """วงแหวนแบนที่ระนาบ x (หันหน้าไปทางแกน X) รัศมีใน ra รัศมีนอก rb  (ra = 0 คือวงกลมเต็ม)"""
    glColor3f(*color)
    glBegin(GL_QUADS)
    for i in range(n):
        a, b = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        glVertex3f(x, cy + ra * math.sin(a), cz + ra * math.cos(a))
        glVertex3f(x, cy + rb * math.sin(a), cz + rb * math.cos(a))
        glVertex3f(x, cy + rb * math.sin(b), cz + rb * math.cos(b))
        glVertex3f(x, cy + ra * math.sin(b), cz + ra * math.cos(b))
    glEnd()


# ---------------------------------------------------------------- Paper Roll Unrolled
def paper_roll_unrolled(x0, x1, cy, cz, r, paper, tail=0.3):  # สร้างสูตรวาด "ม้วนฉากกระดาษ" แบบคลี่ออกมาเล็กน้อย tail = ความยาวกระดาษที่คลี่บนพื้น (เมตร)
    """ม้วนฉากกระดาษถ่ายภาพ (seamless paper) วางนอนตามแนว X จาก x0 ถึง x1 รัศมี r สีกระดาษ paper
    มีแกนกระดาษแข็งโผล่ออกหัวท้าย  ปลายม้วนมีขอบกระดาษเป็นเส้นเงา  หน้าตัดเห็นชั้นกระดาษเป็นวงๆ
    tail > 0 = มีแผ่นกระดาษคลี่ออกมาบนพื้นด้านหน้า (+Z) ยาว tail เมตร ปลายแผ่นงอขึ้นเล็กน้อย"""
    core_r, core_ext = 0.038, 0.035  # รัศมีแกนกระดาษแข็ง 3.8 ซม. และความยาวแกนที่โผล่พ้นหัวท้าย 3.5 ซม.
    card, hole = (0.72, 0.58, 0.40), (0.06, 0.05, 0.05)  # สีแกนกระดาษแข็ง และสีรูกลางแกน
    xcyl(x0, x1, cy, cz, r, paper)  # ตัวม้วนกระดาษ
    a_e = 1.15  # มุมตำแหน่งขอบปลายกระดาษที่พันอยู่รอบม้วน
    glBegin(GL_QUADS)  # เส้นขอบกระดาษ
    glColor3f(paper[0] * 0.70, paper[1] * 0.70, paper[2] * 0.70)  # สีกระดาษมืดลง 30% ให้เห็นเป็นเส้นเงา
    for (aa, bb) in ((a_e, a_e + 0.05),):
        for (x, a) in ((x0, aa), (x1, aa), (x1, bb), (x0, bb)):
            glVertex3f(x, cy + (r + 0.0006) * math.sin(a), cz + (r + 0.0006) * math.cos(a))  # ลอยเหนือผิว 0.6 มม. กันภาพกระพริบ
    glEnd()
    nr = 7  # จำนวนวงของหน้าตัดปลายม้วน
    for x, k in ((x0, 0.82), (x1, 0.94)):  # หน้าตัดสองหัวม้วน (ซ้ายมืดกว่า)
        for j in range(nr):
            ra = core_r + (r - core_r) * j / nr  # รัศมีขอบในของวงนี้
            rb = core_r + (r - core_r) * (j + 1) / nr  # รัศมีขอบนอกของวงนี้
            s = k * (1.0 if j % 2 == 0 else 0.90)  # วงคี่มืดลง 10% ให้เป็นริ้วสลับชั้นกระดาษ
            xring(x + (-0.0004 if x == x0 else 0.0004), cy, cz, ra, rb, (paper[0] * s, paper[1] * s, paper[2] * s))
    xcyl(x0 - core_ext, x1 + core_ext, cy, cz, core_r, card, 20)  # แกนกระดาษแข็ง ยาวกว่าม้วนสองด้าน
    for x, k in ((x0 - core_ext, 0.78), (x1 + core_ext, 0.90)):  # หน้าตัดปลายแกน
        xring(x + (-0.0004 if x < x0 else 0.0004), cy, cz, 0.031, core_r, (card[0] * k, card[1] * k, card[2] * k), 20)  # ขอบหนาของแกน
        xring(x + (0.0006 if x < x0 else -0.0006), cy, cz, 0.0, 0.031, hole, 20)  # รูกลางแกน
    if tail > 0:  # กระดาษคลี่ออกมาบนพื้น
        y = 0.003  # สูงจากพื้น 3 มม. กันทับกับพื้นแล้วภาพกระพริบ
        zs, ze = cz, cz + tail  # จุดเริ่ม (ที่ม้วน) และจุดปลายแผ่น
        gquad([(x0, y, zs), (x1, y, zs), (x1, y, ze - 0.05), (x0, y, ze - 0.05)],  # แผ่นแบนบนพื้น (เว้นปลาย 5 ซม. ไว้ทำส่วนงอ)
              [(paper[0] * 0.97, paper[1] * 0.97, paper[2] * 0.97)] * 4)
        gquad([(x0, y, ze - 0.05), (x1, y, ze - 0.05), (x1, y + 0.014, ze), (x0, y + 0.014, ze)],  # ปลายกระดาษงอขึ้น 1.4 ซม.
              [(paper[0] * 0.90, paper[1] * 0.90, paper[2] * 0.90)] * 4)


# ---------------------------------------------------------------- viewer
# ใช้เฉพาะตอนรันไฟล์นี้ตรงๆ เพื่อดูตัวอย่าง (ไฟล์หลักของเพื่อน import แค่ paper_roll_unrolled ก็พอ)
cam = {"yaw": 35.0, "pitch": 28.0, "dist": 2.6, "drag": None}


def display():
    glClearColor(0.45, 0.50, 0.58, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    yaw, pitch, dist = math.radians(cam["yaw"]), math.radians(cam["pitch"]), cam["dist"]
    ex = dist * math.cos(pitch) * math.sin(yaw)
    ey = dist * math.sin(pitch)
    ez = dist * math.cos(pitch) * math.cos(yaw)
    gluLookAt(ex, ey, ez, 0, 0.09, 0.15, 0, 1, 0)
    paper_roll_unrolled(-0.675, 0.675, 0.09, 0.0, 0.09, (0.93, 0.93, 0.91), tail=0.3)  # วางม้วนฉาก ยาว 1.35 ม. รัศมี 9 ซม. นอนบนพื้น (cy = r)
    glutSwapBuffers()


def reshape(w, h):
    h = max(h, 1)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, w / h, 0.02, 50.0)
    glMatrixMode(GL_MODELVIEW)


def zoom(f):
    cam["dist"] = max(0.3, min(15.0, cam["dist"] * f))
    glutPostRedisplay()


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        cam["drag"] = (x, y) if state == GLUT_DOWN else None
    elif state == GLUT_DOWN and button in (3, 4):  # ล้อเมาส์ (freeglut)
        zoom(0.9 if button == 3 else 1.1)


def motion(x, y):
    if cam["drag"]:
        lx, ly = cam["drag"]
        cam["yaw"] -= (x - lx) * 0.4
        cam["pitch"] = max(-89, min(89, cam["pitch"] + (y - ly) * 0.4))
        cam["drag"] = (x, y)
        glutPostRedisplay()


def key(k, x, y):
    if k in (b'q', b'Q', b'\x1b'):
        sys.exit(0)
    elif k in (b'3', b'+', b'='):
        zoom(0.9)
    elif k in (b'4', b'-'):
        zoom(1.1)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 600)
    glutCreateWindow(b"Paper Roll Unrolled")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(key)
    glutMainLoop()


if __name__ == "__main__":
    main()
