#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone 3D object viewer. Drag with left mouse to rotate; wheel zooms; R resets; Esc quits."""
import math, sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
SHADE_TOP, SHADE_BOT = 1.0, 0.55
SHADE_S, SHADE_N = 0.92, 0.78
SHADE_E, SHADE_W = 0.85, 0.70
LIGHT_DIR=(0.35,0.80,0.45)
LIGHT_N=tuple(v/math.sqrt(sum(c*c for c in LIGHT_DIR)) for v in LIGHT_DIR)
STEEL=(0.78,0.80,0.82)

def box(x0, y0, z0, x1, y1, z1, c, solid=False, flat=False):  # สร้างสูตรวาดกล่อง รับมุมกล่อง 2 มุม สี และตัวเลือกอีก 2 อย่าง
    """กล่องสี่เหลี่ยม (มุมต่ำ -> มุมสูง) solid=True คือให้เดินชนได้"""
    if solid:  # ถ้ากล่องนี้ต้องเดินชนได้
        COLLIDERS.append((min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)))  # จดพื้นที่ของกล่อง (มองจากด้านบน) ลงสมุดสิ่งกีดขวาง
    r, g, b = c  # แยกสีเป็น 3 ค่า แดง เขียว น้ำเงิน
    k = (1, 1, 1, 1, 1, 1) if flat else (SHADE_TOP, SHADE_BOT, SHADE_N, SHADE_S, SHADE_W, SHADE_E)  # เลือกค่าความสว่างของแต่ละด้าน (ถ้า flat ทุกด้านเท่ากัน)
    glBegin(GL_QUADS)  # บอกการ์ดจอว่าจะวาดแผ่นสี่เหลี่ยมต่อไปนี้
    glColor3f(r * k[0], g * k[0], b * k[0])   # top  # เลือกสีของด้านบน
    glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)  # ระบุ 4 มุมของด้านบน
    glColor3f(r * k[1], g * k[1], b * k[1])   # bottom  # เลือกสีของด้านล่าง
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)  # ระบุ 4 มุมของด้านล่าง
    glColor3f(r * k[2], g * k[2], b * k[2])   # north (-z)  # เลือกสีของด้านเหนือ
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x0, y1, z0)  # ระบุ 4 มุมของด้านเหนือ
    glColor3f(r * k[3], g * k[3], b * k[3])   # south (+z)  # เลือกสีของด้านใต้
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)  # ระบุ 4 มุมของด้านใต้
    glColor3f(r * k[4], g * k[4], b * k[4])   # west (-x)  # เลือกสีของด้านตะวันตก
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)  # ระบุ 4 มุมของด้านตะวันตก
    glColor3f(r * k[5], g * k[5], b * k[5])   # east (+x)  # เลือกสีของด้านตะวันออก
    glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)  # ระบุ 4 มุมของด้านตะวันออก
    glEnd()  # บอกการ์ดจอว่าวาดเสร็จแล้ว


