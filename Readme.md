# 2D Robot Simulator

A small SDL2-based 2D robot simulator: drive a robot around by hand with the
arrow keys, or hand it a list of goals and watch it plan a path around
obstacles (BFS / Dijkstra / A*) and drive itself there with a simple PID
controller.

## Features

- **2D simulation window** (SDL2 / `pysdl2`) with a robot sprite that moves
  and collides with obstacles and the boundary walls.
- **Heading**: the robot's current direction of travel is drawn as a red
  line, computed from its velocity vector each frame.
- **Environments**: `Env2D` holds a set of rectangular `Obstacle`s (plus a
  convenience for walling off the four edges), rendered on screen and
  enforced as real collisions — the robot can't drive through them.
- **Path planning**: `Planner.py` builds an occupancy grid from the
  environment's obstacles and finds a route between two points using one
  of three algorithms:
  - `bfs` — fewest grid-cell hops
  - `dijkstra` — true shortest path, explores in all directions
  - `astar` — shortest path with a heuristic, explores far fewer cells
  Planned paths are smoothed into straight segments and drawn as small
  yellow dots so you can see the route before the robot drives it.
- **Goal following**: give `main.py` a list of goal coordinates and the
  robot will plan a path through all of them (avoiding obstacles) and
  follow it with a P/I controller, advancing to the next waypoint once it
  gets within a small distance tolerance.

## Installation

Tested on Python 3.12.0, Windows.

```
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
```

Install the `pysdl2` Python bindings and their compiled SDL2 binaries:

```
> pip install pysdl2 pysdl2-dll
```

Reference: https://pysdl2.readthedocs.io/en/0.9.13/tutorial/pong.html

## Coordinate system

Origin `(0, 0)` is the **top-left** of the window; `x` increases to the
right, `y` increases downward. So a *negative* y-velocity moves the robot
**up** the screen. Left/right (`x`) behaves as you'd expect.

```
(0,0) ------------------> +x
  |
  |
  |
  v
 +y                    (window_width, window_height)
```

Robot heading follows the same convention: 0° points along `+x` (right),
and positive angles rotate clockwise (since `y` increases downward).

## Usage

```
> python main.py
```

By default `main.py`:
1. Creates an `Env2D` with border walls and a couple of sample obstacles.
2. Plans a path through a hardcoded list of goal coordinates using the
   algorithm set in `ALGORITHM` (`"astar"` by default — try `"bfs"` or
   `"dijkstra"` too).
3. Drives the robot along that path in a loop, printing position,
   velocity, heading, and current waypoint once per second.

Arrow-key input is still wired up in `Simulator2D.run()`, but while
`main.py`'s waypoint-following loop is active it recalculates and
overwrites the robot's velocity every iteration, so a keypress has no
lasting effect during autonomous driving. To drive manually, comment out
the PID velocity-setting lines in `main.py`'s loop.

## Project layout

| File            | Purpose                                                        |
|-----------------|------------------------------------------------------------------|
| `main.py`       | Entry point: sets up robot/env/sim, plans a path, runs the loop |
| `Robot.py`      | Robot definitions (currently just identity/metadata)             |
| `Environment.py`| `Env2D` and `Obstacle` — defines the space the robot moves in    |
| `Simulator.py`  | SDL2 window, ECS world, rendering, movement + collision system   |
| `Planner.py`    | Occupancy grid + BFS / Dijkstra / A* path planning               |

## Known limitations / next steps

- Planning is static: the path is computed once up front and not
  recomputed if obstacles change at runtime.
- The simulator window is fixed at 800x600; an `Env2D` with different
  dimensions will affect movement bounds but not resize the window.
- The controller drives straight toward each waypoint; it doesn't yet
  account for the robot's physical footprint beyond the fixed inflation
  radius used during planning.