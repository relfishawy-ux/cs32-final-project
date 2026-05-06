# Autonomous Drone Pathfinding Simulator

## Project Description

This project is an autonomous drone pathfinding simulator written in Python. The simulator models a drone moving through a grid-based environment from a starting point to a goal while avoiding obstacles.

The project compares three pathfinding algorithms:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- A* Search

The original version of the project began as a simple BFS script that found a path through one fixed grid. Since then, it has grown into a modular simulator with multiple maps, comparison metrics, random map generation, a custom map builder, and an interactive browser-based interface.

The main purpose of the project is to explore how different search algorithms behave in constrained environments and to make their behavior easier to understand visually.

---

## Main Features

- Grid-based drone navigation simulation
- BFS, DFS, and A* pathfinding algorithms
- Preset maps with different obstacle layouts
- Random map generation
- Custom map builder where users can click cells to add or remove obstacles
- Single-algorithm mode
- Algorithm comparison mode
- Path length, explored nodes, and runtime metrics
- Visual display of the selected map and resulting path
- Optional path-order visualization
- Highlighting of the most efficient algorithm in comparison mode

---

## File Overview

### `algorithms.py`

This file contains the main pathfinding logic.

It includes:

- `bfs()`
- `dfs()`
- `astar()`
- helper functions for finding the start and goal
- helper logic for neighbors, path reconstruction, and heuristics

### `maps.py`

This file stores the preset map layouts used by the simulator.

Each map is represented as a 2D list where:

- `S` = start
- `G` = goal
- `X` = obstacle
- `.` = open space

### `drone_sim.py`

This is the terminal-based version of the simulator. It runs the algorithms on the maps and prints path results and comparison metrics in the terminal.

### `drone_web2.py`

This is the main interactive web interface for the final project. This is the recommended file to run for the best version of the project.

It includes:

- tab-based navigation
- map selection
- custom map building
- random map generation
- single-algorithm mode
- comparison mode
- visual path display
- metrics display

---

## Setup Instructions

### 1. Open the project folder

Make sure you are inside the project directory. In the terminal, this may look like:
cd /workspaces/cs32-final-project

### 2. Install Flask

The interactive interface uses Flask, so Flask must be installed before running the web version.
Run:

pip install flask

If your environment uses pip3, you can also run:
pip3 install flask

No API keys or external data files are required.


## How to Run the Project
Recommended: Run the Interactive Web Interface
To run the final interactive version, use:
python drone_web2.py

If your system uses python3, run:
python3 drone_web2.py

After running the command, the terminal should show that the Flask app is running, usually on:
http://127.0.0.1:5000

If you are using VS Code Codespaces or cs50.dev, you may see a pop-up saying that the application is available on port 5000. Click **Open in Browser**.

You can also open the **Ports** tab and open the forwarded port manually.

## How to Use the Web Interface

**Run One Algorithm**
1. Open the web interface.
2. Go to the Run One Algorithm tab.
3. Choose a map:
    - preset map
    - random map
    - custom map
4. Choose an algorithm:
    - BFS
    - DFS
    - A*
5. Optionally check Show path order.
6. Click Run.

The page will show:

- whether a path was found
- path length
- explored nodes
- runtime
- path coordinates
- visual path display on the grid

## Compare Algorithms
1. Go to the Compare Algorithms tab.
2. Choose a map.
3. Optionally check Show path order.
4. Click Compare All.

The simulator will run BFS, DFS, and A* on the same map and display their results side by side.
The comparison includes:

- path found or not
- path length
- explored nodes
- runtime
- path coordinates

The simulator also highlights the algorithm that explored the fewest nodes among the successful runs.

## Build a Custom Map

1. Go to the Build Custom Map tab.
2. Click cells to add or remove obstacles.
3. The start position is fixed at the top-left.
4. The goal position is fixed at the bottom-right.
5. After building the map, go to either:
    - Run One Algorithm
    - Compare Algorithms
6. In the map dropdown, select Custom Map.
7. Run the selected algorithm or compare all algorithms.

The custom map is passed from the browser to the Flask app when the user clicks Run or Compare.

## Random Map

To use a randomly generated map:

1. Go to Run One Algorithm or Compare Algorithms.
2. Select Random Map from the map dropdown.
3. Run the simulation.

Random maps may or may not contain a valid path. If no path exists, the simulator will report that no path was found.

## External Resources and AI Assistance

I used ChatGPT to help plan the project structure, improve code organization, and assist with parts of the browser-based user interface code, especially the Flask layout and HTML/CSS structure. I reviewed and tested the code myself and made sure I understood how the main pieces worked.

I also consulted the following Flask resources while building and understanding the web interface:

Flask Official Tutorial: https://flask.palletsprojects.com/en/stable/tutorial/

GeeksforGeeks Flask Tutorial: https://www.geeksforgeeks.org/python/flask-tutorial/

Flask Tutorial Video: https://www.youtube.com/watch?v=45P3xQPaYxc

No external API keys were used.
