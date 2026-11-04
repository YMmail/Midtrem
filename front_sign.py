import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ค่าคงที่ตำแหน่งและมิติป้ายหน้าห้อง
DOOR_B = 0.0
FRAME_HALF = 0.04
SIGN_GAP = 0.05
SIGN_W = 0.38
SIGN_H = 0.38       # ป้ายทรงจัตุรัสตามต้นฉบับ
SIGN_T = 0.015
SIGN_Y0 = 1.70
SIGN_Y1 = SIGN_Y0 + SIGN_H
FZ = 0.0

SIGN_TEX = [0]

def box(x0, y0, z0, x1, y1, z1, c):
    """วาดกล่องขอบป้ายโลหะ"""
    r, g, b = c
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1)
    glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glColor3f(r * 1.1, g * 1.1, b * 1.1)
    glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0)
    glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glColor3f(r * 0.7, g * 0.7, b * 0.7)
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0)
    glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    glColor3f(r * 0.85, g * 0.85, b * 0.85)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1)
    glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1)
    glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    glEnd()

# ตารางบิตแมป 7x9 สำหรับฟอนต์ตัวหนาตันพิเศษ (Extra Bold Sans-serif)
GLYPHS = {
    'C': [" 00000 ", "0000000", "00   00", "00     ", "00     ", "00     ", "00   00", "0000000", " 00000 "],
    'B': ["000000 ", "0000000", "00   00", "000000 ", "000000 ", "00   00", "00   00", "0000000", "000000 "],
    '3': ["000000 ", "0000000", "     00", " 00000 ", " 00000 ", "     00", "     00", "0000000", "000000 "],
    '0': [" 00000 ", "0000000", "00   00", "00   00", "00   00", "00   00", "00   00", "0000000", " 00000 "],
    '6': [" 00000 ", "0000000", "00     ", "000000 ", "0000000", "00   00", "00   00", "0000000", " 00000 "],
    '9': [" 00000 ", "0000000", "00   00", "00   00", "0000000", "     00", "     00", "0000000", " 00000 "],
    'P': ["000000 ", "0000000", "00   00", "0000000", "000000 ", "00     ", "00     ", "00     ", "00     "],
    'h': ["00     ", "00     ", "00     ", "000000 ", "0000000", "00   00", "00   00", "00   00", "00   00"],
    'o': ["       ", "       ", "       ", " 00000 ", "0000000", "00   00", "00   00", "0000000", " 00000 "],
    't': ["  00   ", "  00   ", "0000000", "  00   ", "  00   ", "  00   ", "  00   ", "  00 00", "   000 "],
    'S': [" 00000 ", "0000000", "00     ", "000000 ", " 000000", "     00", "00   00", "0000000", " 00000 "],
    'u': ["       ", "       ", "       ", "00   00", "00   00", "00   00", "00   00", "0000000", " 000000"],
    'd': ["     00", "     00", "     00", " 000000", "0000000", "00   00", "00   00", "0000000", " 000000"],
    'i': ["  00   ", "  00   ", "       ", " 000   ", "  00   ", "  00   ", "  00   ", "  00   ", "0000000"],
    ' ': ["       ", "       ", "       ", "       ", "       ", "       ", "       ", "       ", "       "],
}