def cylinder(cx, y0, cz, r, h, c, seg=18, solid=False):  # สร้างสูตรวาดทรงกระบอก (ตำแหน่ง รัศมี ความสูง สี จำนวนด้าน)
    if solid:  # ถ้าต้องเดินชนได้
        COLLIDERS.append((cx - r, cz - r, cx + r, cz + r))  # จดพื้นที่สี่เหลี่ยมที่ครอบทรงกระบอกลงสมุดสิ่งกีดขวาง
    rr, gg, bb = c  # แยกสีเป็น 3 ค่า
    glBegin(GL_QUADS)  # เริ่มวาดแผ่นสี่เหลี่ยม (ผนังข้างของกระบอก)
    for i in range(seg):  # วนซ้ำทีละด้านของกระบอก
        a0 = 2 * math.pi * i / seg  # มุมเริ่มต้นของแผ่นนี้ (หน่วยเรเดียน)
        a1 = 2 * math.pi * (i + 1) / seg  # มุมสิ้นสุดของแผ่นนี้
        s = 0.75 + 0.25 * math.cos(a0 - 0.8)  # คำนวณความสว่าง ให้ด้านหนึ่งสว่างกว่าอีกด้าน
        glColor3f(rr * s, gg * s, bb * s)  # เลือกสีของแผ่นนี้
        glVertex3f(cx + r * math.cos(a0), y0, cz + r * math.sin(a0))  # มุมล่างซ้ายของแผ่น
        glVertex3f(cx + r * math.cos(a1), y0, cz + r * math.sin(a1))  # มุมล่างขวาของแผ่น
        glVertex3f(cx + r * math.cos(a1), y0 + h, cz + r * math.sin(a1))  # มุมบนขวาของแผ่น
        glVertex3f(cx + r * math.cos(a0), y0 + h, cz + r * math.sin(a0))  # มุมบนซ้ายของแผ่น
    glEnd()  # วาดผนังข้างเสร็จ
    glColor3f(rr, gg, bb)  # เลือกสีเต็มสำหรับฝาด้านบน
    glBegin(GL_TRIANGLE_FAN)  # เริ่มวาดแบบพัด (สามเหลี่ยมหลายอันที่มีจุดร่วมกันตรงกลาง)
    glVertex3f(cx, y0 + h, cz)  # จุดกึ่งกลางฝา
    for i in range(seg + 1):  # วนรอบขอบฝาให้ครบ 1 รอบ
        a = 2 * math.pi * i / seg  # มุมของจุดบนขอบ
        glVertex3f(cx + r * math.cos(a), y0 + h, cz + r * math.sin(a))  # จุดบนขอบฝา
    glEnd()  # วาดฝาเสร็จ


def ball(cx, cy, cz, r, c, seg=12, rings=8):  # สร้างสูตรวาดลูกบอลทรงกลม
    """ทรงกลม (ใส่เฉดสีหลอกให้ดูมีมิติ)"""
    glBegin(GL_QUADS)  # เริ่มวาดแผ่นสี่เหลี่ยมเล็ก ๆ ปะเป็นลูกบอล
    for k in range(rings):  # วนทีละวงจากหัวถึงท้ายลูกบอล
        t0, t1 = math.pi * k / rings, math.pi * (k + 1) / rings  # มุมของขอบบนและขอบล่างของวงนี้
        for i in range(seg):  # วนทีละชิ้นรอบลูกบอล
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg  # มุมเริ่มและมุมจบของชิ้นนี้
            tm, am = (t0 + t1) / 2, (a0 + a1) / 2  # มุมตรงกลางของแผ่น
            nx, ny, nz = math.sin(tm) * math.cos(am), math.cos(tm), math.sin(tm) * math.sin(am)  # ทิศที่ผิวตรงนี้หันไป
            sh = 0.55 + 0.45 * max(0.0, 0.35 * nx + 0.8 * ny + 0.45 * nz)  # ความสว่าง: หันเข้าหาแสงสมมติยิ่งสว่าง ต่ำสุด 55%
            glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)  # เลือกสีแผ่นนี้
            for (t, a) in ((t0, a0), (t0, a1), (t1, a1), (t1, a0)):  # วนทั้ง 4 มุมของแผ่น
                glVertex3f(cx + r * math.sin(t) * math.cos(a), cy + r * math.cos(t),  # ตำแหน่งแกน x และแกน y ของมุม
                           cz + r * math.sin(t) * math.sin(a))  # ตำแหน่งแกน z ของมุม
    glEnd()  # วาดลูกบอลเสร็จ


