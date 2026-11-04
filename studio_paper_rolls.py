import math
from OpenGL.GL import (
    GL_QUADS, glBegin, glEnd, glColor3f, glVertex3f,
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef,
)

__all__ = ["PAPER_COLORS", "DEFAULT_COLORS", "to_rgb", "paper_roll", "place_roll", "paper_roll_set"]

LIGHT_DIR = (0.35, 0.80, 0.45)
_LEN = math.sqrt(sum(c * c for c in LIGHT_DIR))
LIGHT_N = tuple(c / _LEN for c in LIGHT_DIR)

PAPER_COLORS = {
    "white": (0.95, 0.95, 0.94),
    "offwhite": (0.93, 0.93, 0.92),
    "green": (0.25, 0.60, 0.30),
    "pink": (0.95, 0.55, 0.65),
    "kraft": (0.74, 0.57, 0.36),
    "black": (0.06, 0.06, 0.07),
    "grey": (0.55, 0.56, 0.58),
    "blue": (0.20, 0.42, 0.78),
    "red": (0.82, 0.18, 0.18),
    "yellow": (0.96, 0.82, 0.25),
    "orange": (0.95, 0.55, 0.20),
}

DEFAULT_COLORS = ("green", "white", "pink", "kraft", "offwhite")

ROLL_LENGTH = 1.36
CORE_R = 0.038
CORE_EXT = 0.035
CORE_HOLE_R = 0.031
CARD = (0.72, 0.58, 0.40)
HOLE = (0.06, 0.05, 0.05)
SEAM_ANGLE = 1.15
SEAM_WIDTH = 0.05
LAYERS = 7
EPS = 0.0004

ROLL_SET = (
    {"x": 0.085, "z": 0.775, "r": 0.070},
    {"x": 0.225, "z": 0.725, "r": 0.065, "tail": 0.40},
    {"x": 0.085, "z": -0.775, "r": 0.070},
    {"x": 0.225, "z": -0.775, "r": 0.065},
    {"x": 0.155, "z": -0.725, "r": 0.060, "lift": 0.12},
)


def to_rgb(color):
    if isinstance(color, str):
        if color.startswith("#"):
            h = color.lstrip("#")
            if len(h) == 3:
                h = "".join(ch * 2 for ch in h)
            return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        key = color.lower()
        if key not in PAPER_COLORS:
            raise ValueError("unknown color '%s' (choose from: %s)" % (color, ", ".join(PAPER_COLORS)))
        return PAPER_COLORS[key]
    rgb = tuple(float(v) for v in color)
    if len(rgb) != 3:
        raise ValueError("color must have 3 values (r, g, b)")
    if max(rgb) > 1.0:
        rgb = tuple(v / 255.0 for v in rgb)
    return rgb


def _scale(col, k):
    return (col[0] * k, col[1] * k, col[2] * k)


def _shade(a):
    return 0.60 + 0.40 * max(0.0, math.sin(a) * LIGHT_N[1] + math.cos(a) * LIGHT_N[2])


def _quad(pts, col):
    glColor3f(*col)
    for p in pts:
        glVertex3f(*p)


def _cylinder_x(x0, x1, cy, cz, r, col, seg=40):
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        for x, a in ((x0, a0), (x1, a0), (x1, a1), (x0, a1)):
            glColor3f(*_scale(col, _shade(a)))
            glVertex3f(x, cy + r * math.sin(a), cz + r * math.cos(a))


def _ring_x(x, cy, cz, r0, r1, col, seg=40):
    glColor3f(*col)
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        for r, a in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
            glVertex3f(x, cy + r * math.sin(a), cz + r * math.cos(a))


