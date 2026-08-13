from Robot import Robot2D
from Environment import Env2D
from Simulator import Simulator2D
from Planner import plan_path
import time

# define robot such that, we can load sensor, or other processing details in it
robot = Robot2D()

# define environment: walls + a couple of obstacles to path around
env = Env2D()
env.add_border_walls(thickness=20)
env.add_obstacle(300, 150, 40, 300, color=(180, 60, 60))
env.add_obstacle(500, 350, 150, 40, color=(60, 120, 180))

sim = Simulator2D()

sim.load_env(env)
sim.load_robot(robot)

# --- Path planning -----------------------------------------------------
# Choose which search algorithm plans the route: "astar", "dijkstra", or "bfs"
ALGORITHM = "astar"

# goals = [(100, 100), (100, 200), (200, 200), (200, 100), (300, 300)]
goals = [(250, 250), (450, 300)]

start_pos = tuple(sim.r1.sprite.position)
full_path = []
leg_start = start_pos

for goal in goals:
    leg = plan_path(env, leg_start, goal, algorithm=ALGORITHM)
    if leg is None:
        print(f"WARNING: no path found to goal {goal}, skipping it")
        continue
    # avoid a duplicate point where one leg's end == next leg's start
    if full_path and leg[0] == full_path[-1]:
        leg = leg[1:]
    full_path.extend(leg)
    leg_start = goal

if not full_path:
    raise RuntimeError("No valid path could be planned to any goal.")

sim.set_path(full_path)  # draws the planned waypoints for visualization

# --- Waypoint-following control loop ------------------------------------
running = True

waypoint_idx = 0
WAYPOINT_TOLERANCE = 6  # px; how close counts as "reached" a waypoint

error_sum_x = 0
error_sum_y = 0

Kp = 0.01
Ki = 0.0001

start_time = time.time()
while running:
    x, y = sim.r1.sprite.position
    X, Y = full_path[waypoint_idx]

    error_x = x - X
    error_y = y - Y
    dist = (error_x ** 2 + error_y ** 2) ** 0.5

    if dist < WAYPOINT_TOLERANCE:
        waypoint_idx = (waypoint_idx + 1) % len(full_path)
        # reset the integral term so error from the previous leg doesn't
        # carry over and cause overshoot on the new one
        error_sum_x = 0
        error_sum_y = 0
        X, Y = full_path[waypoint_idx]
        error_x = x - X
        error_y = y - Y

    error_sum_x += error_x
    error_sum_y += error_y

    sim.r1.velocity.vx = -(Kp * error_x + Ki * error_sum_x)
    sim.r1.velocity.vy = -(Kp * error_y + Ki * error_sum_y)

    vx, vy = int(sim.r1.velocity.vx), int(sim.r1.velocity.vy)
    current_time = time.time()

    if current_time - start_time > 1:
        print("\nPosition:", x, y)
        print("Velocity:", vx, vy)
        print("Heading (deg):", round(sim.r1.heading.angle, 1))
        print("Waypoint:", waypoint_idx + 1, "/", len(full_path))
        start_time = current_time

    running = sim.run(delay=0)  # advances one time step; loop control stays with us