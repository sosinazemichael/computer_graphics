## OpenGL Maze Generator & Solver

This project is a Python-based application that dynamically generates a rectangular maze and automatically finds a path from the start to the end using computer graphics.

## How it Works
1. Maze Generation (The "Mouse" Logic)
The maze is created using a Depth-First Search (DFS) algorithm.

An invisible "mouse" starts at a random cell and "eats" through walls to move to unvisited neighbors.

The mouse uses a Stack to keep track of its path. When it hits a dead end, it "pops" the stack to backtrack to the last cell with unvisited neighbors.

This ensures a "proper" maze where every cell is connected by a unique path.

2. The Solver (Backtracking)
Once the maze is generated, an automated solver finds the path:

Red Dot: Represents the current position of the solver.

Dark Red Path: Shows the current route the solver is taking.

Blue Dots: Mark dead ends where the solver had to backtrack.

3. Data Structures
As per the assignment requirements, the maze is represented using:

northWall[R][C]: A 2D array where 1 means the upper wall is intact and 0 means it is removed.

eastWall[R][C]: A 2D array where 1 means the right wall is intact and 0 means it is removed.

The zeroth row and column act as phantom boundaries to define the bottom and left edges of the maze.

Bonus Features
Cycle Creation: The program randomly removes extra walls (1 in 20 chance) to create cycles. This makes the maze a "graph" instead of a simple "tree," which can defeat the standard "shoulder-to-the-wall" navigation rule.

Interior Start/End: Instead of starting on the edges, the start and end points are placed randomly within the interior of the maze to make the traversal more interesting.

Requirements
To run this project, you need Python installed along with the PyOpenGL library:
pip install PyOpenGL PyOpenGL_accelerate

Controls
The process is fully automated.

Simply run python maze.py and watch the maze be "eaten" and then solved!