def tube(p0, p1, r, c, seg=8):  # สร้างสูตรวาดท่อกลมจากจุด p0 ไปจุด p1 (ท่อเอียงได้)
    """ท่อกลมระหว่างจุด p0 -> p1 (ใช้ทำขา C-stand ที่โค้งงอ)"""
    d = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])  # ทิศจากจุดเริ่มไปจุดจบ
    L = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) or 1.0  # ความยาวท่อ (กันไม่ให้เป็นศูนย์)
    d = (d[0] / L, d[1] / L, d[2] / L)  # ทำทิศให้มีความยาวเป็น 1
    ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)  # เลือกแกนอ้างอิงที่ไม่ขนานกับท่อ
    u = (d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0])  # หาแกนที่ตั้งฉากกับท่อ (ด้วย cross product)
    ul = math.sqrt(u[0] ** 2 + u[1] ** 2 + u[2] ** 2) or 1.0  # ความยาวของแกนนั้น
    u = (u[0] / ul, u[1] / ul, u[2] / ul)  # ทำแกนให้มีความยาวเป็น 1
    v = (d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0])  # หาแกนที่สองที่ตั้งฉากกับทั้งท่อและแกนแรก
    glBegin(GL_QUADS)  # เริ่มวาดแผ่นสี่เหลี่ยมรอบท่อ
    for i in range(seg):  # วนทีละด้านของท่อ
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg  # มุมเริ่มและมุมจบของด้านนี้
        am = (a0 + a1) / 2  # มุมตรงกลางของด้านนี้
        n = (math.cos(am) * u[0] + math.sin(am) * v[0], math.cos(am) * u[1] + math.sin(am) * v[1],  # ทิศที่ผิวด้านนี้หันไป (ส่วน x และ y)
             math.cos(am) * u[2] + math.sin(am) * v[2])  # ทิศที่ผิวด้านนี้หันไป (ส่วน z)
        sh = 0.55 + 0.45 * max(0.0, n[0] * LIGHT_DIR[0] + n[1] * LIGHT_DIR[1] + n[2] * LIGHT_DIR[2])  # ความสว่าง ยิ่งหันเข้าหาแสงยิ่งสว่าง
        glColor3f(c[0] * sh, c[1] * sh, c[2] * sh)  # เลือกสีของด้านนี้
        for (a, p) in ((a0, p0), (a1, p0), (a1, p1), (a0, p1)):  # วนทั้ง 4 มุมของแผ่น (สองมุมที่ปลายเริ่ม สองมุมที่ปลายจบ)
            ca, sa = math.cos(a), math.sin(a)  # ค่า cos และ sin ของมุมนี้
            glVertex3f(p[0] + r * (ca * u[0] + sa * v[0]),  # ตำแหน่งแกน x ของมุม
                       p[1] + r * (ca * u[1] + sa * v[1]),  # ตำแหน่งแกน y ของมุม
                       p[2] + r * (ca * u[2] + sa * v[2]))  # ตำแหน่งแกน z ของมุม
    glEnd()  # วาดท่อเสร็จ


def c_stand(cx, cz, hub_h, yaw0=0):  # สร้างสูตรวาดขาตั้งไฟ C-stand (ตำแหน่ง ความสูงของฮับขา มุมเริ่มของขา)
    """C-stand ตามสเปคในรูป: สูง 150 cm เสา Ø35 -> Ø30 -> Ø25 mm ปลอกยางดำ
    ขา Ø25 mm 3 ขา ห่าง 120° กางรวม ~74 cm  ขาโค้งลงถึงพื้น  hub_h = ความสูงของฮับขา"""
    steel, dark = STEEL, (0.06, 0.06, 0.07)  # ตั้งชื่อสีเหล็กกับสีดำที่ใช้ซ้ำ
    cylinder(cx, hub_h - 0.05, cz, 0.0175, 1.035 - (hub_h - 0.05), steel, 12)   # Ø35 mm  # เสาท่อนล่างสุด (ใหญ่สุด) จากฮับขึ้นไปถึง 1.035 เมตร
    cylinder(cx, 1.035, cz, 0.0195, 0.123, dark, 12)                             # ปลอกยางดำ  # ปลอกยางสีดำคาดตรงกลางเสา
    cylinder(cx, 1.158, cz, 0.0150, 0.162, steel, 12)                            # Ø30 mm  # เสาท่อนกลาง (เล็กลง)
    cylinder(cx, 1.320, cz, 0.0125, 0.140, steel, 12)                            # Ø25 mm  # เสาท่อนบน (เล็กสุด)
    cylinder(cx, 1.460, cz, 0.0080, 0.040, steel, 10)                            # หัวสตัดบนสุด (รวมสูง 1.50 m)  # หัวเสาเล็ก ๆ บนสุด รวมความสูง 1.50 เมตร
    cylinder(cx, 1.150, cz, 0.0185, 0.015, steel, 12)                            # ปลอกต่อท่อ  # ข้อต่อระหว่างท่อนล่างกับท่อนกลาง
    cylinder(cx, 1.312, cz, 0.0165, 0.015, steel, 12)  # ข้อต่อระหว่างท่อนกลางกับท่อนบน
    cylinder(cx, hub_h - 0.04, cz, 0.030, 0.08, steel, 12)                       # ฮับขา  # ตัวฮับ (จุดที่ขาทั้ง 3 ข้างต่อเข้ามา)
    cylinder(cx + 0.035, hub_h - 0.015, cz, 0.012, 0.035, dark, 8)               # น็อบล็อก  # ลูกบิดสีดำสำหรับขันล็อก
    for k in range(3):  # วนทำขา 3 ขา
        a = math.radians(yaw0 + 120 * k)  # มุมของขาแต่ละขา ห่างกัน 120 องศา แล้วแปลงเป็นเรเดียน
        ux, uz = math.cos(a), -math.sin(a)  # ทิศที่ขานี้ยื่นออกไปบนพื้น
        p0 = (cx, hub_h, cz)  # จุดเริ่มของขา: ที่ฮับ
        p1 = (cx + 0.28 * ux, hub_h, cz + 0.28 * uz)           # แขนแนวนอน 28 cm  # จุดปลายแขนแนวนอน (ห่างจากฮับ 28 ซม.)
        p2 = (cx + 0.43 * ux, 0.02, cz + 0.43 * uz)            # ปลายขาลาดลงพื้น (รัศมี 43 cm)  # จุดปลายขาที่ลาดลงถึงพื้น (ห่างจากฮับ 43 ซม.)
        tube(p0, p1, 0.0125, steel, 8)  # วาดท่อแนวนอนจากฮับไปจุดข้อศอก
        ball(p1[0], p1[1], p1[2], 0.0125, steel, 8, 6)  # วาดลูกบอลที่ข้อศอกเพื่อปิดรอยต่อให้ดูเรียบ
        tube(p1, p2, 0.0125, steel, 8)  # วาดท่อลาดลงจากข้อศอกไปถึงพื้น
        cylinder(p2[0], 0.0, p2[2], 0.0145, 0.04, dark, 8)     # ยางรองขา  # วาดยางสีดำรองปลายขา

