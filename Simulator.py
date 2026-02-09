import sdl2
import sdl2.ext

class Simulator:
    def __init__(self):
        pass

    def load_env(self, env):
        self.env = env
    
    def load_robot(self, robot):
        self.robot = robot


class Simulator2D(Simulator):
    def __init__(self):
        super().__init__()

    
    def run(self):
        sdl2.ext.init()
        self.window = sdl2.ext.Window("Simulator", size = (400, 300))
        self.window.show()

        self.running = True
        while self.running:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                    break
            self.window.refresh()
        sdl2.ext.quit()
        return 0
