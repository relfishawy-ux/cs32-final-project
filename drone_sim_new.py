# drone_sim.py

import time
from algorithms import find_positions, bfs, dfs, astar
from maps import all_maps


def print_grid(grid):
    """
    Print the original grid in a clean, readable format.
    """
    for row in grid:
        print(" ".join(row))


def print_grid_with_path(grid, path):
    """
    Print a copy of the grid with the discovered path marked by '*'.

    The start ('S') and goal ('G') are preserved.
    If no path exists, the original grid is printed unchanged.
    """
    display = [row[:] for row in grid]

    if path is not None:
        for r, c in path:
            if display[r][c] not in ("S", "G"):
                display[r][c] = "*"

    for row in display:
        print(" ".join(row))


def path_length(path):
    """
    Return the number of moves in the path.
    If no path exists, return None.
    """
    if path is None:
        return None
    return len(path) - 1


def run_algorithm(grid, algorithm_name, algorithm_function):
    """
    Run one pathfinding algorithm on one grid and return a dictionary
    of results for later comparison.

    Returned fields:
    - name
    - path
    - path_length
    - explored_nodes
    - runtime
    """
    start, goal = find_positions(grid)

    print(f"\n{algorithm_name}")
    print("-" * len(algorithm_name))

    if start is None or goal is None:
        print("Error: grid must contain both 'S' and 'G'.")
        return {
            "name": algorithm_name,
            "path": None,
            "path_length": None,
            "explored_nodes": 0,
            "runtime": 0.0
        }

    # Measure runtime for one execution of the algorithm
    start_time = time.perf_counter()
    path, explored_count = algorithm_function(grid, start, goal)
    end_time = time.perf_counter()

    runtime = end_time - start_time
    length = path_length(path)

    if path is None:
        print("No path found.")
        print(f"Explored nodes: {explored_count}")
        print(f"Runtime: {runtime:.6f} seconds")
        print("Grid:")
        print_grid(grid)
    else:
        print("Path found.")
        print(f"Path length: {length}")
        print(f"Explored nodes: {explored_count}")
        print(f"Runtime: {runtime:.6f} seconds")
        print(f"Path coordinates: {path}")
        print("Grid with path:")
        print_grid_with_path(grid, path)

    return {
        "name": algorithm_name,
        "path": path,
        "path_length": length,
        "explored_nodes": explored_count,
        "runtime": runtime
    }


def print_summary_table(results):
    """
    Print a summary table comparing all algorithms on the same map.
    """
    print("\nSummary Table")
    print("-" * 72)
    print(f"{'Algorithm':28} {'Found Path':12} {'Path Length':12} {'Explored':10} {'Runtime (s)':>10}")
    print("-" * 72)

    for result in results:
        found_path = "Yes" if result["path"] is not None else "No"
        length = result["path_length"] if result["path_length"] is not None else "N/A"
        explored = result["explored_nodes"]
        runtime = f"{result['runtime']:.6f}"

        print(f"{result['name']:28} {found_path:12} {str(length):12} {str(explored):10} {runtime:>10}")

    print("-" * 72)


def compare_algorithms(grid, map_number):
    """
    Run all algorithms on the same grid so their behavior
    can be compared directly.
    """
    print("\n" + "=" * 50)
    print(f"MAP {map_number}")
    print("=" * 50)

    print("\nOriginal grid:")
    print_grid(grid)

    results = []
    results.append(run_algorithm(grid, "Breadth-First Search (BFS)", bfs))
    results.append(run_algorithm(grid, "Depth-First Search (DFS)", dfs))
    results.append(run_algorithm(grid, "A* Search", astar))

    print_summary_table(results)


def main():
    """
    Main driver for the simulation.
    Iterates through all maps and compares BFS, DFS, and A*.
    """
    for i, grid in enumerate(all_maps, start=1):
        compare_algorithms(grid, i)


if __name__ == "__main__":
    main()
