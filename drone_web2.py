# drone_web2.py

"""
Enhanced interactive web interface for the Autonomous Drone Pathfinding Simulator.

Features:
- Preset maps
- Random map generation
- Custom clickable map builder
- Single algorithm mode
- Compare-all mode
- Optional path-order display
- Metrics for path length, explored nodes, and runtime
- Instructions, legend, and best-algorithm highlight
"""

import json
import random
import time

from flask import Flask, render_template_string, request

from algorithms import find_positions, bfs, dfs, astar
from maps import all_maps


app = Flask(__name__)


# Maps the algorithm names shown in the UI to the actual functions.
ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "A*": astar,
}


DEFAULT_CUSTOM_SIZE = 8


def make_random_grid(rows=8, cols=8, obstacle_probability=0.25):
    """
    Create a random grid with a fixed start and goal.
    Obstacles are placed randomly except on the start and goal cells.
    """
    grid = []

    for r in range(rows):
        row = []
        for c in range(cols):
            if (r, c) == (0, 0):
                row.append("S")
            elif (r, c) == (rows - 1, cols - 1):
                row.append("G")
            elif random.random() < obstacle_probability:
                row.append("X")
            else:
                row.append(".")
        grid.append(row)

    return grid


def make_empty_custom_grid(size=DEFAULT_CUSTOM_SIZE):
    """
    Create a blank custom grid.

    The start and goal are fixed to keep the map builder simple:
    - Start: top-left
    - Goal: bottom-right
    """
    grid = [["." for _ in range(size)] for _ in range(size)]
    grid[0][0] = "S"
    grid[size - 1][size - 1] = "G"

    return grid


def path_length(path):
    """
    Return the number of moves in a path.

    The path includes both the start and goal cells, so the number
    of moves is one less than the number of coordinates.
    """
    if path is None:
        return "N/A"

    return len(path) - 1


def run_algorithm(grid, algorithm_name):
    """
    Run one algorithm on one grid.

    Returns a dictionary containing the results needed for display:
    path, path length, explored nodes, runtime, and success status.
    """
    start, goal = find_positions(grid)

    if start is None or goal is None:
        return {
            "name": algorithm_name,
            "path": None,
            "path_length": "N/A",
            "explored_nodes": 0,
            "runtime": 0.0,
            "found": False,
            "is_best": False,
        }

    algorithm_function = ALGORITHMS[algorithm_name]

    # perf_counter is useful for measuring very short runtimes.
    start_time = time.perf_counter()
    path, explored_count = algorithm_function(grid, start, goal)
    end_time = time.perf_counter()

    return {
        "name": algorithm_name,
        "path": path,
        "path_length": path_length(path),
        "explored_nodes": explored_count,
        "runtime": end_time - start_time,
        "found": path is not None,
        "is_best": False,
    }


def mark_best_algorithm(results):
    """
    Mark the algorithm that explored the fewest nodes among successful runs.

    This is used only in compare mode. If no algorithm finds a path,
    none of them is marked as best.
    """
    successful_results = [result for result in results if result["found"]]

    if not successful_results:
        return results

    best_result = min(successful_results, key=lambda result: result["explored_nodes"])

    for result in results:
        result["is_best"] = result["name"] == best_result["name"]

    return results