def generate_sign_texture():
    """สร้างพื้นผิวป้ายความละเอียด 512x512: ตัวอักษรใหญ่หนาเต็มแผ่น และลายโค้งเว้าลงด้านล่าง"""
    W_TEX, H_TEX = 512, 512
    tex_grid = [[[0, 0, 0, 255] for _ in range(W_TEX)] for _ in range(H_TEX)]

    # สัดส่วนความสูงของเส้นแบ่งครึ่ง (ให้พื้นที่ส่วนบนกว้างพอสำหรับฟอนต์ใหญ่)
    y_split = int(H_TEX * 0.52)

    for y in range(H_TEX):
        for x in range(W_TEX):
            # คำนวณความโค้งเว้าลง (Concave Parabola): จุดกึ่งกลาง x จะมีค่าต่ำสุด
            dx_norm = (x - W_TEX / 2.0) / (W_TEX / 2.0)
            # โค้งเว้าลงมา: ที่ขอบซ้ายขวา y_curve จะสูง ที่กลางจะเว้าลงมาลึก
            y_curve = int(28 + (dx_norm ** 2) * 32)

            if y > y_split:
                # 1. ส่วนบน: โลหะสเตนเลสไล่เฉดสีเงินเงา (Metallic Gradient)
                factor = (y - y_split) / float(H_TEX - y_split)
                # ด้านบนมืด ด้านล่างสว่างสะท้อนแสง
                r = int(140 + (1.0 - factor) * 85)
                g = int(146 + (1.0 - factor) * 85)
                b = int(154 + (1.0 - factor) * 85)
                # ไฮไลต์ปัดเงาด้านข้าง
                shadow = 1.0 - 0.15 * (dx_norm ** 2)
                tex_grid[y][x] = [int(r * shadow), int(g * shadow), int(b * shadow), 255]

            elif y > y_curve:
                # 2. ส่วนกลาง: แผ่นสีเบจ/ครีมอมเทา (Beige Panel)
                factor = (y - y_curve) / float(y_split - y_curve)
                r = int(180 + factor * 25)
                g = int(173 + factor * 24)
                b = int(162 + factor * 22)
                tex_grid[y][x] = [r, g, b, 255]

            else:
                # 3. ส่วนล่างสุด: แถบโลหะโค้งเว้า (Curved Metallic Accent)
                dist_from_curve = y_curve - y
                if dist_from_curve < 5:
                    # เส้นขอบไฮไลต์สว่างสีเงิน (Highlight Rim)
                    tex_grid[y][x] = [225, 230, 235, 255]
                elif dist_from_curve < 10:
                    # เงาตกกระทบใต้ขอบโค้ง
                    tex_grid[y][x] = [80, 84, 90, 255]
                else:
                    # พื้นผิวแถบโลหะด้านล่าง
                    factor = y / float(max(1, y_curve))
                    r = int(110 + factor * 50)
                    g = int(115 + factor * 50)
                    b = int(125 + factor * 50)
                    tex_grid[y][x] = [r, g, b, 255]

    # เส้นรอยต่อแนวนอนระหว่างส่วนบนและส่วนล่าง
    for x in range(W_TEX):
        tex_grid[y_split][x] = [110, 112, 118, 255]
        tex_grid[y_split - 1][x] = [215, 218, 224, 255]

    # ฟังก์ชันสแตมป์ตัวอักษรลงบนบิตแมป
    def render_bold_string(text, start_x, start_y, pixel_size, spacing, color):
        curr_x = start_x
        for char in text:
            if char in GLYPHS:
                glyph = GLYPHS[char]
                for row_idx, row_str in enumerate(reversed(glyph)):
                    for col_idx, col_char in enumerate(row_str):
                        if col_char == '0':
                            for py in range(pixel_size):
                                for px in range(pixel_size):
                                    gx = curr_x + col_idx * pixel_size + px
                                    gy = start_y + row_idx * pixel_size + py
                                    if 0 <= gx < W_TEX and 0 <= gy < H_TEX:
                                        tex_grid[gy][gx] = [color[0], color[1], color[2], 255]
            # ช่องว่างระหว่างตัวอักษร
            curr_x += 7 * pixel_size + spacing

    def get_text_width(text, pixel_size, spacing):
        return len(text) * (7 * pixel_size + spacing) - spacing

    # --- ขยายขนาดตัวอักษรให้ใหญ่ หนา และกว้างเต็มแผ่นเหมือนต้นฉบับ ---

    # 1. "CB 30609" สีดำตัวหนาใหญ่มาก ครึ่งบน
    scale_top = 6          # ขยายขนาดพิกเซลให้ตัวอักษรใหญ่และหนาขึ้นชัดเจน
    spacing_top = 4
    str_top = "CB 30609"
    w_top = get_text_width(str_top, scale_top, spacing_top)
    x_top = (W_TEX - w_top) // 2
    render_bold_string(str_top, x_top, int(H_TEX * 0.69), scale_top, spacing_top, (24, 25, 28))

    # 2. "Photo Studio" สีขาวตัวหนาใหญ่ ครึ่งล่าง
    scale_bot = 4          # ขยายขนาดพิกเซลให้ตัวหนังสือสีขาวหนาเด่น
    spacing_bot = 3
    str_bot = "Photo Studio"
    w_bot = get_text_width(str_bot, scale_bot, spacing_bot)
    x_bot = (W_TEX - w_bot) // 2
    render_bold_string(str_bot, x_bot, int(H_TEX * 0.22), scale_bot, spacing_bot, (255, 255, 255))

    # รวมเป็นข้อมูล 1D ส่งให้ OpenGL Texture
    flat_data = bytearray()
    for row in tex_grid:
        for pixel in row:
            flat_data.extend(pixel)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, W_TEX, H_TEX, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes(flat_data))
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id

def front_sign():
    """วาดป้ายโดยผูก Texture ที่เรนเดอร์ตัวอักษรและลายโค้งสมบูรณ์แล้ว"""
    x0 = DOOR_B + FRAME_HALF + SIGN_GAP
    x1 = x0 + SIGN_W
    zs = FZ + SIGN_T
    zf = zs + 0.001

    # ขอบกรอบโลหะสีเทาเข้ม
    border = 0.009
    box(x0 - border, SIGN_Y0 - border, FZ, x1 + border, SIGN_Y1 + border, zs, (0.30, 0.32, 0.34))

    # หน้าป้ายสี่เหลี่ยมแนบ Texture
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, SIGN_TEX[0])
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(x0, SIGN_Y0, zf)
    glTexCoord2f(1.0, 0.0); glVertex3f(x1, SIGN_Y0, zf)
    glTexCoord2f(1.0, 1.0); glVertex3f(x1, SIGN_Y1, zf)
    glTexCoord2f(0.0, 1.0); glVertex3f(x0, SIGN_Y1, zf)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

def display():
    glClearColor(0.95, 0.95, 0.96, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    x_center = DOOR_B + FRAME_HALF + SIGN_GAP + SIGN_W / 2
    y_center = (SIGN_Y0 + SIGN_Y1) / 2

    glTranslatef(0.0, 0.0, -0.65)
    glRotatef(0, 1, 0, 0)
    glRotatef(0, 0, 1, 0)
    glTranslatef(-x_center, -y_center, -FZ)

    front_sign()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(950, 750)
    glutCreateWindow(b"Front Sign - Exact Match")

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, (950 / 750), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    # สร้าง Texture ป้ายความละเอียดสูง
    SIGN_TEX[0] = generate_sign_texture()

    glutDisplayFunc(display)

    glutMainLoop()

if __name__ == "__main__":
    main()