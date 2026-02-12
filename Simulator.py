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

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


class Robot(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
    
    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

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

        movement = MovementSystem(0, 0, 800, 600)
        spriterenderer = SoftwareRenderer(self.window)

        self.world.add_system(movement)
        self.world.add_system(spriterenderer)

        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        robot_body = factory.from_color(WHITE, size=(20, 20))

        self.r1 = Robot(self.world, robot_body, 250, 250)

    
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
                sdl2.SDL_Delay(10)
            self.world.process()
        return 1
