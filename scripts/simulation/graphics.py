import pygame
from pygame.locals import *
from scripts.simulation.simulation import *
# from scripts.optimalization.simulated_annealing import *
from scripts.optimalization.genetic_algorithm import *
import os
import numpy as np


class SimulationGraphic:
    def __init__(self, lights_cycle) -> None:
        self.lights_cycle = lights_cycle
        self.step_counter = 0
        self.turn_time = 120
        self.simulation: Simulation = Simulation(self.turn_time)
        self.simulation.init_corssroad_params(lights_cycle)
        self.start_time = pygame.time.get_ticks()
        self.crossroad_to_xy = {
            0: (250, 250),
            1: (550, 250),
            2: (250, 550),
            3: (550, 550)
        }
        self.lane_to_xy_map = {
            Direction.EAST: (40, -25),
            Direction.WEST: (-40, 25),
            Direction.NORTH: (-25, -40),
            Direction.SOUTH: (25, 40)
        }
        self.lane_dxy_map = {
            Direction.EAST: (12, 0),
            Direction.WEST: (-12, 0),
            Direction.NORTH: (0, -12),
            Direction.SOUTH: (0, 12)
        }

    def timer(self, timer_duration):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= timer_duration:
            self.start_time = pygame.time.get_ticks()
            self.simulation.step(self.step_counter)
            self.step_counter = (self.step_counter +
                                 1) % self.turn_time

    def lane_to_xy(self, crossroad_id: int, lane_direction: Direction, i: int):
        crossroad_xy = self.crossroad_to_xy[crossroad_id]
        base_xy = self.lane_to_xy_map[lane_direction]
        d_xy = self.lane_dxy_map[lane_direction]
        d_xy = (d_xy[0]*i, d_xy[1]*i)
        xy_cords = tuple(np.add(np.add(crossroad_xy, base_xy), d_xy))
        return xy_cords

    def render_cars(self, surface) -> None:
        for c_id, crossroad in enumerate(self.simulation.crossroad_network.crossroad_network):
            for direction, in_lane in crossroad.in_lanes.items():
                for i, car in enumerate(in_lane.queue):
                    # print(c_id, direction)
                    pygame.draw.circle(surface, "lightblue",
                                       self.lane_to_xy(c_id, direction, i+2), 6)

    def render_lights(self, surface) -> None:
        for c_id, crossroad in enumerate(
                self.simulation.crossroad_network.crossroad_network):
            for cycle in crossroad.lights_cycle:
                if cycle[1] >= self.step_counter:
                    green_light_now = cycle[0]
                    break
            for direction in list(Direction):
                if green_light_now == None:
                    color = "yellow"
                elif green_light_now == direction:
                    color = "green"
                else:
                    color = "red"
                pygame.draw.circle(surface, color,
                                   self.lane_to_xy(c_id, direction, 0), 10)


class App:
    def __init__(self) -> None:
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 800, 800
        self.FPS = 60
        self.FramePerSec = pygame.time.Clock()
        self.simulation_graphics: SimulationGraphic

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.background_image = pygame.image.load(
            "images\\4waycrossroad.jpg")
        self._running = True
        return self._display_surf is not None

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False  # Zatrzymuje pętlę Pygame

    def on_loop(self):
        self.simulation_graphics.timer(10)

    def on_render(self):
        self._display_surf.blit(self.background_image, (0, 0))
        self.simulation_graphics.render_cars(self._display_surf)
        self.simulation_graphics.render_lights(self._display_surf)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()  # Zamyka tylko zasoby Pygame

    def on_execute(self):
        if not self.on_init():
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.FramePerSec.tick(self.FPS)
        self.on_cleanup()  # Wyczyść zasoby na końcu


if __name__ == "__main__":

    traffic_opt = TrafficLightsOptGentetic()
    opt = traffic_opt.genetic_algorthm.run_evolution(50, 0.1)
    cycle = opt[0]
    print(opt)
    theApp = App()
    theApp.simulation_graphics = SimulationGraphic(cycle)
    theApp.on_execute()
