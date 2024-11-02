from scripts.simulation.simulation import *
import random
import numpy as np
from copy import deepcopy


class SimulatedAnnealing:
    def __init__(self) -> None:
        self.lights_times = [{Direction.SOUTH: 20,
                             Direction.WEST: 20,
                             Direction.NORTH: 20,
                             Direction.EAST: 20} for _ in range(4)]
        self.lights_permutation = [[Direction.SOUTH,
                                   Direction.WEST,
                                   Direction.NORTH,
                                   Direction.EAST]for _ in range(4)]
        self.lights_cycle = self.generate_cycle(self.lights_times,
                                                self.lights_permutation)
        self.simulation = Simulation(100, 50)

    def fitness(self, lights_cycle) -> int:
        for i, crossroad in enumerate(self.simulation.crossroad_network.crossroad_network):
            crossroad.lights_cycle = lights_cycle[i]
        return self.simulation.run()

    def neigbour(self):
        new_light_times = deepcopy(self.lights_times)
        crossroad_id = random.randint(0, 3)
        direction_list = list(Direction)
        add_to = random.choice(direction_list)
        direction_list.remove(add_to)
        remove_from = random.choice(direction_list)
        print(new_light_times[crossroad_id])
        new_light_times[crossroad_id][add_to] += 1
        new_light_times[crossroad_id][remove_from] -= 1
        return new_light_times

    def generate_cycle(self, lights_times, lights_permutation):
        lights_cycle_lst = []
        for crossraod_id in range(4):
            lights_cycle = []
            for direction in lights_permutation[crossraod_id]:
                lights_cycle += [direction] * \
                    lights_times[crossraod_id][direction] + [None]*5
            lights_cycle_lst.append(lights_cycle)
        return lights_cycle_lst

    def run(self):
        lowest_score = self.fitness(self.lights_cycle)
        temperature = 2
        alfa = 0.95
        while temperature > 0.001:
            new_lights_times = self.neigbour()
            new_lights_cycle = self.generate_cycle(
                new_lights_times, self.lights_permutation)
            new_score = self.fitness(new_lights_cycle)
            difference = new_score - lowest_score
            r = random.random()
            p = np.exp(-difference/temperature)
            if difference < 0 or r < p:
                lowest_score = new_score
                self.lights_cycle = new_lights_cycle
                self.lights_times = new_lights_times

            print(difference)
            print(self.lights_times)
            temperature *= alfa


if __name__ == "__main__":

    optimaliztion = SimulatedAnnealing()
    optimaliztion.run()
