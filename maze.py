import random
import time
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Configuration
R, C = 20, 25  
CELL_SIZE = 30
WINDOW_WIDTH = C * CELL_SIZE
WINDOW_HEIGHT = R * CELL_SIZE

# Data Structures
# northWall[i][j] = 1 means solid upper wall
northWall = [[1 for _ in range(C)] for _ in range(R + 1)] 
# eastWall[i][j] = 1 means solid right wall
eastWall = [[1 for _ in range(C + 1)] for _ in range(R)]
visited = [[False for _ in range(C)] for _ in range(R)]

# State Management
stack = []
current_cell = (0, 0)
visited[0][0] = True
generating = True
solving = False
solve_stack = []
dead_ends = set()
path = []

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

def draw_maze():
    glColor3f(1.0, 1.0, 1.0) # White walls
    glLineWidth(2)
    glBegin(GL_LINES)
    for r in range(R):
        for c in range(C):
            # Draw North Walls
            if northWall[r][c]:
                glVertex2f(c * CELL_SIZE, (r + 1) * CELL_SIZE)
                glVertex2f((c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE)
            # Draw East Walls
            if eastWall[r][c]:
                glVertex2f((c + 1) * CELL_SIZE, r * CELL_SIZE)
                glVertex2f((c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE)
    
    # Left edge and Bottom edge boundaries
    for r in range(R):
        if eastWall[r][C]: # Left phantom edge
            glVertex2f(0, r * CELL_SIZE)
            glVertex2f(0, (r + 1) * CELL_SIZE)
    for c in range(C):
        if northWall[R][c]: # Bottom phantom edge
            glVertex2f(c * CELL_SIZE, 0)
            glVertex2f((c + 1) * CELL_SIZE, 0)
    glEnd()

def draw_entities():
    # 1. Draw Dead Ends (Blue Dots) - Explored and rejected
    glColor3f(0.0, 0.0, 1.0)
    glPointSize(10)
    glBegin(GL_POINTS)
    for (r, c) in dead_ends:
        glVertex2f(c * CELL_SIZE + CELL_SIZE/2, r * CELL_SIZE + CELL_SIZE/2)
    glEnd()

    # 2. Draw the Travelled Path (Red Dots) - The stack leading to the mouse
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    # Draw everything EXCEPT the very last point
    for (r, c) in path[:-1]: 
        glVertex2f(c * CELL_SIZE + CELL_SIZE/2, r * CELL_SIZE + CELL_SIZE/2)
    glEnd()

    # 3. Draw the ACTIVE MOUSE (Green Dot) - The current head
    if path:
        r, c = path[-1]
        glColor3f(0.0, 1.0, 0.0) # Green for the "living" mouse
        glPointSize(14) # Make it slightly larger to be the "hero"
        glBegin(GL_POINTS)
        glVertex2f(c * CELL_SIZE + CELL_SIZE/2, r * CELL_SIZE + CELL_SIZE/2)
        glEnd()

def generate_step():
    global current_cell, generating, solving
    r, c = current_cell
    neighbors = []

    # Check bounds and "intact" status of neighbors[cite: 1]
    if r < R - 1 and not visited[r + 1][c]: neighbors.append((r + 1, c, 'N'))
    if r > 0 and not visited[r - 1][c]:     neighbors.append((r - 1, c, 'S'))
    if c < C - 1 and not visited[r][c + 1]: neighbors.append((r, c + 1, 'E'))
    if c > 0 and not visited[r][c - 1]:     neighbors.append((r, c - 1, 'W'))

    if neighbors:
        nr, nc, direction = random.choice(neighbors)
        stack.append(current_cell)
        
        # "Eat" through the wall[cite: 1]
        if direction == 'N': northWall[r][c] = 0
        if direction == 'S': northWall[r-1][c] = 0
        if direction == 'E': eastWall[r][c] = 0
        if direction == 'W': eastWall[r][c-1] = 0
        
        visited[nr][nc] = True
        current_cell = (nr, nc)
    elif stack:
        current_cell = stack.pop() # Backtrack during generation[cite: 1]
    else:
        generating = False
        # Create start/end openings[cite: 1]
        eastWall[R-1][C] = 0 # Entrance left
        eastWall[0][C-1] = 0 # Exit right
        solving = True
        solve_stack.append((R-1, 0))
def solve_step():
    global solving, path
    if not solve_stack: return
    
    r, c = solve_stack[-1]
    path = list(solve_stack)
    
    if (r, c) == (0, C - 1): # Reached Goal[cite: 1]
        solving = False
        return

    # Try random direction move[cite: 1]
    moves = []
    # North
    if r < R - 1 and northWall[r][c] == 0 and (r + 1, c) not in solve_stack and (r + 1, c) not in dead_ends:
        moves.append((r + 1, c))
    # South
    if r > 0 and northWall[r - 1][c] == 0 and (r - 1, c) not in solve_stack and (r - 1, c) not in dead_ends:
        moves.append((r - 1, c))
    # East
    if c < C - 1 and eastWall[r][c] == 0 and (r, c + 1) not in solve_stack and (r, c + 1) not in dead_ends:
        moves.append((r, c + 1))
    # West
    if c > 0 and eastWall[r][c - 1] == 0 and (r, c - 1) not in solve_stack and (r, c - 1) not in dead_ends:
        moves.append((r, c - 1))

    if moves:
        solve_stack.append(random.choice(moves))
    else:
        dead_ends.add(solve_stack.pop()) # Mark dead end blue[cite: 1]

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_maze()
    draw_entities()
    glutSwapBuffers()

def update(value):
    if generating:
        generate_step()
    elif solving:
        solve_step()
    
    glutPostRedisplay()
    glutTimerFunc(10, update, 0) # Adjust speed for "delightful" viewing[cite: 1]

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Maze Builder & Runner")
    init()
    glutDisplayFunc(display)
    glutTimerFunc(10, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()