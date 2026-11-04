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

def _load_shell():
    """ดึงแปลนห้องจาก studio_room_shell.py (PyOpenGL ล้วน)"""
    try:
        import numpy  # noqa  (ไฟล์ shell ใช้สร้างลายพื้น/ผนัง)
    except ImportError:
        sys.exit("ต้องติดตั้ง numpy ก่อน:  pip install numpy")
    try:
        return importlib.import_module("studio_room_shell")
    except ModuleNotFoundError:
        _fetch("studio_room_shell"); importlib.invalidate_caches()
        return importlib.import_module("studio_room_shell")

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAWS = ("https://raw.githubusercontent.com/YMmail/Midtrem/add-studio-walk-pyopengl/",   # branch นี้ก่อน (เป็นเวอร์ชันล่าสุด ไม่มี pygame)
         "https://raw.githubusercontent.com/YMmail/Midtrem/main/")
_CACHE = os.path.join(_HERE, "_models")
os.makedirs(_CACHE, exist_ok=True)
for _p in (_HERE, os.getcwd(), _CACHE):
    if _p not in sys.path: sys.path.insert(0, _p)

def _fetch(name):
    """ถ้าไม่มีไฟล์โมเดลในเครื่อง ให้โหลดจาก GitHub มาเก็บใน _models/"""
    import urllib.request, urllib.parse
    dst = os.path.join(_CACHE, name + ".py")
    if not os.path.exists(dst):
        err = None
        for base in _RAWS:                       # ลอง main ก่อน แล้วค่อย branch งานนี้
            try:
                urllib.request.urlretrieve(base + urllib.parse.quote(name + ".py"), dst); return dst
            except Exception as e:
                err = e
        raise err
    return dst

def _imp(name):
    """import โมเดล ถ้าไม่มีไฟล์ (หรือไฟล์นั้นต้องใช้ไฟล์อื่นที่ขาด) จะโหลดจาก GitHub มาให้อัตโนมัติ"""
    want = name
    for _ in range(8):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError as e:
            want = e.name or name
            if want.split(".")[0] in ("OpenGL", "numpy", "PIL"):
                raise SystemExit("ขาดไลบรารี %s  ->  pip install %s" % (want, "PyOpenGL PyOpenGL_accelerate numpy pillow"))
            try:
                _fetch(want); importlib.invalidate_caches()
            except Exception as e2:
                raise SystemExit("[import ไม่ได้] %s (ต้องใช้ %s) -> %s\nวางไฟล์ %s.py ไว้โฟลเดอร์เดียวกับไฟล์นี้" % (name, want, e2, want))
        except Exception as e:
            raise SystemExit("[import พัง] %s -> %s: %s" % (name, type(e).__name__, e))
    raise SystemExit("[import วนไม่จบ] " + name)

_imp("studio_sign")
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
sign_m         = _imp("studio_sign")            # ป้ายหน้าห้อง (แทน front_sign เดิม)
shoe_m         = _imp("front_shoe_racks")
whiteboard_m   = _imp("studio_whiteboard")
details_m      = _imp("studio_wall_details")
rolls_m        = _imp("studio_paper_rolls")      # ม้วนฉากกระดาษใต้กระดาน (ชุดเดียวแทน paper_roll*, 12.x, 13)

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
BARSTOOL_SEAT_H = 0.90      # ความสูงที่นั่งเก้าอี้เคาน์เตอร์บาร์ (เมตร) ~ระดับเอว  (เดิม 0.625)

