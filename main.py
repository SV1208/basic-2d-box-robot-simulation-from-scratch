from Robot import Robot2D
from Environment import Env2D
from Simulator import Simulator2D

robot = Robot2D()
env = Env2D()
sim = Simulator2D()

sim.load_env(env)
sim.load_robot(robot)

sim.run()




