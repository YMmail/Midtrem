#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Studio Room Walkthrough (PyOpenGL + GLUT เท่านั้น)
ขนาดห้อง/ตำแหน่งของทุกชิ้นอ่านมาจาก Final Code 209_219_258_260_270 (ไม่ได้ import ไฟล์นั้น)
ชิ้นงานดึงจากไฟล์ย่อยเดิมด้วย import
W A S D เดิน | Shift วิ่ง | เมาส์/ลูกศร หมุนกล้อง | R กลับจุดเริ่ม | F สลับห้อง/ทางเดิน | H ซ่อน HUD | Esc ออก"""
import math, os, sys, random, importlib, re, inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ============ 1) import ชิ้นงานจากไฟล์เก่า ============
# ---------- โมเดลสำรอง (ใช้เมื่อหาไฟล์เก่าไม่เจอ) สเกลจาก Studio.pdf ----------
def _cyl(x, y, z, r, h, c, axis='y'):
    glColor3f(*c); glPushMatrix(); glTranslatef(x, y, z)
    if axis == 'x': glRotatef(90, 0, 1, 0)
    elif axis == 'z': pass
    else: glRotatef(-90, 1, 0, 0)
    q = gluNewQuadric(); gluCylinder(q, r, r, h, 16, 1)
    gluDisk(q, 0, r, 16, 1); glTranslatef(0, 0, h); gluDisk(q, 0, r, 16, 1)
    gluDeleteQuadric(q); glPopMatrix()

def _yaw(x, z, yaw):
    glPushMatrix(); glTranslatef(x, 0, z); glRotatef(yaw, 0, 1, 0)

class _FB:
    """โมเดลง่ายๆ แทนไฟล์เก่า"""
    LOGO_TEX = None
    my_logo = None
    def aircon(self, cx, y, z):
        box(cx - .60, y - .14, z - .445, cx + .60, y + .14, z + .445, (.93, .91, .84))
    def paper_roll(self, a, b, cy, xo, r, col):
        _cyl(a, cy, xo, r, b - a, col, 'x')
    def paper_roll_unrolled(self, z0, z1, cy, xo, r, col, off=0.0):
        _cyl(xo, cy, z0, r, z1 - z0, col, 'z')
    def training_table(self, x0, zr, length, depth):
        box(x0, .70, zr, x0 + length, .73, zr + depth, WOOD)
        box(x0, .28, zr + depth - .03, x0 + length, .66, zr + depth, (.90, .90, .92))
        for xx in (x0 + .06, x0 + length - .06):
            box(xx - .015, 0, zr + .05, xx + .015, .70, zr + depth - .05, (.82, .82, .85))
    def stool(self, x, y, z, dots=False):
        _cyl(x, y + .42, z, .17, .03, (.93, .93, .93))
        for dx, dz in ((.10, .10), (-.10, .10), (.10, -.10), (-.10, -.10)):
            _cyl(x + dx, y, z + dz, .012, .42, (.7, .7, .72))
    def bar_stool(self, x, z, yaw):
        _cyl(x, .70, z, .18, .04, (.95, .95, .95))
        for dx, dz in ((.10, .10), (-.10, .10), (.10, -.10), (-.10, -.10)):
            _cyl(x + dx, 0, z + dz, .014, .70, (.75, .58, .38))
    def mic(self, x, y, z, yaw):
        _yaw(x, z, yaw); _cyl(0, y + .02, 0, .02, .25, (.10, .10, .11), 'x'); glPopMatrix()
    def keyboard(self, x, y, z):
        box(x - .14, y, z - .055, x + .14, y + .012, z + .055, (.92, .92, .92))
    def magic_mouse(self, x, y, z, yaw):
        _yaw(x, z, yaw); box(-.028, y, -.056, .028, y + .012, .056, (.95, .95, .95)); glPopMatrix()
    def imac(self, x, ty, z, w, h, logo=None):
        box(x - w / 2, ty + .12, z - .01, x + w / 2, ty + .12 + h, z + .01, (.92, .92, .92))
        box(x - w / 2 + .01, ty + .13, z + .01, x + w / 2 - .01, ty + .11 + h, z + .012, (.05, .05, .07))
        box(x - .10, ty, z - .09, x + .10, ty + .012, z + .09, (.9, .9, .9))
        box(x - .02, ty, z - .015, x + .02, ty + .12, z, (.9, .9, .9))
    def portable_ac(self, x, z):
        box(x - .14, 0, z - .225, x + .14, .85, z + .225, (.93, .91, .85))
    def softbox_rect(self, x, z, yaw):
        _yaw(x, z, yaw)
        _cyl(0, 0, 0, .02, 1.55, (.2, .2, .2)); box(-.30, 1.30, -.20, .30, 1.90, .20, (.05, .05, .06))
        glPopMatrix()
    def dome_para(self, x, z, ribs=True):
        glColor3f(.06, .06, .07); glPushMatrix(); glTranslatef(x, 0, z); glScalef(.30, .69, .30)
        q = gluNewQuadric(); gluSphere(q, 1.0, 20, 10); gluDeleteQuadric(q); glPopMatrix()
    def tv_stand(self, cx, pz):
        box(cx - .62, 1.42 - .71, pz - .08, cx + .62, 1.42, pz - .04, (.03, .03, .04))
        box(cx - .04, 0, pz - .08, cx + .04, .72, pz - .04, (.15, .15, .17))
        box(cx - .30, 0, pz - .45, cx + .30, .03, pz - .04, (.12, .12, .13))
    def black_table(self, cx, cz):
        box(cx - 30 * INCH, 0, cz - 23.5 * INCH / 2, cx + 30 * INCH, 29.5 * INCH, cz + 23.5 * INCH / 2, (.04, .04, .05))
    def jbl_speaker(self, x, z, yaw):
        _yaw(x, z, yaw); box(-.163, 0, -.184, .163, .75, .184, (.07, .07, .08)); box(-.12, .45, .184, .12, .55, .19, (.95, .45, .1)); glPopMatrix()
    def c_stand(self, x, z, lean=0.0):
        _cyl(x, 0, z, .018, 1.9, (.78, .80, .82))
        for dx in (-.25, .25): box(x + dx - .01, 0, z - .01, x + dx + .01, .03, z + .01, (.78, .80, .82))
    def office_chair(self, x, z, f, coll=None):
        _cyl(x, 0, z, .24, .04, (.1, .1, .1)); _cyl(x, .04, z, .025, .40, (.2, .2, .2))
        box(x - .23, .44, z - .235, x + .23, .53, z + .235, (.45, .22, .12))
        bz = z + f * .22
        box(x - .23, .53, bz - .04, x + .23, .99, bz + .04, (.25, .15, .10))
        if coll is not None: coll.append((x - .3, z - .3, x + .3, z + .3))
    def stool_stack_positions(self, D):
        return [(0.35, D - 0.45), (0.35, D - 1.05)]
    def kat_vr(self, tex, x, z, yaw):
        _cyl(x, 0, z, .55, .12, (.08, .08, .10)); _cyl(x, 1.0, z, .45, .03, (.2, .2, .22))
        for k in range(4):
            a = k * math.pi / 2 + math.radians(yaw); _cyl(x + .45 * math.cos(a), .12, z + .45 * math.sin(a), .02, .9, (.2, .2, .22))

def _load_shell():
    """ดึงแปลนห้อง studio_room_shell.py (ไฟล์นั้น import pygame ไว้ -> ใส่ตัวหลอกชั่วคราว ไม่ใช้ pygame จริง)"""
    import types
    try:
        import numpy  # noqa  (ไฟล์ shell ใช้สร้างลายพื้น/ผนัง)
    except ImportError:
        sys.exit("ต้องติดตั้ง numpy ก่อน:  pip install numpy")
    fake = types.ModuleType("pygame"); fake.locals = types.ModuleType("pygame.locals")
    old = {k: sys.modules.get(k) for k in ("pygame", "pygame.locals")}
    sys.modules["pygame"], sys.modules["pygame.locals"] = fake, fake.locals
    try:
        try:
            return importlib.import_module("studio_room_shell")
        except ModuleNotFoundError:
            _fetch("studio_room_shell"); importlib.invalidate_caches()
            return importlib.import_module("studio_room_shell")
    finally:
        for k, v in old.items():
            if v is None: sys.modules.pop(k, None)
            else: sys.modules[k] = v

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAW = "https://raw.githubusercontent.com/YMmail/Midtrem/main/"
_CACHE = os.path.join(_HERE, "_models")
os.makedirs(_CACHE, exist_ok=True)
for _p in (_HERE, os.getcwd(), _CACHE):
    if _p not in sys.path: sys.path.insert(0, _p)

def _fetch(name):
    """ถ้าไม่มีไฟล์โมเดลในเครื่อง ให้โหลดจาก GitHub มาเก็บใน _models/"""
    import urllib.request, urllib.parse
    dst = os.path.join(_CACHE, name + ".py")
    if not os.path.exists(dst):
        urllib.request.urlretrieve(_RAW + urllib.parse.quote(name + ".py"), dst)
    return dst

def _imp(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        try:
            _fetch(name); importlib.invalidate_caches()
            return importlib.import_module(name)
        except Exception as e:
            print("[ใช้โมเดลสำรอง]", name, "->", e)
    except Exception as e:
        print("[import พัง]", name, "->", type(e).__name__, e)
    return _FB()

shell_m        = _load_shell()          # แปลนห้อง (ผนัง หน้าต่าง ประตู ทางเดิน) จาก studio_room_shell.py
office_chair_m = _imp("office_chair")
aircon_m       = _imp("aircon")
stool_m        = _imp("stool")
barstool_m     = _imp("bar_stool")
mic_m          = _imp("mic")
keyboard_m     = _imp("keyboard")
mouse_m        = _imp("magic_mouse")
imac_m         = _imp("IMAC_FInal")
pac_m          = _imp("Portable_New")
softbox_m      = _imp("softbox_rect_New")
dome_m         = _imp("dome_para_New")
tv_m           = _imp("tv_stand")
table_m        = _imp("training_table")
btable_m       = _imp("black_table")
jbl_m          = _imp("jbl_speaker_New_Final")
cstand_m       = _imp("11_C_Stand")
kat_m          = _imp("14_KAT_VR_PyOpenGL_only")
cab_m          = _imp("01_cabinet_Ninew")
ITEM_NAMES     = ("02_yellow_box", "03_blue_box", "04_white_box", "05_documents", "06_cardboard_box",
                  "07_black_bag", "08_orange_cloth_Box", "09_green_cloth_Box", "10_paper_on_shelf")
items_m        = [_imp(n) for n in ITEM_NAMES]
fan_m          = _imp("fan")
sign_m         = _imp("front_sign")
shoe_m         = _imp("front_shoe_racks")
# ม้วนกระดาษ (paper_roll*, 12.x, 13) ยังไม่ดึง ตามที่สั่ง

# ============ 2) ขนาดห้อง (เมตร) X=ซ้าย->ขวา Y=สูง Z=หน้าต่าง->ประตู ============
INCH = 0.0254
W, D, H = 305 * INCH, 355 * INCH, 130 * INCH
EYE_MAX = 1.65                       # ไม่เกิน 165 ซม.
EYE_HEIGHT, CROUCH_EYE = 1.60, 1.00
PLAYER_R, WALK, RUN = 0.16, 1.5, 3.2
START_POS = (W / 2, 8.4)             # หน้าประตู เหมือน Final Code
START_YAW = 0.0                      # หันไปทางหน้าต่าง (-Z)
CABINET_H = 1.90
BLACK_TABLE_Z = 1.50
ROW_GAP = 0.65
BEAM_HANG = 0.60
DESK_SHIFT = (-0.125, 0.05)
W, D, H = shell_m.W, shell_m.D, shell_m.H
DOOR_A, DOOR_B, DOOR_OPEN_H = shell_m.DOOR_A, shell_m.DOOR_B, shell_m.DOOR_OPEN_H
STRIP_X, STRIP_Y0, STRIP_Y1 = shell_m.STRIP_X, shell_m.STRIP_Y0, shell_m.STRIP_Y1
FZW, BASE_X0 = shell_m.FZ, shell_m.BASE_X0
FRONT_START, FRONT_YAW = shell_m.FRONT_START, shell_m.FRONT_YAW

WALL_GREY, BLACK = (0.53, 0.55, 0.60), (0.04, 0.04, 0.05)
WOOD, WHITE, CURTAIN, STEEL = (0.86, 0.72, 0.52), (0.92, 0.92, 0.92), (0.27, 0.29, 0.35), (0.78, 0.80, 0.82)
COLL = []                            # กล่องชน (x0,z0,x1,z1)

# ============ 3) ตารางข้อมูลวัตถุ (วนลูปอ่านแล้วแมปลง 3D) ============
# (รหัส, พารามิเตอร์)  รหัสแปลงเป็นฟังก์ชันวาดใน DISPATCH
LAYOUT = [
    ("aircon",   (1.75,)), ("aircon", (6.00,)),
    ("softbox",  (4.35, 0.55, 8)), ("softbox", (6.65, 0.95, -25)),
    ("dome",     (3.25, 0.62)), ("dome", (5.65, 0.95)),
    ("cabinet",  ()), ("cabitems", ()), ("cstands", ()),
    ("rows",     ()), ("blacktable", ()), ("tv", (4.05, BLACK_TABLE_Z)),
    ("jbl",      (4.95, 1.50, 0)),
    ("chair",    (2.37, BLACK_TABLE_Z - 0.58, -1)),
    ("barstool", (5.85, 8.55, 0)), ("barstool", (5.30, 8.55, -6)),
    ("stoolstack", ()), ("pac", (W - 0.31, 0.85)),
    ("fan", ()), ("sign", ()), ("shoes", ()),
    ("kat",      (W - 0.75, D - 0.75, 225)),
]

# ============ 4) ฟังก์ชันวาดพื้นฐาน ============
SH = (1.0, 0.55, 0.80, 0.90, 0.72, 0.93)

def box(x0, y0, z0, x1, y1, z1, c, solid=False):
    if solid:
        COLL.append((min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)))
    r, g, b = c
    f = [((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)),
         ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
         ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)),
         ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)),
         ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)),
         ((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0))]
    glBegin(GL_QUADS)
    for k, pts in zip(SH, f):
        glColor3f(r * k, g * k, b * k)
        for p in pts:
            glVertex3f(*p)
    glEnd()

def cbox(cx, y0, cz, sx, sy, sz, c, solid=False):
    box(cx - sx / 2, y0, cz - sz / 2, cx + sx / 2, y0 + sy, cz + sz / 2, c, solid)

def quad(pts, c):
    glColor3f(*c)
    glBegin(GL_QUADS)
    for p in pts:
        glVertex3f(*p)
    glEnd()

def wall_pieces(x0, x1, y0, y1, holes):
    ys = sorted({y0, y1} | {v for h in holes for v in (h[2], h[3])})
    out = []
    for ya, yb in zip(ys[:-1], ys[1:]):
        cuts = sorted((h[0], h[1]) for h in holes if h[2] <= ya and h[3] >= yb)
        cur = x0
        for ca, cb in cuts:
            if ca > cur:
                out.append((cur, ca, ya, yb))
            cur = max(cur, cb)
        if cur < x1:
            out.append((cur, x1, ya, yb))
    return out

DOOR_HOLES = [(DOOR_A, DOOR_B, 0.0, DOOR_OPEN_H), (DOOR_A, DOOR_B, DOOR_OPEN_H + 0.05, STRIP_Y1)] \
             + [(a, b, STRIP_Y0, STRIP_Y1) for a, b in STRIP_X]

# ============ 5) โครงห้อง ============
def west_wall():
    z0, z1 = 2.3, 7.1; zm = (z0 + z1) / 2
    y0 = 1.05; y1 = y0 + 47.5 * INCH; yt = y1 + .10
    br, kr = (.20, .11, .08), (.72, .56, .38)
    box(0, y0, z0, .03, y1, z1, (.94, .95, .96))
    box(0, y1, z0 - .04, .09, y1 + .10, z1 + .04, br)
    box(0, y0 - .06, z0 - .04, .12, y0, z1 + .04, br)
    box(.10, y0 - .06, z0 - .04, .12, y0 + .015, z1 + .04, br)
    box(0, y0, z0 - .04, .04, y1, z0, br); box(0, y0, z1, .04, y1, z1 + .04, br)
    box(0, y0, zm - .005, .031, y1, zm + .005, (.7, .7, .7))
    box(0, yt, 4.70, .14, yt + .075, 6.04, kr)
    box(0, yt, 3.26, .14, yt + .075, 4.66, tuple(v * .94 for v in kr))
    box(0, yt, 6.62, .06, yt + .045, 6.95, (.55, .40, .25))
    for z in (z0 + .45, z0 + 1.55, zm, z1 - 1.55, z1 - .45):
        box(0, y0 - .14, z - .02, .05, y0 - .06, z + .02, (.12, .07, .05))

def draw_aircon(cx):
    aircon_m.aircon(cx, 0.55, H - 0.40)
    for dx in (-.6, .6):
        box(cx + dx - .01, H - .15, .87, cx + dx + .01, H, .89, STEEL)

# ============ 6) ตู้เหล็ก ============
def draw_cabinet():
    z0, z1, h = .50, .50 + 1.48, CABINET_H
    st, inn, sh = (.55, .57, .58), (.46, .48, .50), (.62, .64, .66)
    COLL.append((.02, z0, .48, z1))
    box(.02, 0, z0, .045, h, z1, inn); box(.02, 0, z0, .48, h, z0 + .03, st)
    box(.02, 0, z1 - .03, .48, h, z1, st); box(.02, h - .03, z0, .48, h, z1, st)
    box(.02, 0, z0, .48, .06, z1, st); box(.045, .86, z0, .48, .98, z1, st)
    box(.44, h - .06, z0, .48, h, z1, st)
    for y in (.45, 1.28, 1.56):
        box(.045, y, z0 + .03, .46, y + .02, z1 - .03, sh)
    for a in [(.10, .98, z0 + .10, .42, 1.12, z0 + .45, (.95, .82, .18)),
              (.10, .98, z0 + .55, .30, 1.20, z0 + .75, (.20, .35, .70)),
              (.10, .98, z0 + .90, .40, 1.15, z0 + 1.30, (.90, .90, .88)),
              (.10, 1.30, z0 + .15, .40, 1.50, z0 + .60, (.93, .93, .90)),
              (.10, 1.30, z0 + .80, .40, 1.42, z0 + 1.25, (.55, .40, .25)),
              (.10, 1.58, z0 + .20, .42, 1.78, z0 + .80, (.10, .10, .11)),
              (.08, .06, z0 + .08, .44, .40, z0 + .55, (.95, .60, .28)),
              (.08, .06, z0 + .70, .44, .30, z0 + 1.20, (.15, .55, .30)),
              (.10, .47, z0 + .30, .40, .70, z0 + 1.00, (.92, .88, .80))]:
        box(*a)
    box(.04, h, z0 + .04, .44, h + .15, z0 + 1.44, (.92, .92, .94))
    top = h - .06
    return [(.485, z0 + .04, z0 + .76, top - .86, top), (.505, z0 + .40, z0 + 1.12, top - .86, top),
            (.485, z0 + .22, z0 + .94, .06, .86), (.505, z0 + .68, z0 + 1.40, .06, .86)]

def cabinet_glass(panes):
    alu = (.74, .76, .78)
    for px, za, zb, ya, yb in panes:
        for a in [(px - .006, ya, za, px + .006, yb, za + .025), (px - .006, ya, zb - .025, px + .006, yb, zb),
                  (px - .006, ya, za, px + .006, ya + .025, zb), (px - .006, yb - .025, za, px + .006, yb, zb)]:
            box(*a, alu)
    glDepthMask(GL_FALSE); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS); glColor4f(.72, .88, .92, .16)
    for px, za, zb, ya, yb in panes:
        for p in ((px, ya, za), (px, ya, zb), (px, yb, zb), (px, yb, za)):
            glVertex3f(*p)
    glEnd(); glDisable(GL_BLEND); glDepthMask(GL_TRUE)

# ============ 7) ตัวแปลงรหัส -> ฟังก์ชันวาด ============
PANES = []

def ph(m, x0, z0, x1, z1, h, c=(.75, .45, .25)):
    pass

def d_rows():
    n, depth, length, per = 4, .6, 1.8, 3
    zs = BLACK_TABLE_Z + 23.5 * INCH / 2
    x0 = (W - per * length) / 2
    rng = random.Random(7)
    for r in range(n):
        zr = zs + ROW_GAP + r * (depth + ROW_GAP)
        for i in range(per):
            table_m.training_table(x0 + i * length, zr, length, depth)
            ph(table_m, x0 + i * length, zr, x0 + (i + 1) * length, zr + depth, .75, (.80, .70, .55))
        COLL.append((x0, zr, x0 + per * length, zr + depth))
        for i in range(per):
            if rng.random() < .55:
                sx = x0 + i * length + rng.uniform(.50, 1.30)
                sz = zr + rng.uniform(.34, .50)
                stool_m.stool(sx, 0.0, sz, dots=True)

def d_blacktable():
    cx, cz, ty = 2.62, BLACK_TABLE_Z, 29.5 * INCH
    btable_m.black_table(cx, cz)
    ph(btable_m, cx - 30 * INCH, cz - 23.5 * INCH / 2, cx + 30 * INCH, cz + 23.5 * INCH / 2, ty, (.08, .08, .09))
    COLL.append((cx - 30 * INCH, cz - 23.5 * INCH / 2, cx + 30 * INCH, cz + 23.5 * INCH / 2))
    glPushMatrix(); glTranslatef(*(DESK_SHIFT[0], 0, DESK_SHIFT[1]))
    ix, iz = 3.00, 1.58
    glPushMatrix(); glTranslatef(ix, 0, iz); glRotatef(180, 0, 1, 0); glTranslatef(-ix, 0, -iz)
    imac_m.imac(ix, ty, iz, 25.5 * INCH, 16 * INCH, logo=imac_m.my_logo); glPopMatrix()
    kx, kz = 2.85, 1.37
    glPushMatrix(); glTranslatef(kx, 0, kz); glRotatef(180, 0, 1, 0); glTranslatef(-kx, 0, -kz)
    keyboard_m.keyboard(kx, ty, kz); glPopMatrix()
    mouse_m.magic_mouse(2.65, ty, 1.40, 180)
    mic_m.mic(2.47, ty + .031, 1.245, -57); mic_m.mic(2.26, ty + .031, 1.300, -57)
    glPopMatrix()

def d_tv(cx, pz):
    tv_m.tv_stand(cx, pz)
    ph(tv_m, cx - 49 * INCH / 2, pz - .105, cx + 49 * INCH / 2, pz, 1.50, (.05, .05, .06))
    COLL.append((cx - 49 * INCH / 2, pz - .105, cx + 49 * INCH / 2, pz))

def d_cstands():
    for i in range(7):
        cstand_m.c_stand(.95, .62 + i * .10, .18 + .04 * i)
    ph(cstand_m, .88, .55, 1.02, 1.30, 1.80, (.3, .3, .32))
    COLL.append((.88, .55, 1.02, 1.30))

def d_stoolstack():
    for (x, z) in office_chair_m.stool_stack_positions(D):
        for k in range(5):
            stool_m.stool(x, k * .14, z, dots=True)
        ph(stool_m, x - .26, z - .26, x + .26, z + .26, .70, (.9, .5, .6))
        COLL.append((x - .26, z - .26, x + .26, z + .26))

def d_softbox(x, z, yaw):
    softbox_m.softbox_rect(x, z, yaw)
    ph(softbox_m, x - .4, z - .4, x + .4, z + .4, 1.9, (.9, .9, .9))
    COLL.append((x - .5, z - .5, x + .5, z + .5))

def d_dome(x, z):
    dome_m.dome_para(x, z, ribs=True); ph(dome_m, x - .38, z - .38, x + .38, z + .38, 2.0, (.85, .85, .85)); COLL.append((x - .38, z - .38, x + .38, z + .38))

def d_jbl(x, z, yaw):
    jbl_m.jbl_speaker(x, z, yaw); ph(jbl_m, x - .163, z - .184, x + .163, z + .184, .55, (.1, .1, .1)); COLL.append((x - .163, z - .184, x + .163, z + .184))

def d_chair(x, z, f):
    office_chair_m.office_chair(x, z, f, COLL)
    ph(office_chair_m, x - .3, z - .3, x + .3, z + .3, .95, (.15, .15, .17))

def d_barstool(x, z, yaw):
    barstool_m.bar_stool(x, z, yaw); ph(barstool_m, x - .27, z - .27, x + .27, z + .27, .75, (.2, .2, .2)); COLL.append((x - .27, z - .27, x + .27, z + .27))

def d_pac(x, z):
    pac_m.portable_ac(x, z); ph(pac_m, x - .14, z - .225, x + .14, z + .225, .85, (.9, .9, .92)); COLL.append((x - .14, z - .225, x + .14, z + .225))

def d_kat(x, z, yaw):
    kat_m.kat_vr(kat_m.LOGO_TEX, x, z, yaw); ph(kat_m, x - .6, z - .6, x + .6, z + .6, 2.2, (.1, .1, .15)); COLL.append((x - .6, z - .6, x + .6, z + .6))

_TR = re.compile(r"glTranslatef\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)")

def _place(mod):
    """ไฟล์ 01-10 วาดแบบมีออฟเซ็ตสำหรับหน้าต่างดูโมเดล -> หักออกให้ได้พิกัดโลกจริง"""
    if not hasattr(mod, "draw_object"):
        return
    t = _TR.search(inspect.getsource(mod.draw_object))
    glPushMatrix()
    if t: glTranslatef(-float(t.group(1)), -float(t.group(2)), -float(t.group(3)))
    mod.draw_object()
    glPopMatrix()

def d_cabinet():
    _place(cab_m)
    COLL.append((.02, .50, .48, 1.98))

def d_cabitems():
    for m_ in items_m:
        _place(m_)

def d_fan():
    fm = fan_m
    if not hasattr(fm, "exhaust_fan"): return
    fm.FAN_CY = 2.31                          # ตำแหน่งความสูง (ขนาดใช้ตามโมเดล)
    cx = W / 2 - 0.175
    glPushMatrix(); glTranslatef(0, 0, FZW)   # โมเดลวาดผนังหนา z -0.12..0 -> ย้ายมาอยู่ในผนังหน้าห้อง
    fm.exhaust_fan(cx); fm.fan_blades(0.0, cx)
    glPopMatrix()

def d_sign():
    sm = sign_m
    if not hasattr(sm, "front_sign"): return
    sm.DOOR_B, sm.FZ = DOOR_B, FZW            # ตำแหน่งวางที่ขอบประตู (ขนาดป้ายใช้ตามโมเดล)
    sm.SIGN_Y1 = STRIP_Y0 - 0.65; sm.SIGN_Y0 = sm.SIGN_Y1 - sm.SIGN_H
    sm.front_sign()

def d_shoes():
    if not hasattr(shoe_m, "front_shoe_racks"): return
    glPushMatrix(); glTranslatef(BASE_X0, 0, FZW)
    shoe_m.front_shoe_racks()
    glPopMatrix()
    COLL.append((BASE_X0, FZW, BASE_X0 + 2.10, FZW + .15))

DISPATCH = {
    "aircon": draw_aircon, "softbox": d_softbox,
    "dome": d_dome, "cabinet": d_cabinet, "cabitems": d_cabitems, "fan": d_fan, "sign": d_sign, "shoes": d_shoes, "cstands": d_cstands,
    "rows": d_rows, "blacktable": d_blacktable, "tv": d_tv, "jbl": d_jbl, "chair": d_chair,
    "barstool": d_barstool, "stoolstack": d_stoolstack, "pac": d_pac,
    "kat": d_kat,
}

SCENE = [0]

def build_scene():
    S = shell_m
    COLL.clear(); S.COLLIDERS.clear(); S.GLASS_QUADS.clear()
    tex = (S.upload_texture(S.tex_floor()), S.upload_texture(S.tex_wall()), S.upload_texture(S.tex_ceiling()))
    ter, fwall = S.upload_texture(S.tex_terrazzo()), S.upload_texture(S.tex_front_wall())
    try:
        if hasattr(sign_m, "generate_sign_texture"):
            sign_m.SIGN_TEX[0] = sign_m.generate_sign_texture()
    except Exception as e:
        print('[ป้าย] สร้างเท็กซ์เจอร์ไม่ได้:', e)
    lst = glGenLists(1)
    glNewList(lst, GL_COMPILE)
    S.room_shell(tex); S.ceiling_fixtures(); S.window_wall(); S.door_wall(); S.east_wall()   # แปลนห้อง
    S.front_shell(ter, fwall); S.front_door(); S.front_strip_windows(); S.wall_glass()       # ทางเดินหน้าห้อง
    S.front_baseboard(); S.front_window_wall()
    west_wall()
    for code, args in LAYOUT:                    # วนอ่านตารางแล้วแมปลง 3D
        try:
            DISPATCH[code](*args)
        except Exception as e:
            print('[วาดไม่ได้]', code, '->', type(e).__name__, e)
    S.draw_window_glass()
    glEndList()
    SCENE[0] = lst

# ============ 8) กล้อง + ชน ============
class Cam:
    x, z = START_POS
    y = EYE_HEIGHT
    yaw, pitch = START_YAW, 0.0

cam = Cam()
keys = set()
state = {"collide": True, "last": 0, "warp": False}

def blocked(x, z):
    r = PLAYER_R
    if state["collide"]:
        if shell_m.blocked(x, z): return True      # ผนัง ประตูบานสวิง ทางเดิน
        for x0, z0, x1, z1 in COLL:
            if x0 - r < x < x1 + r and z0 - r < z < z1 + r:
                return True
        return False
    in_room = r <= x <= W - r and r <= z <= D - r
    in_door = DOOR_A + r <= x <= DOOR_B - r and D - r <= z <= FZW + r
    in_corr = shell_m.CORR_X0 + r <= x <= shell_m.CORR_X1 - r and FZW + r <= z <= shell_m.ZW - r
    return not (in_room or in_door or in_corr)

def move(dx, dz):
    dc = shell_m.door_clearance
    stuck = dc(cam.x, cam.z) < 0
    nx = cam.x + dx
    if not blocked(nx, cam.z) or (stuck and dc(nx, cam.z) >= dc(cam.x, cam.z)): cam.x = nx
    nz = cam.z + dz
    if not blocked(cam.x, nz) or (stuck and dc(cam.x, nz) >= dc(cam.x, cam.z)): cam.z = nz

state.update({"shift": False, "hud": True, "fps": 0.0, "frames": 0, "t0": 0})
arrows = set()
TURN_YAW, TURN_PITCH = math.radians(100), math.radians(70)     # ลูกศรหมุนกล้อง (องศา/วินาที)
SHIFT_KEYS = (112, 113)                                  # freeglut: GLUT_KEY_SHIFT_L / R

def area_name():
    if cam.z > D + 0.12: return "Corridor"
    if cam.z > D - 0.1 and DOOR_A < cam.x < DOOR_B: return "Doorway"
    return "Studio room"

def update():
    now = glutGet(GLUT_ELAPSED_TIME)
    dt = min((now - state["last"]) / 1000.0, 0.05); state["last"] = now
    fx, fz = math.sin(cam.yaw), -math.cos(cam.yaw)
    rx, rz = math.cos(cam.yaw), math.sin(cam.yaw)
    vx = vz = 0.0
    if b'w' in keys: vx += fx; vz += fz
    if b's' in keys: vx -= fx; vz -= fz
    if b'd' in keys: vx += rx; vz += rz
    if b'a' in keys: vx -= rx; vz -= rz
    n = math.hypot(vx, vz)
    if n > 0:
        sp = RUN if state["shift"] else WALK
        move(vx / n * sp * dt, vz / n * sp * dt)
    if GLUT_KEY_LEFT in arrows: cam.yaw -= TURN_YAW * dt
    if GLUT_KEY_RIGHT in arrows: cam.yaw += TURN_YAW * dt
    if GLUT_KEY_UP in arrows: cam.pitch = min(1.4, cam.pitch + TURN_PITCH * dt)
    if GLUT_KEY_DOWN in arrows: cam.pitch = max(-1.4, cam.pitch - TURN_PITCH * dt)
    cam.y = min(EYE_MAX, cam.y)
    shell_m.update_door(cam, dt)              # ประตูกระจกเปิดเอง
    glutPostRedisplay()

# ---------- HUD (ข้อความด้วย GLUT bitmap ไม่ใช้ pygame) ----------
FONT = GLUT_BITMAP_HELVETICA_12
CONTROLS = ["W A S D   Walk", "Shift       Run", "Mouse / Arrows   Look", "R   Back to start",
            "F   Room <-> Corridor", "C   Collision on/off", "H   Show/hide HUD", "Esc   Quit"]

def _text(x, y, t, col=(1, 1, 1)):
    glColor3f(*col); glRasterPos2f(x, y)
    for ch in t: glutBitmapCharacter(FONT, ord(ch))

def draw_hud(w, h):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # จุดเล็งกลางจอ
    glColor4f(1, 1, 1, .8); glBegin(GL_LINES)
    glVertex2f(w / 2 - 6, h / 2); glVertex2f(w / 2 + 6, h / 2); glVertex2f(w / 2, h / 2 - 6); glVertex2f(w / 2, h / 2 + 6)
    glEnd()
    if state["hud"]:
        info = ["STUDIO WALKTHROUGH",
                "Area : %s" % area_name(),
                "Pos  : x %.2f  z %.2f  (m)" % (cam.x, cam.z),
                "Eye  : %.0f cm  (max %.0f)" % (cam.y * 100, EYE_MAX * 100),
                "Yaw  : %.0f deg" % (math.degrees(cam.yaw) % 360),
                "Move : %s" % ("RUN" if state["shift"] else "WALK"),
                "Collision : %s" % ("ON" if state["collide"] else "OFF"),
                "FPS  : %.0f" % state["fps"]]
        glColor4f(0, 0, 0, .50); glBegin(GL_QUADS)
        glVertex2f(8, h - 8); glVertex2f(250, h - 8); glVertex2f(250, h - 14 - 16 * len(info)); glVertex2f(8, h - 14 - 16 * len(info))
        bh = 14 + 16 * len(CONTROLS)
        glVertex2f(8, 8); glVertex2f(210, 8); glVertex2f(210, 8 + bh); glVertex2f(8, 8 + bh)
        glEnd()
        for i, t in enumerate(info):
            _text(16, h - 26 - 16 * i, t, (1, .85, .3) if i == 0 else (1, 1, 1))
        for i, t in enumerate(CONTROLS):
            _text(16, 8 + bh - 22 - 16 * i, t, (.8, .9, 1))
    glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def display():
    glClearColor(.05, .05, .06, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    cp = math.cos(cam.pitch)
    gluLookAt(cam.x, cam.y, cam.z, cam.x + math.sin(cam.yaw) * cp, cam.y + math.sin(cam.pitch),
              cam.z - math.cos(cam.yaw) * cp, 0, 1, 0)
    glCallList(SCENE[0])
    shell_m.draw_auto_door()
    now = glutGet(GLUT_ELAPSED_TIME); state["frames"] += 1
    if now - state["t0"] >= 500:
        state["fps"] = state["frames"] * 1000.0 / max(now - state["t0"], 1); state["frames"] = 0; state["t0"] = now
    draw_hud(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, max(h, 1)); glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(70, w / max(h, 1), .03, 60); glMatrixMode(GL_MODELVIEW)

def quit_app():
    glutSetCursor(GLUT_CURSOR_INHERIT)
    try: glutLeaveMainLoop()                 # freeglut: ออกจากลูปอย่างสะอาด
    except Exception: sys.exit(0)

def _mods():
    try: state["shift"] = bool(glutGetModifiers() & GLUT_ACTIVE_SHIFT)
    except Exception: pass

def go_start():
    cam.x, cam.z = START_POS; cam.yaw, cam.pitch = START_YAW, 0.0

def key_down(k, x, y):
    _mods()
    if k == b'\x1b': quit_app(); return
    kl = k.lower()
    if kl == b'c': state["collide"] = not state["collide"]
    elif kl == b'h': state["hud"] = not state["hud"]
    elif kl == b'r': go_start()
    elif kl == b'f':                                       # สลับห้อง <-> ทางเดิน
        if cam.z > D: go_start()
        else: cam.x, cam.z = FRONT_START; cam.yaw, cam.pitch = FRONT_YAW, 0.0
    else: keys.add(kl)

def key_up(k, x, y):
    _mods(); keys.discard(k.lower())

def special_down(k, x, y):
    if k in SHIFT_KEYS: state["shift"] = True
    else: _mods(); arrows.add(k)

def special_up(k, x, y):
    if k in SHIFT_KEYS: state["shift"] = False
    else: _mods(); arrows.discard(k)

def mouse_move(x, y):
    _mods()
    w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    cx, cy = w // 2, h // 2
    if state["warp"]:
        state["warp"] = False; return
    dx, dy = x - cx, y - cy
    if dx == 0 and dy == 0: return
    cam.yaw += math.radians(dx * .12)
    cam.pitch = max(-1.4, min(1.4, cam.pitch - math.radians(dy * .12)))
    state["warp"] = True; glutWarpPointer(cx, cy)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1280, 720); glutCreateWindow(b"Studio Walkthrough (1 unit = 1 m)")
    glEnable(GL_DEPTH_TEST)
    build_scene()
    state["last"] = state["t0"] = glutGet(GLUT_ELAPSED_TIME)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(display); glutReshapeFunc(reshape); glutIdleFunc(update)
    glutKeyboardFunc(key_down); glutKeyboardUpFunc(key_up)
    glutSpecialFunc(special_down); glutSpecialUpFunc(special_up)
    glutPassiveMotionFunc(mouse_move); glutMotionFunc(mouse_move)
    glutIgnoreKeyRepeat(1)
    glutMainLoop()

if __name__ == "__main__":
    main()
