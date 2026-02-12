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
while running:
    x, y = sim.r1.sprite.position
    vx, vy = sim.r1.velocity.vx, sim.r1.velocity.vy
    if count>100:
        count = 0
        print("\nPostion:",x,y)
        print("Velocity:",vx, vy )
    count+=0.001

    running = sim.run(delay=10) # it should run only one time step, and not the whole loop, so that loop control is over us


