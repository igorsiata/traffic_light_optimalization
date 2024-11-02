from scripts.simulation.simulation import *
import random
import numpy as np


class SimulatedAnnealing:
    def __init__(self) -> None:
        self.lights_times = {Location.SOUTH: 20,
                             Location.WEST: 20,
                             Location.NORTH: 20,
                             Location.EAST: 20}
        self.lights_permutation = [Location.SOUTH,
                                   Location.WEST,
                                   Location.NORTH,
                                   Location.EAST]
        self.lights_cycle = self.generate_cycle(self.lights_times,
                                                self.lights_permutation)
        self.simulation = Simulation(self.lights_cycle, 100)

    def fitness(self, lights_cycle) -> int:
        return self.simulation.run(lights_cycle)

    def neigbour(self):
        direction_list = list(Location)
        add_to = random.choice(direction_list)
        direction_list.remove(add_to)
        remove_from = random.choice(direction_list)
        new_light_times = self.lights_times.copy()
        new_light_times[add_to] += 1
        new_light_times[remove_from] -= 1
        return new_light_times

    def generate_cycle(self, lights_times, lights_permutation):
        lights_cycle = []
        for i in range(4):
            direction = lights_permutation[i]
            lights_cycle += [direction] * \
                lights_times[direction] + [None]*5
        return lights_cycle

    def run(self):
        lowest_score = self.fitness(self.lights_cycle)
        temperature = 2
        alfa = 0.95
        while temperature > 0.001:
            new_light_times = self.neigbour()
            new_score = self.fitness(self.generate_cycle(
                new_light_times, self.lights_permutation))
            difference = new_score - lowest_score
            if difference < 0:
                lowest_score = new_score
                self.lights_cycle = new_light_times
                self.lights_times = new_light_times
            else:
                r = random.random()
                p = np.exp(-difference/temperature)
                if r < p:
                    lowest_score = new_score
                    self.lights_cycle = new_light_times
                    self.lights_times = new_light_times
            print(lowest_score)
            print(self.lights_times)
            temperature *= alfa


if __name__ == "__main__":

    optimaliztion = SimulatedAnnealing()
    optimaliztion.run()
    lights_times = {Location.SOUTH: 32,
                    Location.WEST: 8,
                    Location.NORTH: 32,
                    Location.EAST: 8}
    lights_permutation = [Location.SOUTH,
                          Location.WEST,
                          Location.NORTH,
                          Location.EAST]
    fit = optimaliztion.fitness(optimaliztion.generate_cycle(
        lights_times, lights_permutation))
    print(fit)
