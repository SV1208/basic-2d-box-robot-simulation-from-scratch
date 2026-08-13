# This will be used to make different type of Environments that could be started,
# and then a robot can be loaded into it and then we could drive.


class Obstacle:
    """A static, axis-aligned rectangular obstacle in the environment."""
    def __init__(self, x, y, width, height, color=(150, 150, 150)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color  # (r, g, b)

    def rect(self):
        """Return (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)


class Environment:
    def __init__(self):
        self.obstacles = []


class Env2D(Environment):
    def __init__(self, width=800, height=600):
        super().__init__()
        # Env dimensions. NOTE: these should match the simulator window size
        # (800x600 by default) since the simulator does not auto-resize its
        # window to fit the environment.
        self.width = width
        self.height = height

    def add_obstacle(self, x, y, width, height, color=(150, 150, 150)):
        """Add a rectangular obstacle. Returns the created Obstacle."""
        obstacle = Obstacle(x, y, width, height, color)
        self.obstacles.append(obstacle)
        return obstacle

    def add_border_walls(self, thickness=20, color=(100, 100, 100)):
        """Convenience: wall off the four edges of the environment."""
        self.add_obstacle(0, 0, self.width, thickness, color)  # top
        self.add_obstacle(0, self.height - thickness, self.width, thickness, color)  # bottom
        self.add_obstacle(0, 0, thickness, self.height, color)  # left
        self.add_obstacle(self.width - thickness, 0, thickness, self.height, color)  # right

    def clear_obstacles(self):
        self.obstacles = []