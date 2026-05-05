# drone_web.py

"""
Interactive web interface for the Autonomous Drone Pathfinding Simulator.

This file connects the algorithm logic from algorithms.py with the map data
from maps.py and displays the results in a browser using Flask.
"""

import time

from flask import Flask, render_template_string, request

from algorithms import find_positions, bfs, dfs, astar
from maps import all_maps


app = Flask(__name__)


# Dictionary that maps the name shown in the UI to the actual function.
ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "A*": astar
}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Drone Pathfinding Simulator</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 30px;
            background-color: #f7f7f7;
        }

        h1 {
            text-align: center;
        }

        .controls {
            text-align: center;
            margin-bottom: 25px;
        }

        select, button {
            padding: 8px 12px;
            margin: 5px;
            font-size: 16px;
        }

        .grid {
            display: grid;
            gap: 4px;
            justify-content: center;
            margin-top: 20px;
        }

        .cell {
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            border-radius: 6px;
            border: 1px solid #ccc;
        }

        .start {
            background-color: #7dd87d;
        }

        .goal {
            background-color: #ffcc66;
        }

        .obstacle {
            background-color: #444;
            color: white;
        }

        .open {
            background-color: white;
        }

        .path {
            background-color: #70b7ff;
        }

        .metrics {
            max-width: 650px;
            margin: 25px auto;
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }

        .path-text {
            font-size: 14px;
            word-wrap: break-word;
        }
    </style>
</head>

<body>
    <h1>Autonomous Drone Pathfinding Simulator</h1>

    <div class="controls">
        <form method="POST">
            <label for="map_choice">Choose Map:</label>
            <select name="map_choice" id="map_choice">
                {% for i in range(num_maps) %}
                    <option value="{{ i }}" {% if i == selected_map %}selected{% endif %}>
                        Map {{ i + 1 }}
                    </option>
                {% endfor %}
            </select>

            <label for="algorithm_choice">Choose Algorithm:</label>
            <select name="algorithm_choice" id="algorithm_choice">
                {% for name in algorithms %}
                    <option value="{{ name }}" {% if name == selected_algorithm %}selected{% endif %}>
                        {{ name }}
                    </option>
                {% endfor %}
            </select>

            <button type="submit">Run Algorithm</button>
        </form>
    </div>

    <div class="grid" style="grid-template-columns: repeat({{ cols }}, 45px);">
        {% for r in range(rows) %}
            {% for c in range(cols) %}
                {% set cell = grid[r][c] %}
                {% set pos = (r, c) %}

                {% if cell == 'S' %}
                    <div class="cell start">S</div>
                {% elif cell == 'G' %}
                    <div class="cell goal">G</div>
                {% elif cell == 'X' %}
                    <div class="cell obstacle">X</div>
                {% elif path and pos in path %}
                    <div class="cell path">*</div>
                {% else %}
                    <div class="cell open">.</div>
                {% endif %}
            {% endfor %}
        {% endfor %}
    </div>

    <div class="metrics">
        <h2>Results</h2>

        {% if ran %}
            <p><strong>Algorithm:</strong> {{ selected_algorithm }}</p>
            <p><strong>Path found:</strong> {{ "Yes" if path else "No" }}</p>
            <p><strong>Path length:</strong> {{ path_length }}</p>
            <p><strong>Explored nodes:</strong> {{ explored_count }}</p>
            <p><strong>Runtime:</strong> {{ runtime }} seconds</p>

            {% if path %}
                <p class="path-text">
                    <strong>Path coordinates:</strong> {{ path }}
                </p>
            {% endif %}
        {% else %}
            <p>Select a map and algorithm, then click "Run Algorithm."</p>
        {% endif %}
    </div>
</body>
</html>
"""


def run_selected_algorithm(grid, algorithm_name):
    """
    Run the algorithm selected by the user.

    Parameters:
        grid: the selected map from maps.py
        algorithm_name: the selected algorithm name from the dropdown

    Returns:
        path: list of coordinates from start to goal, or None
        explored_count: number of nodes the algorithm explored
        path_length: number of moves in the path, or "N/A"
        runtime: execution time in seconds
    """

    start, goal = find_positions(grid)
    algorithm_function = ALGORITHMS[algorithm_name]

    # perf_counter gives a precise measurement for short code execution.
    start_time = time.perf_counter()
    path, explored_count = algorithm_function(grid, start, goal)
    end_time = time.perf_counter()

    runtime = end_time - start_time

    if path is None:
        path_length = "N/A"
    else:
        # The path list includes both start and goal, so moves = nodes - 1.
        path_length = len(path) - 1

    return path, explored_count, path_length, runtime


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page of the web app.

    GET request:
        Show the default map and default algorithm.

    POST request:
        Read the user's selected map and algorithm,
        run the selected algorithm, and display results.
    """

    selected_map = 0
    selected_algorithm = "BFS"

    path = None
    explored_count = None
    path_length = None
    runtime = None
    ran = False

    if request.method == "POST":
        selected_map = int(request.form["map_choice"])
        selected_algorithm = request.form["algorithm_choice"]

        grid = all_maps[selected_map]

        path, explored_count, path_length, runtime = run_selected_algorithm(
            grid,
            selected_algorithm
        )

        ran = True

    else:
        grid = all_maps[selected_map]

    return render_template_string(
        HTML_TEMPLATE,
        grid=grid,
        rows=len(grid),
        cols=len(grid[0]),
        num_maps=len(all_maps),
        algorithms=ALGORITHMS.keys(),
        selected_map=selected_map,
        selected_algorithm=selected_algorithm,
        path=path,
        explored_count=explored_count,
        path_length=path_length,
        runtime=f"{runtime:.6f}" if runtime is not None else None,
        ran=ran
    )


if __name__ == "__main__":
    app.run(debug=True)
