# algorithms.py

from collections import deque
import heapq


def find_positions(grid):
    """
    Scan the grid and return the coordinates of the start ('S')
    and goal ('G') as tuples: (row, col).

    Returns:
        (start, goal)
        where start and goal are each either a tuple or None
    """
    start = None
    goal = None

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'G':
                goal = (r, c)

    return start, goal


def get_neighbors(grid, position):
    """
    Return all valid neighboring cells for a given position.

    A valid neighbor:
    - stays inside the bounds of the grid
    - is not an obstacle ('X')

    Movement is limited to four directions:
    up, down, left, right
    """
    rows = len(grid)
    cols = len(grid[0])
    r, c = position

    directions = [
        (1, 0),   # down
        (-1, 0),  # up
        (0, 1),   # right
        (0, -1)   # left
    ]

    neighbors = []

    for dr, dc in directions:
        nr, nc = r + dr, c + dc

        # Check that the new position is inside the grid
        if 0 <= nr < rows and 0 <= nc < cols:
            # Only allow movement onto non-obstacle cells
            if grid[nr][nc] != 'X':
                neighbors.append((nr, nc))

    return neighbors


def reconstruct_path(parent, start, goal):
    """
    Reconstruct a path from start to goal using a parent dictionary.

    The parent dictionary stores how each node was reached:
        parent[child] = previous_node

    We backtrack from the goal to the start, then reverse the list.
    """
    if goal not in parent and goal != start:
        return None

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()
    return path


def heuristic(position, goal):
    """
    Manhattan distance heuristic for A*.

    This works well for a grid where movement is only allowed
    up, down, left, and right.
    """
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def bfs(grid, start, goal):
    """
    Breadth-First Search (BFS)

    BFS explores nodes level by level using a queue.
    In an unweighted grid, it guarantees the shortest path
    in terms of number of steps.

    Returns:
        path, explored_count
    """
    if start is None or goal is None:
        return None, 0

    queue = deque([start])
    visited = {start}
    parent = {start: None}
    explored_count = 0

    while queue:
        current = queue.popleft()
        explored_count += 1

        if current == goal:
            return reconstruct_path(parent, start, goal), explored_count

        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None, explored_count


def dfs(grid, start, goal):
    """
    Depth-First Search (DFS)

    DFS explores as far as possible along one branch before backtracking.
    It uses a stack and does NOT guarantee the shortest path.

    Returns:
        path, explored_count
    """
    if start is None or goal is None:
        return None, 0

    stack = [start]
    visited = {start}
    parent = {start: None}
    explored_count = 0

    while stack:
        current = stack.pop()
        explored_count += 1

        if current == goal:
            return reconstruct_path(parent, start, goal), explored_count

        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    return None, explored_count


def astar(grid, start, goal):
    """
    A* Search

    A* uses both:
    - g(n): the known cost from the start to the current node
    - h(n): a heuristic estimate from the current node to the goal

    It prioritizes nodes with the smallest:
        f(n) = g(n) + h(n)

    In this grid setting, each move has cost 1 and we use
    Manhattan distance as the heuristic.

    Returns:
        path, explored_count
    """
    if start is None or goal is None:
        return None, 0

    # Priority queue entries look like:
    # (f_score, g_score, current_node)
    frontier = []
    heapq.heappush(frontier, (heuristic(start, goal), 0, start))

    parent = {start: None}
    g_score = {start: 0}
    explored_count = 0
    visited = set()

    while frontier:
        f_current, g_current, current = heapq.heappop(frontier)

        # Skip repeated outdated entries that may remain in the heap
        if current in visited:
            continue

        visited.add(current)
        explored_count += 1

        if current == goal:
            return reconstruct_path(parent, start, goal), explored_count

        for neighbor in get_neighbors(grid, current):
            tentative_g = g_score[current] + 1

            # Only update the neighbor if this path is better
            # than any previously found path to that neighbor
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (f_score, tentative_g, neighbor))

    return None, explored_count
