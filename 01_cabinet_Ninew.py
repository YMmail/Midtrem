import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Black background, mouse-drag rotation, wheel zoom. Press R to reset, ESC to quit.
SHADE=(1.0,0.55,0.80,0.90,0.72,0.93)
def quad(points,color):
    glColor3f(*color); glBegin(GL_QUADS)
    for p in points: glVertex3f(*p)
    glEnd()
def box(x0,y0,z0,x1,y1,z1,c):
    r,g,b=c; ks=SHADE
    faces=[([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],ks[0]), ([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],ks[1]), ([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],ks[2]), ([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],ks[3]), ([(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)],ks[4]), ([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],ks[5])]
    for pts,k in faces: quad(pts,(r*k,g*k,b*k))
def cylinder(cx, y0, cz, r, h, c, seg=16):
    glColor3f(*c); glBegin(GL_QUAD_STRIP)
    for i in range(seg+1):
        a=2*math.pi*i/seg; x=cx+r*math.cos(a); z=cz+r*math.sin(a)
        glVertex3f(x,y0,z); glVertex3f(x,y0+h,z)
    glEnd()
    for y in (y0,y0+h):
        glBegin(GL_TRIANGLE_FAN); glVertex3f(cx,y,cz)
        for i in range(seg+1):
            a=2*math.pi*i/seg; glVertex3f(cx+r*math.cos(a),y,cz+r*math.sin(a))
        glEnd()
def rod(a,b,r,c,seg=10):
    # cylinder between two points
    dx,dy,dz=b[0]-a[0],b[1]-a[1],b[2]-a[2]; length=math.sqrt(dx*dx+dy*dy+dz*dz)
    if length<1e-6:return
    glPushMatrix(); glTranslatef(*a)
    axis=( -dz,0,dx ); al=math.sqrt(axis[0]**2+axis[2]**2)
    if al>1e-6: glRotatef(math.degrees(math.acos(max(-1,min(1,dy/length)))),axis[0]/al,axis[1],axis[2]/al)
    elif dy<0: glRotatef(180,1,0,0)
    q=gluNewQuadric(); glColor3f(*c); gluCylinder(q,r,r,length,seg,1); gluDisk(q,0,r,seg,1); glTranslatef(0,0,length); gluDisk(q,0,r,seg,1); gluDeleteQuadric(q); glPopMatrix()
def roll_z(zc,xo,cy,r,length,col):
    glPushMatrix(); glTranslatef(xo,cy,zc); glRotatef(90,0,1,0); cylinder(0,-length/2,0,r,length,col,32); glPopMatrix()

def draw_object():
    # Steel cabinet body, shelves, sliding glass panels and top white box.
    z0,z1=0.50,1.98; h=1.90
    steel=(0.55,0.57,0.58); inner=(0.46,0.48,0.50); shelf=(0.62,0.64,0.66); alu=(0.74,0.76,0.78)
    glPushMatrix(); glTranslatef(-0.25,-0.95,-1.24)
    box(0.02,0,z0,0.045,h,z1,inner); box(0.02,0,z0,0.48,h,z0+0.03,steel); box(0.02,0,z1-0.03,0.48,h,z1,steel)
    box(0.02,h-0.03,z0,0.48,h,z1,steel); box(0.02,0,z0,0.48,0.06,z1,steel); box(0.045,0.86,z0,0.48,0.98,z1,steel); box(0.44,h-0.06,z0,0.48,h,z1,steel)
    for y in (0.45,1.28,1.56): box(0.045,y,z0+0.03,0.46,y+0.02,z1-0.03,shelf)
    # Four glass panes, tinted cyan, with aluminium frames
    panes=[(0.485,z0+.04,z0+.76,.98,1.84),(0.505,z0+.40,z0+1.12,.98,1.84),(0.485,z0+.22,z0+.94,.06,.86),(0.505,z0+.68,z0+1.40,.06,.86)]
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
    for px,za,zb,ya,yb in panes:
        glColor4f(.72,.88,.92,.22); glBegin(GL_QUADS)
        for p in [(px,ya,za),(px,ya,zb),(px,yb,zb),(px,yb,za)]: glVertex3f(*p)
        glEnd()
    glDepthMask(GL_TRUE); glDisable(GL_BLEND)
    for px,za,zb,ya,yb in panes:
        for args in [(px-.006,ya,za,px+.006,yb,za+.025),(px-.006,ya,zb-.025,px+.006,yb,zb),(px-.006,ya,za,px+.006,ya+.025,zb),(px-.006,yb-.025,za,px+.006,yb,zb)]: box(*args,alu)
    box(.04,h,z0+.04,.44,h+.15,z0+1.44,(.92,.92,.94))
    glPopMatrix()
rot_x,rot_y,zoom=20.0,-25.0,1.0
last_x=last_y=0; dragging=False
def display():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT); glLoadIdentity()
    glTranslatef(0,0,-4.0/zoom); glRotatef(rot_x,1,0,0); glRotatef(rot_y,0,1,0)
    draw_object(); glutSwapBuffers()
def reshape(w,h):
    glViewport(0,0,w,max(1,h)); glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(38,w/max(1,h),0.05,100); glMatrixMode(GL_MODELVIEW)
def mouse(button,state,x,y):
    global dragging,last_x,last_y,zoom
    if button==GLUT_LEFT_BUTTON: dragging=(state==GLUT_DOWN); last_x,last_y=x,y
    if state==GLUT_DOWN and button==3: zoom=min(2.5,zoom*1.1)
    if state==GLUT_DOWN and button==4: zoom=max(0.45,zoom/1.1)
    glutPostRedisplay()
def motion(x,y):
    global rot_x,rot_y,last_x,last_y
    if dragging: rot_y+=(x-last_x)*0.7; rot_x+=(y-last_y)*0.7; last_x,last_y=x,y; glutPostRedisplay()
def keyboard(key,x,y):
    global rot_x,rot_y,zoom
    if key==b'\x1b': raise SystemExit
    if key in (b'r',b'R'): rot_x,rot_y,zoom=20,-25,1
    glutPostRedisplay()
def main():
    glutInit(); glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH); glutInitWindowSize(900,700); glutCreateWindow(b'Isolated Studio Object - Drag mouse to rotate')
    glClearColor(0,0,0,1); glEnable(GL_DEPTH_TEST); glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION); gluPerspective(38,900/700,0.05,100); glMatrixMode(GL_MODELVIEW)
    glutDisplayFunc(display); glutReshapeFunc(reshape); glutMouseFunc(mouse); glutMotionFunc(motion); glutKeyboardFunc(keyboard); glutMainLoop()
if __name__=='__main__': main()
