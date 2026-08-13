# Path planning: turns an Environment's obstacles into an occupancy grid,
# then finds a path between two world-coordinate points using one of
# several classic search algorithms (BFS, Dijkstra, A*).

import heapq
import math
from collections import deque


def _rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


class Grid:
    """Occupancy grid built by rasterizing an Environment's obstacles.

    Obstacles are inflated by `robot_radius` before rasterizing, so a path
    that only touches free cells keeps the robot's body clear of walls
    instead of just its center point.
    """

    def __init__(self, env, cell_size=20, robot_radius=10):
        self.cell_size = cell_size
        self.cols = max(1, env.width // cell_size)
        self.rows = max(1, env.height // cell_size)
        self.blocked = set()

        for obstacle in env.obstacles:
            ox, oy, ow, oh = obstacle.rect()
            ox -= robot_radius
            oy -= robot_radius
            ow += 2 * robot_radius
            oh += 2 * robot_radius
            for row in range(self.rows):
                for col in range(self.cols):
                    cx, cy = col * cell_size, row * cell_size
                    if _rects_overlap(cx, cy, cell_size, cell_size, ox, oy, ow, oh):
                        self.blocked.add((col, row))

    def in_bounds(self, cell):
        col, row = cell
        return 0 <= col < self.cols and 0 <= row < self.rows

    def is_free(self, cell):
        return self.in_bounds(cell) and cell not in self.blocked

    def world_to_cell(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)

    def cell_to_world(self, cell):
        col, row = cell
        return (col + 0.5) * self.cell_size, (row + 0.5) * self.cell_size

    def neighbors(self, cell):
        col, row = cell
        steps = [(-1, 0), (1, 0), (0, -1), (0, 1),
                 (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dc, dr in steps:
            n = (col + dc, row + dr)
            if not self.is_free(n):
                continue
            if dc != 0 and dr != 0:
                # don't let the path cut diagonally between two blocked
                # cells (that would clip a corner)
                if not self.is_free((col + dc, row)) or not self.is_free((col, row + dr)):
                    continue
            cost = math.sqrt(2) if dc != 0 and dr != 0 else 1.0
            yield n, cost


def _reconstruct(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def bfs(grid, start, goal):
    """Breadth-first search. Ignores movement cost; finds a path in the
    fewest number of cell-hops, not necessarily the geometrically shortest."""
    if not grid.is_free(start) or not grid.is_free(goal):
        return None
    frontier = deque([start])
    came_from = {}
    visited = {start}
    while frontier:
        current = frontier.popleft()
        if current == goal:
            return _reconstruct(came_from, current)
        for nxt, _cost in grid.neighbors(current):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = current
                frontier.append(nxt)
    return None


def dijkstra(grid, start, goal):
    """Uniform-cost search. Finds the true shortest path by travel cost,
    but explores in all directions equally (no goal-directed heuristic)."""
    if not grid.is_free(start) or not grid.is_free(goal):
        return None
    frontier = [(0.0, start)]
    came_from = {}
    cost_so_far = {start: 0.0}
    while frontier:
        cost, current = heapq.heappop(frontier)
        if current == goal:
            return _reconstruct(came_from, current)
        if cost > cost_so_far.get(current, float("inf")):
            continue
        for nxt, step_cost in grid.neighbors(current):
            new_cost = cost_so_far[current] + step_cost
            if new_cost < cost_so_far.get(nxt, float("inf")):
                cost_so_far[nxt] = new_cost
                came_from[nxt] = current
                heapq.heappush(frontier, (new_cost, nxt))
    return None


def _heuristic(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def astar(grid, start, goal):
    """Dijkstra + a straight-line heuristic toward the goal, so it explores
    far fewer cells than plain Dijkstra while still finding a shortest path."""
    if not grid.is_free(start) or not grid.is_free(goal):
        return None
    frontier = [(0.0, start)]
    came_from = {}
    cost_so_far = {start: 0.0}
    while frontier:
        _priority, current = heapq.heappop(frontier)
        if current == goal:
            return _reconstruct(came_from, current)
        for nxt, step_cost in grid.neighbors(current):
            new_cost = cost_so_far[current] + step_cost
            if new_cost < cost_so_far.get(nxt, float("inf")):
                cost_so_far[nxt] = new_cost
                priority = new_cost + _heuristic(nxt, goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current
    return None


ALGORITHMS = {
    "bfs": bfs,
    "dijkstra": dijkstra,
    "astar": astar,
}


def _has_line_of_sight(grid, p1, p2, samples=None):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if samples is None:
        samples = max(2, int(dist / (grid.cell_size / 2)))
    for i in range(samples + 1):
        t = i / samples
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        if not grid.is_free(grid.world_to_cell(x, y)):
            return False
    return True


def _smooth(grid, waypoints):
    """Greedy line-of-sight smoothing: drop intermediate waypoints whenever
    a straight line to a farther one stays clear of obstacles. Turns a
    staircase-y grid path into a small number of straight segments."""
    if len(waypoints) <= 2:
        return waypoints
    smoothed = [waypoints[0]]
    i = 0
    while i < len(waypoints) - 1:
        j = len(waypoints) - 1
        while j > i + 1 and not _has_line_of_sight(grid, waypoints[i], waypoints[j]):
            j -= 1
        smoothed.append(waypoints[j])
        i = j
    return smoothed


def plan_path(env, start, goal, algorithm="astar", cell_size=20, robot_radius=10, smooth=True):
    """
    Plan a path from `start` to `goal` (both (x, y) world coordinates)
    through `env`, avoiding its obstacles.

    algorithm: one of "bfs", "dijkstra", "astar"
    Returns a list of (x, y) world-coordinate waypoints (start and goal are
    the first/last entries), or None if no path exists (e.g. goal is
    unreachable or inside an obstacle).
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm '{algorithm}'. Choose from {list(ALGORITHMS)}.")

    grid = Grid(env, cell_size=cell_size, robot_radius=robot_radius)
    start_cell = grid.world_to_cell(*start)
    goal_cell = grid.world_to_cell(*goal)

    cell_path = ALGORITHMS[algorithm](grid, start_cell, goal_cell)
    if cell_path is None:
        return None

    waypoints = [grid.cell_to_world(cell) for cell in cell_path]
    # snap the endpoints to the exact requested start/goal instead of cell centers
    waypoints[0] = tuple(start)
    waypoints[-1] = tuple(goal)

    if smooth:
        waypoints = _smooth(grid, waypoints)

    return waypoints