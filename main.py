from Robot import Robot2D
from Environment import Env2D
from Simulator import Simulator2D

# define robot such that, we can load sensor, or other processing details in it
robot = Robot2D()


# define environment such t
env = Env2D()

sim = Simulator2D()

sim.load_env(env)
sim.load_robot(robot)


running = True
count = 0


goals = [(100,100), (100,200), (200, 200), (200,100)]
# goals = [(100,100)]
id = 0

error_sum_x = 0
error_sum_y = 0

Kp = 0.01
Ki = 0.0001 

import time
start_time = time.time()
while running:
    x, y = sim.r1.sprite.position
    X, Y = goals[id]
    error_x = x-X
    error_y = y-Y
    if (error_x, error_y) == (0,0):
        id+=1
        id = id%len(goals)

    error_sum_x += error_x
    error_sum_y += error_y

    sim.r1.velocity.vx = -(Kp*error_x + Ki*error_sum_x) 
    sim.r1.velocity.vy = -(Kp*error_y + Ki*error_sum_y)

    # sim.r1.velocity.vx = 0.1
    # sim.r1.velocity.vy = 0.1


    vx, vy = int(sim.r1.velocity.vx), int(sim.r1.velocity.vy)
    current_time = time.time()

    if (current_time-start_time > 1):
        print("\nPostion:",x,y)
        print("Velocity:",vx, vy )
        print("Heading (deg):", round(sim.r1.heading.angle, 1))
        start_time = current_time        

    running = sim.run(delay=0) # it should run only one time step, and not the whole loop, so that loop control is over us