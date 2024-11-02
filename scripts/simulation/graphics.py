import pygame
from pygame.locals import *
from simulation import *
import os


class SimulationGraphic:
    def __init__(self) -> None:

        self.lights_cycle = [Direction.SOUTH]*20 + [None] * 5 +\
            [Direction.WEST]*20 + [None] * 5 +\
            [Direction.NORTH]*20 + [None] * 5 +\
            [Direction.EAST]*20 + [None] * 5
        self.step_counter = 0
        self.simulation: Simulation = Simulation(self.lights_cycle)
        self.start_time = pygame.time.get_ticks()
        self.lane_to_xy_map = {
            Direction.EAST: (500, 363),
            Direction.WEST: (295, 438),
            Direction.NORTH: (360, 295),
            Direction.SOUTH: (435, 505)
        }
        self.lane_dxy_map = {
            Direction.EAST: (20, 0),
            Direction.WEST: (-20, 0),
            Direction.NORTH: (0, -20),
            Direction.SOUTH: (0, 20)
        }

    def timer(self, timer_duration):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= timer_duration:
            self.start_time = pygame.time.get_ticks()
            self.simulation.step(self.step_counter)
            self.step_counter = (self.step_counter +
                                 1) % len(self.lights_cycle)

    def lane_to_xy(self, lane: Lane, i: int):
        base_xy = self.lane_to_xy_map[lane.location]
        d_xy = self.lane_dxy_map[lane.location]
        xy_cords = (base_xy[0] + d_xy[0]*i, base_xy[1] + d_xy[1] * i)
        return xy_cords

    def render_cars(self, surface) -> None:
        for lane in self.simulation.crossroad.in_lanes:
            for i, car in enumerate(lane.queue):
                pygame.draw.circle(surface, (0, 0, 255),
                                   self.lane_to_xy(lane, i), 10)

    def render_lights(self, surface) -> None:
        now_green_light = self.simulation.crossroad.lights_cycle[self.step_counter]

        for lane in self.simulation.crossroad.in_lanes:
            color = "green" if lane.location == now_green_light else "red"
            if now_green_light == None:
                now_yellow_light = self.yellow_light_loc()
                color = "yellow" if lane.location in now_yellow_light else "red"

            x, y = self.lane_to_xy(lane, -2)
            pygame.draw.circle(surface, color, (x, y), 10)

    def yellow_light_loc(self) -> list[Direction]:

        for i in range(1, 6):
            ret_prev = None
            ret_next = None
            prev_light = self.step_counter - i
            next_light = (self.step_counter + i) % len(self.lights_cycle)
            if self.lights_cycle[prev_light] != None and not ret_prev:
                ret_prev = self.lights_cycle[prev_light]
            if self.lights_cycle[next_light] != None and not ret_next:
                ret_next = self.lights_cycle[next_light]
        return ret_prev, ret_next


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

        self.background_image = pygame.image.load(
            "images\\crossroad_one_lane.jpg")
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