LAYOUT = [
    ("aircon",   (1.75,)), ("aircon", (6.00,)),
    ("softbox",  (4.35, 0.55, 8)), ("softbox", (6.65, 0.95, -25)),
    ("dome",     (3.25, 0.62)), ("dome", (5.65, 0.95)),
    ("cabinet",  ()), ("paperrolls", ()), ("cabitems", ()), ("cstands", ()),
    ("rows",     ()), ("blacktable", ()), ("tv", (4.05, BLACK_TABLE_Z)),
    ("jbl",      (4.95, 1.50, 0)),
    ("chair",    (2.37, BLACK_TABLE_Z - 0.58, -1)),
    ("barstool", (5.85, 8.55, 0)), ("barstool", (5.30, 8.55, -6)),
    ("stoolstack", ()), ("pac", (W - 0.31, 0.85)), ("cornerrolls", ()),
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
def draw_aircon(cx):
    aircon_m.aircon(cx, 0.55, H - 0.40)
    details_m.aircon_brackets(cx, H)

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

def d_rows():
    n, depth, length, per = 4, .6, 1.8, 3
    zs = BLACK_TABLE_Z + 23.5 * INCH / 2
    x0 = (W - per * length) / 2
    rng = random.Random(7)
    for r in range(n):
        zr = zs + ROW_GAP + r * (depth + ROW_GAP)
        for i in range(per):
            table_m.training_table(x0 + i * length, zr, length, depth)

        COLL.append((x0, zr, x0 + per * length, zr + depth))
        for i in range(per):
            if rng.random() < .55:
                sx = x0 + i * length + rng.uniform(.50, 1.30)
                sz = zr + rng.uniform(.34, .50)
                stool_m.stool(sx, 0.0, sz, dots=True)

def d_blacktable():
    cx, cz, ty = 2.62, BLACK_TABLE_Z, 29.5 * INCH
    btable_m.black_table(cx, cz)

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

    COLL.append((cx - 49 * INCH / 2, pz - .105, cx + 49 * INCH / 2, pz))

def d_cstands():
    for i in range(7):
        cstand_m.c_stand(.95, .62 + i * .10, .18 + .04 * i)

    COLL.append((.88, .55, 1.02, 1.30))

def d_stoolstack():
    for (x, z) in office_chair_m.stool_stack_positions(D):
        for k in range(5):
            stool_m.stool(x, k * .14, z, dots=True)

        COLL.append((x - .26, z - .26, x + .26, z + .26))

def d_softbox(x, z, yaw):
    softbox_m.softbox_rect(x, z, yaw)

    COLL.append((x - .5, z - .5, x + .5, z + .5))

def d_dome(x, z):
    dome_m.dome_para(x, z, ribs=True); COLL.append((x - .38, z - .38, x + .38, z + .38))

def d_jbl(x, z, yaw):
    jbl_m.jbl_speaker(x, z, yaw); COLL.append((x - .163, z - .184, x + .163, z + .184))

def d_chair(x, z, f):
    office_chair_m.office_chair(x, z, f, COLL)


def d_barstool(x, z, yaw):
    barstool_m.bar_stool(x, z, yaw, seat_h=BARSTOOL_SEAT_H); COLL.append((x - .27, z - .27, x + .27, z + .27))

def d_pac(x, z):
    pac_m.portable_ac(x, z); COLL.append((x - .14, z - .225, x + .14, z + .225))

def d_kat(x, z, yaw):
    kat_m.kat_vr(kat_m.LOGO_TEX, x, z, yaw); COLL.append((x - .6, z - .6, x + .6, z + .6))

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

def d_paperrolls():
    # ชุดม้วนกระดาษ 5 ม้วนใต้กระดานฝั่งตะวันตก (ติดผนัง x=0, กึ่งกลางชุดที่ z=4.325 -> ม้วนอยู่ z 2.78-5.86 เหมือนเดิม)
    if hasattr(rolls_m, "paper_roll_set"):
        rolls_m.paper_roll_set(0.0, 4.325, 0.0, colliders=COLL)

def d_cornerrolls():
    # ม้วนฉากมุมตะวันออก-หน้าต่าง (ตำแหน่งเดียวกับ corner_stuff ของ Final) ใช้ paper_roll จาก studio_paper_rolls
    COLL.append((5.64, 0.0, 7.16, 0.40))
    rolls_m.paper_roll(5.70, 7.06, 0.070, 0.085, 0.070, (0.95, 0.95, 0.94))
    rolls_m.paper_roll(5.70, 7.06, 0.065, 0.225, 0.065, (0.95, 0.55, 0.65), tail=0.40)
    rolls_m.paper_roll(5.74, 7.10, 0.180, 0.155, 0.060, (0.74, 0.57, 0.36))

def d_cabitems():
    for m_ in items_m:
        _place(m_)

FAN_CX, FAN_CY, FAN_HALF = W / 2 - 0.175, 2.31, 0.15       # ตำแหน่งพัดลมในช่องแสงเหนือประตู

def cut_fan_hole(S):
    """เจาะกระจกช่องแสงให้พัดลมทะลุ (ตัดกระจกทั้งสองฝั่งผนังตรงตำแหน่งพัดลมออก)"""
    out = []
    for q in S.GLASS_QUADS:
        zs = {round(pt[2], 4) for pt in q}
        if len(zs) == 1 and zs.pop() in (round(S.D, 4), round(S.FZ, 4)):
            xs, ys, z = [pt[0] for pt in q], [pt[1] for pt in q], q[0][2]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            cx, cy, h = FAN_CX, FAN_CY, FAN_HALF
            if x0 <= cx - h and x1 >= cx + h and y0 <= cy - h and y1 >= cy + h:
                for (a, b, c, d) in ((x0, cx - h, y0, y1), (cx + h, x1, y0, y1),
                                     (cx - h, cx + h, y0, cy - h), (cx - h, cx + h, cy + h, y1)):
                    out.append([(a, c, z), (b, c, z), (b, d, z), (a, d, z)])
                continue
        out.append(q)
    S.GLASS_QUADS[:] = out

def d_fan():
    fm = fan_m
    if not hasattr(fm, "exhaust_fan"): return
    fm.FAN_CY = FAN_CY
    cx = FAN_CX
    keep = fm.cable
    fm.cable = lambda *a, **k: None            # ตัวสายไฟของโมเดลอยู่ในกรอบพิกัดเก่า -> วาดเองด้านล่างให้ติดผนังฝั่งห้อง
    glPushMatrix(); glTranslatef(0, 0, FZW)    # โมเดลวาดผนังหนา z -0.12..0 -> ย้ายมาอยู่ในผนังหน้าห้อง
    try:
        fm.exhaust_fan(cx); fm.fan_blades(0.0, cx)
    finally:
        glPopMatrix(); fm.cable = keep
    # สายไฟ: เกาะกำแพงด้านในห้อง (ค่าเดียวกับโมเดล แต่ z อิง D = ผนังห้อง)
    sg = 1.0 if cx < W / 2 else -1.0
    xc, zf = W / 2 - sg * 0.010, D - 0.067
    keep([(cx + sg * 0.11, FAN_CY + 0.13, D - 0.012), (xc, FAN_CY + 0.13, zf), (xc, 2.605, zf),
          (xc, 2.64, D - 0.018), (xc, 2.65, D - 0.015)], r=0.004, col=(0.05, 0.05, 0.06), seg=6)

SIGN_TX = [None]

def d_sign():
    if SIGN_TX[0] is None: return
    x = shell_m.DOOR_B + shell_m.FRAME_HALF + shell_m.SIGN_GAP + sign_m.SIGN_W / 2     # ชิดกรอบประตูด้านขวา
    sign_m.room_sign(x, shell_m.SIGN_Y0, FZW, SIGN_TX[0])

def d_shoes():
    if not hasattr(shoe_m, "front_shoe_racks"): return
    glPushMatrix(); glTranslatef(BASE_X0, 0, FZW)
    shoe_m.front_shoe_racks()
    glPopMatrix()
    COLL.append((BASE_X0, FZW, BASE_X0 + 2.10, FZW + .15))

DISPATCH = {
    "aircon": draw_aircon, "softbox": d_softbox,
    "dome": d_dome, "cabinet": d_cabinet, "paperrolls": d_paperrolls, "cabitems": d_cabitems, "cornerrolls": d_cornerrolls, "fan": d_fan, "sign": d_sign, "shoes": d_shoes, "cstands": d_cstands,
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
        SIGN_TX[0] = sign_m.prepare_sign()           # สร้างเท็กซ์เจอร์ป้ายก่อนเข้า display list
    except Exception as e:
        print('[ป้าย] สร้างไม่ได้:', e)
    lst = glGenLists(1)
    glNewList(lst, GL_COMPILE)
    S.room_shell(tex); S.ceiling_fixtures(); S.window_wall(); S.door_wall(); S.east_wall()   # แปลนห้อง
    S.front_shell(ter, fwall); S.front_door(); S.front_strip_windows(); S.wall_glass()       # ทางเดินหน้าห้อง
    S.front_baseboard(); S.front_window_wall()
    cut_fan_hole(S)                                                                           # เจาะกระจกให้พัดลม
    whiteboard_m.whiteboard()                                                                  # ไวท์บอร์ด (import)
    details_m.wall_wires(S.W, S.D, S.H); details_m.light_switches(S.D)                         # สายไฟ + สวิตช์ (import)
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

# ---------- HUD (ข้อความด้วย GLUT bitmap) ----------
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