def draw_object():
    # Original C-stand function, centered for the standalone viewer.
    glPushMatrix(); glTranslatef(0,0.0,0)
    c_stand(0.0, 0.0, 0.18, 0)
    glPopMatrix()

# --- Standalone rotating viewer (same interaction style as the iMac example) ---
class View:
    yaw, pitch, dist = 0.85, 0.22, 2.3
    last = None

def display():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    target_y = 0.72
    gluLookAt(View.dist*math.cos(View.pitch)*math.cos(View.yaw),
              target_y + View.dist*math.sin(View.pitch),
              View.dist*math.cos(View.pitch)*math.sin(View.yaw),
              0, target_y, 0, 0, 1, 0)
    glPushMatrix()
    glTranslatef(0, 0, 0)
    draw_object()
    glPopMatrix()
    glutSwapBuffers()

def reshape(w,h):
    glViewport(0,0,w,max(h,1)); glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(45, w/max(h,1), 0.03, 100); glMatrixMode(GL_MODELVIEW)

def mouse(button,state,x,y):
    if button == GLUT_LEFT_BUTTON: View.last=(x,y) if state==GLUT_DOWN else None
    elif state==GLUT_DOWN and button in (3,4):
        View.dist=min(max(View.dist*(0.9 if button==3 else 1.1),0.25),15); glutPostRedisplay()

def motion(x,y):
    if View.last is None: return
    lx,ly=View.last; View.yaw+=(x-lx)*0.01
    View.pitch=min(max(View.pitch+(y-ly)*0.01,-1.45),1.45); View.last=(x,y); glutPostRedisplay()

def keyboard(key,x,y):
    if key in (b'\x1b',b'q'): sys.exit(0)
    if key in (b'r',b'R'): View.yaw,View.pitch,View.dist=0.85,0.22,2.3; glutPostRedisplay()

def main():
    glutInit(sys.argv); glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(900,650); glutCreateWindow(b"C-Stand")
    glEnable(GL_DEPTH_TEST); glutDisplayFunc(display); glutReshapeFunc(reshape)
    glutMouseFunc(mouse); glutMotionFunc(motion); glutKeyboardFunc(keyboard); glutMainLoop()

if __name__=='__main__': main()