def get_selected_grid(form):
    """
    Return the grid selected by the user.

    Supported choices:
    - Preset maps from maps.py
    - Randomly generated map
    - Custom map built in the browser
    """
    map_choice = form.get("map_choice", "preset_0")

    if map_choice == "random":
        return make_random_grid(), map_choice

    if map_choice == "custom":
        custom_grid_json = form.get("custom_grid", "")

        if custom_grid_json:
            return json.loads(custom_grid_json), map_choice

        return make_empty_custom_grid(), map_choice

    # Preset choices are stored as strings like "preset_0".
    preset_index = int(map_choice.split("_")[1])

    return all_maps[preset_index], map_choice


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Drone Pathfinding Simulator</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: linear-gradient(135deg, #eef4ff, #f9fbff);
            color: #222;
        }

        header {
            text-align: center;
            padding: 28px 20px;
            background: #1f2937;
            color: white;
        }

        header h1 {
            margin: 0;
            font-size: 30px;
        }

        header p {
            margin-top: 8px;
            color: #d1d5db;
        }

        .container {
            max-width: 1120px;
            margin: 25px auto;
            padding: 0 20px;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
        }

        .instructions {
            border-left: 6px solid #2563eb;
        }

        .instructions ul {
            margin-bottom: 0;
        }

        .tabs {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .tab-button {
            border: none;
            background: #e5e7eb;
            padding: 12px 18px;
            border-radius: 999px;
            cursor: pointer;
            font-size: 15px;
            color: #111827;
        }

        .tab-button.active {
            background: #2563eb;
            color: white;
        }

        .controls {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            align-items: center;
            justify-content: center;
        }

        select, button {
            padding: 9px 12px;
            font-size: 15px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
        }

        button {
            cursor: pointer;
            background: #2563eb;
            color: white;
            border: none;
            font-weight: bold;
        }

        button.secondary {
            background: #475569;
        }

        label {
            font-weight: bold;
        }

        .checkbox-label {
            font-weight: normal;
        }

        .legend {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 12px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
        }

        .legend-box {
            width: 20px;
            height: 20px;
            border-radius: 5px;
            border: 1px solid #cbd5e1;
        }

        .legend-start { background: #22c55e; }
        .legend-goal { background: #f59e0b; }
        .legend-obstacle { background: #111827; }
        .legend-open { background: #f8fafc; }
        .legend-path { background: #60a5fa; }
        .legend-step { background: #bfdbfe; }

        .grid {
            display: grid;
            gap: 5px;
            justify-content: center;
            margin: 20px auto;
        }

        .cell {
            width: 46px;
            height: 46px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            border-radius: 9px;
            border: 1px solid #d1d5db;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .cell:hover {
            transform: scale(1.04);
        }

        .start {
            background: #22c55e;
            color: white;
        }

        .goal {
            background: #f59e0b;
            color: white;
        }

        .obstacle {
            background: #111827;
            color: white;
        }

        .open {
            background: #f8fafc;
        }

        .path {
            background: #60a5fa;
            color: white;
            box-shadow: 0 0 0 2px #2563eb inset;
        }

        .step {
            background: #bfdbfe;
            color: #1e3a8a;
            font-size: 13px;
        }

        .custom-cell {
            cursor: pointer;
        }

        .custom-cell:hover {
            outline: 3px solid #93c5fd;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }

        .result-card {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            background: #f9fafb;
        }

        .best-card {
            border: 2px solid #22c55e;
            background: #f0fdf4;
        }

        .best-badge {
            display: inline-block;
            background: #22c55e;
            color: white;
            font-size: 13px;
            padding: 5px 9px;
            border-radius: 999px;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .metric {
            margin: 7px 0;
        }

        .path-text {
            font-size: 13px;
            word-wrap: break-word;
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        .note {
            text-align: center;
            color: #475569;
            font-size: 14px;
        }

        .hidden {
            display: none;
        }
    </style>
</head>

<body>
    <header>
        <h1>Autonomous Drone Pathfinding Simulator</h1>
        <p>Run BFS, DFS, and A* on preset, random, or custom drone maps.</p>
    </header>

    <div class="container">

        <section class="card instructions">
            <h2>How to Use This Simulator</h2>
            <ul>
                <li><strong>Run One Algorithm:</strong> choose a map and one algorithm to see its path and metrics.</li>
                <li><strong>Compare Algorithms:</strong> run BFS, DFS, and A* on the same map and compare performance.</li>
                <li><strong>Build Custom Map:</strong> click cells to add or remove obstacles, then select “Custom Map” in another tab.</li>
                <li><strong>Show path order:</strong> displays the numbered order of the final path instead of only stars.</li>
            </ul>

            <div class="legend">
                <div class="legend-item"><span class="legend-box legend-start"></span> Start</div>
                <div class="legend-item"><span class="legend-box legend-goal"></span> Goal</div>
                <div class="legend-item"><span class="legend-box legend-obstacle"></span> Obstacle</div>
                <div class="legend-item"><span class="legend-box legend-open"></span> Open Space</div>
                <div class="legend-item"><span class="legend-box legend-path"></span> Path</div>
                <div class="legend-item"><span class="legend-box legend-step"></span> Path Order</div>
            </div>
        </section>

        <div class="tabs">
            <button class="tab-button active" onclick="showTab('run-tab', this)">Run One Algorithm</button>
            <button class="tab-button" onclick="showTab('compare-tab', this)">Compare Algorithms</button>
            <button class="tab-button" onclick="showTab('custom-tab', this)">Build Custom Map</button>
        </div>

        <section id="run-tab" class="card">
            <h2>Run One Algorithm</h2>

            <form method="POST" onsubmit="syncCustomGrid()">
                <input type="hidden" name="mode" value="single">
                <input type="hidden" name="custom_grid" id="custom_grid_single">

                <div class="controls">
                    <label>Map:</label>
                    <select name="map_choice">
                        {% for i in range(num_maps) %}
                            <option value="preset_{{ i }}" {% if map_choice == "preset_" ~ i %}selected{% endif %}>
                                Map {{ i + 1 }}
                            </option>
                        {% endfor %}
                        <option value="random" {% if map_choice == "random" %}selected{% endif %}>Random Map</option>
                        <option value="custom" {% if map_choice == "custom" %}selected{% endif %}>Custom Map</option>
                    </select>

                    <label>Algorithm:</label>
                    <select name="algorithm_choice">
                        {% for name in algorithms %}
                            <option value="{{ name }}" {% if selected_algorithm == name %}selected{% endif %}>
                                {{ name }}
                            </option>
                        {% endfor %}
                    </select>

                    <label class="checkbox-label">
                        <input type="checkbox" name="show_steps" {% if show_steps %}checked{% endif %}>
                        Show path order
                    </label>

                    <button type="submit">Run</button>
                </div>
            </form>
        </section>

        <section id="compare-tab" class="card hidden">
            <h2>Compare Algorithms</h2>

            <form method="POST" onsubmit="syncCustomGrid()">
                <input type="hidden" name="mode" value="compare">
                <input type="hidden" name="custom_grid" id="custom_grid_compare">

                <div class="controls">
                    <label>Map:</label>
                    <select name="map_choice">
                        {% for i in range(num_maps) %}
                            <option value="preset_{{ i }}" {% if map_choice == "preset_" ~ i %}selected{% endif %}>
                                Map {{ i + 1 }}
                            </option>
                        {% endfor %}
                        <option value="random" {% if map_choice == "random" %}selected{% endif %}>Random Map</option>
                        <option value="custom" {% if map_choice == "custom" %}selected{% endif %}>Custom Map</option>
                    </select>

                    <label class="checkbox-label">
                        <input type="checkbox" name="show_steps" {% if show_steps %}checked{% endif %}>
                        Show path order
                    </label>

                    <button type="submit">Compare All</button>
                </div>
            </form>
        </section>

        <section id="custom-tab" class="card hidden">
            <h2>Build Your Own Map</h2>
            <p class="note">
                Click cells to toggle obstacles. Start is fixed at the top-left and goal is fixed at the bottom-right.
            </p>

            <div id="custom-grid" class="grid" style="grid-template-columns: repeat({{ custom_cols }}, 46px);"></div>

            <div class="controls">
                <button type="button" class="secondary" onclick="clearCustomGrid()">Clear Custom Map</button>
                <button type="button" class="secondary" onclick="randomizeCustomGrid()">Randomize Custom Map</button>
            </div>
        </section>

        <section class="card">
            <h2>Selected Map</h2>

            <div class="grid" style="grid-template-columns: repeat({{ cols }}, 46px);">
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
                        {% elif main_path and pos in main_path and show_steps %}
                            <div class="cell step">{{ main_path.index(pos) }}</div>
                        {% elif main_path and pos in main_path %}
                            <div class="cell path">*</div>
                        {% else %}
                            <div class="cell open">.</div>
                        {% endif %}
                    {% endfor %}
                {% endfor %}
            </div>
        </section>

        <section class="card">
            <h2>Results</h2>

            {% if not ran %}
                <p>Select a mode, map, and algorithm, then run the simulation.</p>

            {% elif mode == "single" %}
                <div class="result-card">
                    <h3>{{ results[0].name }}</h3>
                    <p class="metric"><strong>Path found:</strong> {{ "Yes" if results[0].found else "No" }}</p>
                    <p class="metric"><strong>Path length:</strong> {{ results[0].path_length }}</p>
                    <p class="metric"><strong>Explored nodes:</strong> {{ results[0].explored_nodes }}</p>
                    <p class="metric"><strong>Runtime:</strong> {{ "%.6f"|format(results[0].runtime) }} seconds</p>

                    {% if results[0].path %}
                        <p class="path-text"><strong>Path coordinates:</strong> {{ results[0].path }}</p>
                    {% endif %}
                </div>

            {% else %}
                <div class="results-grid">
                    {% for result in results %}
                        <div class="result-card {% if result.is_best %}best-card{% endif %}">
                            {% if result.is_best %}
                                <div class="best-badge">Most efficient on this map</div>
                            {% endif %}

                            <h3>{{ result.name }}</h3>
                            <p class="metric"><strong>Path found:</strong> {{ "Yes" if result.found else "No" }}</p>
                            <p class="metric"><strong>Path length:</strong> {{ result.path_length }}</p>
                            <p class="metric"><strong>Explored nodes:</strong> {{ result.explored_nodes }}</p>
                            <p class="metric"><strong>Runtime:</strong> {{ "%.6f"|format(result.runtime) }} seconds</p>

                            {% if result.path %}
                                <p class="path-text"><strong>Path coordinates:</strong> {{ result.path }}</p>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </section>
    </div>

    <script>
        let customGrid = {{ custom_grid_json | safe }};

        function showTab(tabId, button) {
            const tabs = ["run-tab", "compare-tab", "custom-tab"];

            tabs.forEach(id => {
                document.getElementById(id).classList.add("hidden");
            });

            document.getElementById(tabId).classList.remove("hidden");

            document.querySelectorAll(".tab-button").forEach(btn => {
                btn.classList.remove("active");
            });

            button.classList.add("active");
        }

        function drawCustomGrid() {
            const gridDiv = document.getElementById("custom-grid");
            gridDiv.innerHTML = "";

            for (let r = 0; r < customGrid.length; r++) {
                for (let c = 0; c < customGrid[0].length; c++) {
                    const cell = document.createElement("div");
                    cell.classList.add("cell", "custom-cell");

                    if (customGrid[r][c] === "S") {
                        cell.classList.add("start");
                        cell.textContent = "S";
                    } else if (customGrid[r][c] === "G") {
                        cell.classList.add("goal");
                        cell.textContent = "G";
                    } else if (customGrid[r][c] === "X") {
                        cell.classList.add("obstacle");
                        cell.textContent = "X";
                    } else {
                        cell.classList.add("open");
                        cell.textContent = ".";
                    }

                    cell.onclick = function () {
                        toggleObstacle(r, c);
                    };

                    gridDiv.appendChild(cell);
                }
            }
        }

        function toggleObstacle(r, c) {
            if (customGrid[r][c] === "S" || customGrid[r][c] === "G") {
                return;
            }

            customGrid[r][c] = customGrid[r][c] === "X" ? "." : "X";
            drawCustomGrid();
        }

        function clearCustomGrid() {
            for (let r = 0; r < customGrid.length; r++) {
                for (let c = 0; c < customGrid[0].length; c++) {
                    customGrid[r][c] = ".";
                }
            }

            customGrid[0][0] = "S";
            customGrid[customGrid.length - 1][customGrid[0].length - 1] = "G";

            drawCustomGrid();
        }

        function randomizeCustomGrid() {
            for (let r = 0; r < customGrid.length; r++) {
                for (let c = 0; c < customGrid[0].length; c++) {
                    const isStart = r === 0 && c === 0;
                    const isGoal = r === customGrid.length - 1 && c === customGrid[0].length - 1;

                    if (isStart || isGoal) {
                        continue;
                    }

                    customGrid[r][c] = Math.random() < 0.25 ? "X" : ".";
                }
            }

            drawCustomGrid();
        }

        function syncCustomGrid() {
            const gridString = JSON.stringify(customGrid);

            document.getElementById("custom_grid_single").value = gridString;
            document.getElementById("custom_grid_compare").value = gridString;
        }

        drawCustomGrid();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route for the web app.

    GET:
        Shows the default preset map.

    POST:
        Reads the user's selections, runs the selected simulation,
        and sends the results back to the page.
    """
    mode = "single"
    selected_algorithm = "BFS"
    map_choice = "preset_0"
    show_steps = False
    ran = False

    results = []
    main_path = None
    custom_grid = make_empty_custom_grid()

    if request.method == "POST":
        mode = request.form.get("mode", "single")
        selected_algorithm = request.form.get("algorithm_choice", "BFS")
        map_choice = request.form.get("map_choice", "preset_0")
        show_steps = request.form.get("show_steps") == "on"

        custom_grid_json = request.form.get("custom_grid", "")

        if custom_grid_json:
            custom_grid = json.loads(custom_grid_json)

        grid, map_choice = get_selected_grid(request.form)

        if mode == "single":
            result = run_algorithm(grid, selected_algorithm)
            results = [result]
            main_path = result["path"]

        else:
            results = [
                run_algorithm(grid, "BFS"),
                run_algorithm(grid, "DFS"),
                run_algorithm(grid, "A*"),
            ]

            results = mark_best_algorithm(results)

            # In compare mode, show A* on the main grid because it is
            # usually the most goal-directed algorithm.
            main_path = results[2]["path"]

        ran = True

    else:
        grid = all_maps[0]

    return render_template_string(
        HTML_TEMPLATE,
        grid=grid,
        rows=len(grid),
        cols=len(grid[0]),
        num_maps=len(all_maps),
        algorithms=ALGORITHMS.keys(),
        selected_algorithm=selected_algorithm,
        map_choice=map_choice,
        show_steps=show_steps,
        mode=mode,
        ran=ran,
        results=results,
        main_path=main_path,
        custom_grid_json=json.dumps(custom_grid),
        custom_cols=len(custom_grid[0]),
    )


if __name__ == "__main__":
    app.run(debug=True)