def paper_roll(x0, x1, cy, cz, r, paper, tail=0.0):
    glBegin(GL_QUADS)
    _cylinder_x(x0, x1, cy, cz, r, paper)

    rs = r + 0.0006
    a, b = SEAM_ANGLE, SEAM_ANGLE + SEAM_WIDTH
    _quad([(x0, cy + rs * math.sin(a), cz + rs * math.cos(a)),
           (x1, cy + rs * math.sin(a), cz + rs * math.cos(a)),
           (x1, cy + rs * math.sin(b), cz + rs * math.cos(b)),
           (x0, cy + rs * math.sin(b), cz + rs * math.cos(b))], _scale(paper, 0.70))

    for x, side, k in ((x0, -1, 0.82), (x1, 1, 0.94)):
        for j in range(LAYERS):
            ra = CORE_R + (r - CORE_R) * j / LAYERS
            rb = CORE_R + (r - CORE_R) * (j + 1) / LAYERS
            _ring_x(x + side * EPS, cy, cz, ra, rb, _scale(paper, k * (1.0 if j % 2 == 0 else 0.90)))

    cx0, cx1 = x0 - CORE_EXT, x1 + CORE_EXT
    _cylinder_x(cx0, cx1, cy, cz, CORE_R, CARD, 20)
    for x, side, k in ((cx0, -1, 0.78), (cx1, 1, 0.90)):
        _ring_x(x + side * EPS, cy, cz, CORE_HOLE_R, CORE_R, _scale(CARD, k), 20)
        _ring_x(x - side * 1.5 * EPS, cy, cz, 0.0, CORE_HOLE_R, HOLE, 20)

    if tail > 0:
        y = 0.003
        ze = cz + tail
        _quad([(x0, y, cz), (x1, y, cz), (x1, y, ze - 0.05), (x0, y, ze - 0.05)], _scale(paper, 0.97))
        _quad([(x0, y, ze - 0.05), (x1, y, ze - 0.05), (x1, y + 0.014, ze), (x0, y + 0.014, ze)], _scale(paper, 0.90))
    glEnd()


def place_roll(cx, cz, color, along="x", length=ROLL_LENGTH, r=0.07, lift=0.0, tail=0.0):
    col = to_rgb(color)
    cy = r + lift
    half = length / 2
    if along == "x":
        paper_roll(cx - half, cx + half, cy, cz, r, col, tail)
        return (cx - half, cz - r, cx + half, cz + r + tail)
    if along != "z":
        raise ValueError("along must be 'x' or 'z'")
    glPushMatrix()
    glTranslatef(0, 0, cz)
    glRotatef(90, 0, 1, 0)
    paper_roll(-half, half, cy, cx, r, col, tail)
    glPopMatrix()
    return (cx - r, cz - half, cx + r + tail, cz + half)


def _to_world(box, x, z, yaw):
    th = math.radians(yaw)
    cs, sn = math.cos(th), math.sin(th)
    x0, z0, x1, z1 = box
    pts = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
    xs = [x + px * cs + pz * sn for px, pz in pts]
    zs = [z - px * sn + pz * cs for px, pz in pts]
    return (min(xs), min(zs), max(xs), max(zs))


def paper_roll_set(x, z, yaw=0.0, colors=DEFAULT_COLORS, colliders=None):
    if len(colors) != len(ROLL_SET):
        raise ValueError("colors needs %d values (got %d)" % (len(ROLL_SET), len(colors)))
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(yaw, 0, 1, 0)
    boxes = [
        place_roll(spec["x"], spec["z"], color, along="z", r=spec["r"],
                   lift=spec.get("lift", 0.0), tail=spec.get("tail", 0.0))
        for spec, color in zip(ROLL_SET, colors)
    ]
    glPopMatrix()
    world = [_to_world(b, x, z, yaw) for b in boxes]
    if colliders is not None:
        colliders.extend(world)
    return world


