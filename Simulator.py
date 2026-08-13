import math
import sdl2
import sdl2.ext

class Simulator:
    def __init__(self):
        pass

    def load_env(self, env):
        self.env = env
    
    def load_robot(self, robot):
        self.robot = robot

WHITE = sdl2.ext.Color(255, 255, 255)
RED = sdl2.ext.Color(255, 0, 0)
YELLOW = sdl2.ext.Color(255, 255, 0)

def rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    """AABB overlap test for two rectangles given as (x, y, width, height)."""
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)
        # obstacles to draw each frame, set via Simulator2D.load_env()
        self.obstacles = []
        # planned path waypoints [(x, y), ...] to draw each frame, set via
        # Simulator2D.set_path()
        self.path = []

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        for obstacle in self.obstacles:
            x, y, w, h = obstacle.rect()
            r, g, b = obstacle.color
            sdl2.ext.fill(self.surface, sdl2.ext.Color(r, g, b), (x, y, w, h))
        for (x, y) in self.path:
            size = 4
            sdl2.ext.fill(self.surface, YELLOW,
                          (int(x - size / 2), int(y - size / 2), size, size))
        super(SoftwareRenderer, self).render(components)


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


# threshold (px/step) below which heading is left unchanged, so the robot
# doesn't jitter its heading while nearly stationary. Module-level constant,
# NOT an instance attribute, because sdl2.ext.Entity tracks attributes by
# type, and a second bare float on the entity would collide with `angle`.
HEADING_DEADZONE = 0.05


class Heading(object):
    """Heading component. 0 deg = facing +x (right).
    Coordinate system is y-down, so positive angles rotate clockwise."""
    def __init__(self):
        super(Heading, self).__init__()
        self.angle = 0.0


class Robot(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.pen_down = False
        self.path = []
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.heading = Heading()

    def pen_down(self):
        self.pen_down = True

    def pen_up(self):
        self.pen_down = False

    def update_heading(self):
        """Point the robot's heading along its current velocity vector."""
        vx, vy = self.velocity.vx, self.velocity.vy
        if abs(vx) > HEADING_DEADZONE or abs(vy) > HEADING_DEADZONE:
            self.heading.angle = math.degrees(math.atan2(vy, vx))

    def center(self):
        sw, sh = self.sprite.size
        return self.sprite.x + sw // 2, self.sprite.y + sh // 2

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        # obstacles to collide against, set via Simulator2D.load_env()
        self.obstacles = []

    def _blocked(self, x, y, w, h):
        for obstacle in self.obstacles:
            ox, oy, ow, oh = obstacle.rect()
            if rects_overlap(x, y, w, h, ox, oy, ow, oh):
                return True
        return False

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size

            # move on each axis independently so the robot slides along
            # a wall/obstacle instead of fully stopping on diagonal contact
            new_x = sprite.x + int(velocity.vx)
            if not self._blocked(new_x, sprite.y, swidth, sheight):
                sprite.x = new_x

            new_y = sprite.y + int(velocity.vy)
            if not self._blocked(sprite.x, new_y, swidth, sheight):
                sprite.y = new_y

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight

            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight


class Simulator2D(Simulator):
    def __init__(self):
        super().__init__()
        sdl2.ext.init()
        self.window = sdl2.ext.Window("Simulator", size = (800, 600))
        self.window.show()

        self.world = sdl2.ext.World()

        self.movement = MovementSystem(0, 0, 800, 600)
        self.spriterenderer = SoftwareRenderer(self.window)

        self.world.add_system(self.movement)
        self.world.add_system(self.spriterenderer)

        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        robot_body = factory.from_color(WHITE, size=(20, 20))

        self.r1 = Robot(self.world, robot_body, 250, 250)
        self.world.robot = self.r1
        self.env = None

    def load_env(self, env):
        """Load an Environment (e.g. Env2D) into the simulator: wires up
        movement bounds, obstacle collision, and obstacle rendering."""
        self.env = env
        self.movement.minx = 0
        self.movement.miny = 0
        self.movement.maxx = env.width
        self.movement.maxy = env.height
        self.movement.obstacles = env.obstacles
        self.spriterenderer.obstacles = env.obstacles

    def set_path(self, waypoints):
        """Set the planned path (list of (x, y) world coords) to draw for
        debugging/visualization."""
        self.spriterenderer.path = list(waypoints) if waypoints else []

    
    def run(self, delay=0):
        # self.r1.velocity.vx = 1

        self.running = True
        # while self.running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                sdl2.ext.quit()
                return 0
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    self.r1.velocity.vy = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    self.r1.velocity.vy = 3
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.r1.velocity.vx = -3
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.r1.velocity.vx = 3
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.r1.velocity.vy = 0
                
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    self.r1.velocity.vx = 0
        if delay>0:
            sdl2.SDL_Delay(delay)
        self.world.process()

        self.r1.update_heading()
        self._draw_heading_indicator(self.r1)
        self.window.refresh()
        return 1

    def _draw_heading_indicator(self, robot, length=None, color=RED):
        """Draw a short line from the robot's center in its heading direction."""
        surface = self.window.get_surface()
        cx, cy = robot.center()
        if length is None:
            sw, sh = robot.sprite.size
            length = max(sw, sh)
        rad = math.radians(robot.heading.angle)
        x2 = int(cx + length * math.cos(rad))
        y2 = int(cy + length * math.sin(rad))
        sdl2.ext.line(surface, color, (cx, cy, x2, y2))