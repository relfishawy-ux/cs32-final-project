# maps.py

"""
This file defines different grid environments for testing
the drone pathfinding algorithms.

Legend:
'S' = start
'G' = goal
'X' = obstacle
'.' = open space
"""

# Simple map (baseline test)
grid1 = [
    ['S', '.', '.', 'X', '.'],
    ['.', 'X', '.', 'X', '.'],
    ['.', '.', '.', '.', '.'],
    ['X', '.', 'X', '.', 'G']
]


# Medium difficulty map (more obstacles)
grid2 = [
    ['S', '.', 'X', '.', '.'],
    ['.', 'X', 'X', '.', 'X'],
    ['.', '.', '.', '.', '.'],
    ['X', '.', 'X', '.', 'G']
]


# No-solution map (goal is blocked)
grid3 = [
    ['S', 'X', '.', '.', '.'],
    ['X', 'X', '.', 'X', '.'],
    ['.', '.', '.', 'X', '.'],
    ['.', 'X', 'X', 'X', 'G']
]


# Harder map (larger and more complex)
grid4 = [
    ['S', '.', '.', '.', 'X', '.', '.'],
    ['X', 'X', '.', 'X', 'X', '.', 'X'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', 'X', 'X', 'X', '.', 'X', '.'],
    ['.', '.', '.', 'X', '.', '.', 'G']
]


# List of all maps for easy iteration
all_maps = [grid1, grid2, grid3, grid4]
