# modular structure
# using Robot class, make the robot body, that can run


class Robot:
    def __init__(self):
        self.index = 1

class Robot2D(Robot):
    def __init__(self, name = "Robo1"):
        super().__init__()
        self.name = name


