import pygame
from pygame.locals import *
from objects import *
import os


class SimulationGraphic:
    def __init__(self) -> None:
        self.car_image = pygame.image.load("images\car_yellow.png")
        self.simulation = Simulation(FourDirectionTwoLaneCrossroad)
        self.start_time = pygame.time.get_ticks()
        self.lane_to_xy_map = {
            Location.EAST: {Turn.LEFT: (520, 370),
                            Turn.RIGHT: (520, 323),
                            Turn.FORWARD: (520, 323)},
            Location.WEST: {Turn.LEFT: (275, 425),
                            Turn.RIGHT: (275, 475),
                            Turn.FORWARD: (275, 476)},
            Location.NORTH: {Turn.LEFT: (370, 275),
                             Turn.RIGHT: (320, 275),
                             Turn.FORWARD: (320, 275)},
            Location.SOUTH: {Turn.LEFT: (420, 525),
                             Turn.RIGHT: (470, 525),
                             Turn.FORWARD: (470, 525)}
        }
        self.lane_dxy_map = {
            Location.EAST: (20, 0),
            Location.WEST: (-20, 0),
            Location.NORTH: (0, -20),
            Location.SOUTH: (0, 20)
        }

    def timer(self, timer_duration):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= timer_duration:
            self.start_time = pygame.time.get_ticks()
            self.simulation.step()

    def lane_to_xy(self, lane: Lane, i: int):
        base_xy = self.lane_to_xy_map[lane.location][lane.possible_turns[0]]
        d_xy = self.lane_dxy_map[lane.location]
        xy_cords = (base_xy[0] + d_xy[0]*i, base_xy[1] + d_xy[1] * i)
        return xy_cords

    def render_cars(self, surface) -> None:
        for lane in self.simulation.crossroad.lanes:
            for i, car in enumerate(lane.queue):
                pygame.draw.circle(surface, (0, 0, 255),
                                   self.lane_to_xy(lane, i), 10)

    def render_lights(self, surface) -> None:
        for lane in self.simulation.crossroad.lanes:
            color = (0, 255, 0) if lane.green_light else (255, 0, 0)
            x, y = self.lane_to_xy(lane, -2)
            pygame.draw.circle(surface, color, (x, y), 10)


class App:
    def __init__(self) -> None:
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 800, 800
        self.FPS = 60
        self.FramePerSec = pygame.time.Clock()
        self.simulation_graphics = SimulationGraphic()

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.background_image = pygame.image.load("images\crossroad.jpg")
        self._running = True
        return self._display_surf is not None

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.simulation_graphics.timer(100)

    def on_render(self):
        self._display_surf.blit(self.background_image, (0, 0))
        self.simulation_graphics.render_cars(self._display_surf)
        self.simulation_graphics.render_lights(self._display_surf)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.FramePerSec.tick(self.FPS)
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
