import pygame
from pygame.locals import *
from simulation import *
import os


class SimulationGraphic:
    def __init__(self) -> None:

        self.lights_cycle = [Location.SOUTH]*20 + [None] * 5 +\
            [Location.WEST]*20 + [None] * 5 +\
            [Location.NORTH]*20 + [None] * 5 +\
            [Location.EAST]*20 + [None] * 5
        self.step_counter = 0
        self.simulation: Simulation = Simulation(self.lights_cycle)
        self.start_time = pygame.time.get_ticks()
        self.lane_to_xy_map = {
            Location.EAST: (500, 363),
            Location.WEST: (295, 438),
            Location.NORTH: (360, 295),
            Location.SOUTH: (435, 505)
        }
        self.lane_dxy_map = {
            Location.EAST: (20, 0),
            Location.WEST: (-20, 0),
            Location.NORTH: (0, -20),
            Location.SOUTH: (0, 20)
        }

    def generate_cycle(self, lights_times, lights_permutation):
        lights_cycle = []
        for i in range(4):
            direction = lights_permutation[i]
            lights_cycle += [direction] * \
                lights_times[direction] + [None]*5
        return lights_cycle

    def update_lights_cycle(self):

        lights_times = {Location.SOUTH: 27,
                        Location.WEST: 10,
                        Location.NORTH: 30,
                        Location.EAST: 13}
        lights_permutation = [Location.SOUTH,
                              Location.WEST,
                              Location.NORTH,
                              Location.EAST]
        self.lights_cycle = self.generate_cycle(
            lights_times, lights_permutation)

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

    def yellow_light_loc(self) -> list[Location]:

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