def _preview():
    import sys
    from OpenGL.GL import (
        glViewport, glEnable, glClearColor, glMatrixMode, glLoadIdentity, glClear,
        glGenLists, glNewList, glEndList, glCallList,
        GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW, GL_COMPILE,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    )
    from OpenGL.GLU import gluPerspective, gluLookAt
    from OpenGL.GLUT import (
        glutInit, glutInitDisplayMode, glutInitWindowSize, glutCreateWindow, glutDisplayFunc,
        glutReshapeFunc, glutIdleFunc, glutKeyboardFunc, glutKeyboardUpFunc, glutSpecialFunc,
        glutSpecialUpFunc, glutPassiveMotionFunc, glutMotionFunc, glutMainLoop, glutSwapBuffers,
        glutPostRedisplay, glutGet, glutGetModifiers, glutWarpPointer, glutSetCursor,
        glutIgnoreKeyRepeat, glutLeaveMainLoop,
        GLUT_DOUBLE, GLUT_RGB, GLUT_DEPTH, GLUT_ELAPSED_TIME, GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT,
        GLUT_CURSOR_NONE, GLUT_CURSOR_INHERIT, GLUT_ACTIVE_SHIFT,
        GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_KEY_DOWN,
    )

    SW, SH = 1280, 720
    EYE = 1.60
    RADIUS = 0.16
    WALK, RUN = 1.5, 3.2
    START = (1.8, 1.6, -0.80, -0.50)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SW, SH)
    glutCreateWindow(b"Studio Paper Rolls  (1 unit = 1 m)")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.06, 1)

    colliders = []
    scene = glGenLists(1)
    glNewList(scene, GL_COMPILE)
    paper_roll_set(0.0, 0.0, colliders=colliders)
    glEndList()

    cam = list(START)
    keys, arrows = set(), set()
    st = {"shift": False, "warp": False, "last": glutGet(GLUT_ELAPSED_TIME)}

    def blocked(px, pz):
        return any(x0 - RADIUS < px < x1 + RADIUS and z0 - RADIUS < pz < z1 + RADIUS
                   for (x0, z0, x1, z1) in colliders)

    def mods():
        try:
            st["shift"] = bool(glutGetModifiers() & GLUT_ACTIVE_SHIFT)
        except Exception:
            pass

    def reshape(w, h):
        glViewport(0, 0, w, max(h, 1))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70.0, w / max(h, 1), 0.03, 60)
        glMatrixMode(GL_MODELVIEW)

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        fx, fz = math.sin(cam[2]), -math.cos(cam[2])
        cp = math.cos(cam[3])
        gluLookAt(cam[0], EYE, cam[1],
                  cam[0] + fx * cp, EYE + math.sin(cam[3]), cam[1] + fz * cp,
                  0, 1, 0)
        glCallList(scene)
        glutSwapBuffers()

    def update():
        now = glutGet(GLUT_ELAPSED_TIME)
        dt = min((now - st["last"]) / 1000.0, 0.05)
        st["last"] = now
        cam[2] += ((GLUT_KEY_RIGHT in arrows) - (GLUT_KEY_LEFT in arrows)) * 1.8 * dt
        cam[3] += ((GLUT_KEY_UP in arrows) - (GLUT_KEY_DOWN in arrows)) * 1.2 * dt
        cam[3] = max(-math.radians(85), min(math.radians(85), cam[3]))
        fx, fz = math.sin(cam[2]), -math.cos(cam[2])
        rx, rz = math.cos(cam[2]), math.sin(cam[2])
        f = (b'w' in keys) - (b's' in keys)
        s = (b'd' in keys) - (b'a' in keys)
        vx, vz = fx * f + rx * s, fz * f + rz * s
        n = math.hypot(vx, vz)
        if n > 0:
            speed = RUN if st["shift"] else WALK
            dx, dz = vx / n * speed * dt, vz / n * speed * dt
            if not blocked(cam[0] + dx, cam[1]):
                cam[0] += dx
            if not blocked(cam[0], cam[1] + dz):
                cam[1] += dz
        glutPostRedisplay()

    def key_down(k, x, y):
        mods()
        if k == b'\x1b':
            glutSetCursor(GLUT_CURSOR_INHERIT)
            try:
                glutLeaveMainLoop()
            except Exception:
                sys.exit()
        elif k.lower() == b'r':
            cam[:] = START
        else:
            keys.add(k.lower())

    def key_up(k, x, y):
        mods()
        keys.discard(k.lower())

    def special_down(k, x, y):
        if k in (112, 113):
            st["shift"] = True
        else:
            mods()
            arrows.add(k)

    def special_up(k, x, y):
        if k in (112, 113):
            st["shift"] = False
        else:
            mods()
            arrows.discard(k)

    def mouse_move(x, y):
        mods()
        cx, cy = glutGet(GLUT_WINDOW_WIDTH) // 2, glutGet(GLUT_WINDOW_HEIGHT) // 2
        if st["warp"]:
            st["warp"] = False
            return
        dx, dy = x - cx, y - cy
        if dx == 0 and dy == 0:
            return
        cam[2] += math.radians(dx * 0.12)
        cam[3] = max(-math.radians(85), min(math.radians(85), cam[3] - math.radians(dy * 0.12)))
        st["warp"] = True
        glutWarpPointer(cx, cy)

    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(update)
    glutKeyboardFunc(key_down)
    glutKeyboardUpFunc(key_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutPassiveMotionFunc(mouse_move)
    glutMotionFunc(mouse_move)
    glutIgnoreKeyRepeat(1)
    glutMainLoop()


if __name__ == "__main__":
    _preview()
