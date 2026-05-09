import random
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# --- CONFIGURATION AND DIMENSIONS ---
R, C = 20, 25
CELL_SIZE = 30
WINDOW_WIDTH = C * CELL_SIZE
WINDOW_HEIGHT = R * CELL_SIZE

# --- DATA STRUCTURE DEFINITIONS ---
# northWall[i][j] tracks horizontal walls; eastWall[i][j] tracks vertical walls
northWall = [[1 for _ in range(C)] for _ in range(R + 1)]
eastWall = [[1 for _ in range(C + 1)] for _ in range(R)]
visited = [[False for _ in range(C)] for _ in range(R)]

# --- STATE MANAGEMENT ---
stack = []
current_cell = (0, 0)
visited[0][0] = True
generating = True
solving = False

# --- SOLVER STATE (WALL FOLLOWER) ---
direction = 1  # 0:N, 1:E, 2:S, 3:W
mouse_position = (R - 1, 0)
path = []
dead_ends = set()
visited_solver = set()
ENABLE_CYCLES = True

# --- OPENGL INITIALIZATION ---
def init():
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

# --- MAZE RENDERING LOGIC ---
def draw_maze():
    glColor3f(1, 1, 1)
    glLineWidth(2)
    glBegin(GL_LINES)
    for r in range(R):
        for c in range(C):
            y = (R - r - 1) * CELL_SIZE
            if northWall[r][c]:
                glVertex2f(c * CELL_SIZE, y + CELL_SIZE)
                glVertex2f((c + 1) * CELL_SIZE, y + CELL_SIZE)
            if eastWall[r][c]:
                glVertex2f((c + 1) * CELL_SIZE, y)
                glVertex2f((c + 1) * CELL_SIZE, y + CELL_SIZE)
    for r in range(R):
        y = (R - r - 1) * CELL_SIZE
        if eastWall[r][C]:
            glVertex2f(0, y)
            glVertex2f(0, y + CELL_SIZE)
    for c in range(C):
        if northWall[R][c]:
            glVertex2f(c * CELL_SIZE, 0)
            glVertex2f((c + 1) * CELL_SIZE, 0)
    glEnd()

# --- ENTITY RENDERING (MOUSE AND PATH) ---
def draw_entities():
    glEnable(GL_POINT_SMOOTH)
    glColor3f(1, 0, 0)
    glPointSize(6)
    glBegin(GL_POINTS)
    for r, c in path:
        y = (R - r - 1) * CELL_SIZE
        glVertex2f(c * CELL_SIZE + CELL_SIZE / 2, y + CELL_SIZE / 2)
    glEnd()

    glColor3f(0, 0, 1)
    glPointSize(8)
    glBegin(GL_POINTS)
    for r, c in dead_ends:
        y = (R - r - 1) * CELL_SIZE
        glVertex2f(c * CELL_SIZE + CELL_SIZE / 2, y + CELL_SIZE / 2)
    glEnd()

    r, c = mouse_position
    y = (R - r - 1) * CELL_SIZE
    glColor3f(0, 1, 0)
    glPointSize(12)
    glBegin(GL_POINTS)
    glVertex2f(c * CELL_SIZE + CELL_SIZE / 2, y + CELL_SIZE / 2)
    glEnd()

# --- MAZE GENERATION ALGORITHM (DFS) ---
def generate_step():
    global current_cell, generating, solving
    r, c = current_cell
    neighbors = []
    if r < R - 1 and not visited[r + 1][c]: neighbors.append((r + 1, c, 'N'))
    if r > 0 and not visited[r - 1][c]: neighbors.append((r - 1, c, 'S'))
    if c < C - 1 and not visited[r][c + 1]: neighbors.append((r, c + 1, 'E'))
    if c > 0 and not visited[r][c - 1]: neighbors.append((r, c - 1, 'W'))

    if neighbors:
        nr, nc, d = random.choice(neighbors)
        stack.append(current_cell)
        if d == 'N': northWall[r][c] = 0
        elif d == 'S': northWall[r - 1][c] = 0
        elif d == 'E': eastWall[r][c] = 0
        elif d == 'W': eastWall[r][c - 1] = 0
        visited[nr][nc] = True
        current_cell = (nr, nc)
    elif stack:
        current_cell = stack.pop()
    else:
        generating = False
        eastWall[R - 1][0] = 0
        eastWall[0][C - 1] = 0 
        if ENABLE_CYCLES:
            for _ in range((R * C) // 20):
                r_rand = random.randint(0, R - 2)
                c_rand = random.randint(0, C - 2)
                if random.choice([True, False]): northWall[r_rand][c_rand] = 0
                else: eastWall[r_rand][c_rand] = 0
        solving = True

# --- SOLVER MOVEMENT AND COLLISION LOGIC ---
def can_move(r, c, d):
    if d == 0: return r < R - 1 and northWall[r][c] == 0
    elif d == 1: return c < C - 1 and eastWall[r][c] == 0
    elif d == 2: return r > 0 and northWall[r - 1][c] == 0
    elif d == 3: return c > 0 and eastWall[r][c - 1] == 0
    return False

def move_forward(r, c, d):
    if d == 0: return (r + 1, c)
    elif d == 1: return (r, c + 1)
    elif d == 2: return (r - 1, c)
    elif d == 3: return (r, c - 1)

# --- BACKTRACKING SOLVER ALGORITHM ---
def solve_step():
    global mouse_position, direction, solving
    r, c = mouse_position
    path.append((r, c))
    visited_solver.add((r, c))
    if (r, c) == (0, C - 1):
        print("Maze solved!")
        solving = False
        return    
    
    priorities = [(direction + 1) % 4, direction, (direction - 1) % 4, (direction + 2) % 4]
    moved = False
    for nd in priorities:
        if can_move(r, c, nd):
            direction = nd
            nr, nc = move_forward(r, c, nd)
            mouse_position = (nr, nc)
            moved = True
            break
    if not moved:
        dead_ends.add((r, c))

# --- MAIN DISPLAY AND UPDATE LOOP ---
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_maze()
    draw_entities()
    glutSwapBuffers()

def update(value):
    if generating: generate_step()
    elif solving: solve_step()
    glutPostRedisplay()
    glutTimerFunc(20, update, 0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Maze Generator + Wall Follower + Cycles")
    init()
    glutDisplayFunc(display)
    glutTimerFunc(20, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()