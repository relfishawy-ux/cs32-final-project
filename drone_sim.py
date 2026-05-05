from collections import deque

grid = [
    ['S', '.', '.', 'X', '.'],
    ['.', 'X', '.', 'X', '.'],
    ['.', '.', '.', '.', '.'],
    ['X', '.', 'X', '.', 'G']
]

ROWS = len(grid)
COLS = len(grid[0])

# Find start and goal
def find_positions():
    start = None
    goal = None
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'G':
                goal = (r, c)
    return start, goal

# BFS to find shortest path
def bfs(start, goal):
    queue = deque()
    queue.append((start, [start]))  # (position, path)

    visited = set()
    visited.add(start)

    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    while queue:
        (r, c), path = queue.popleft()

        if (r, c) == goal:
            return path

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if grid[nr][nc] != 'X' and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

    return None

# Printing the grid with path
def print_grid_with_path(path):
    display = [row[:] for row in grid]

    for r, c in path:
        if display[r][c] not in ('S', 'G'):
            display[r][c] = '*'

    for row in display:
        print(" ".join(row))


# Run everything
start, goal = find_positions()
path = bfs(start, goal)

if path:
    print("Path found!")
    print_grid_with_path(path)
else:
    print("No path found.")
