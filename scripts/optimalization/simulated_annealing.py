from scripts.simulation.simulation import *
import random
import numpy as np
from copy import deepcopy


class SimulatedAnnealing:
    type LightsTimes = List[Dict[Direction, int]]
    type LightsPermutation = List[List[Direction]]

    def __init__(self) -> None:
        # To find neighbour easly light cycle can be represented as
        # list of times for each direction and
        # list of permutations specifying order of lights
        # this can be converted to lights_cycle (List[Direction])
        self.lights_times: \
            SimulatedAnnealing.LightsTimes = [{Direction.SOUTH: 20,
                                               Direction.WEST: 20,
                                               Direction.NORTH: 20,
                                               Direction.EAST: 20}
                                              for _ in range(4)]
        self.lights_permutation: \
            SimulatedAnnealing.LightsPermutation = [[Direction.SOUTH,
                                                     Direction.WEST,
                                                     Direction.NORTH,
                                                     Direction.EAST]
                                                    for _ in range(4)]
        self.lights_cycle: \
            List[Crossroad.LightsCycle] = self.generate_cycle(self.lights_times,
                                                              self.lights_permutation)
        self.simulation = Simulation(100, 20)

    def fitness(self, lights_cycle: List[Crossroad.LightsCycle]) -> int:
        """
        Evaluates solution

        Args:
            lights_cycle (List[Crossroad.LightsCycle]): Solution to evaluate

        Returns:
            int: score
        """
        for i, crossroad in enumerate(self.simulation.crossroad_network.crossroad_network):
            crossroad.lights_cycle = lights_cycle[i]
        return self.simulation.run()/100000

    def neigbour(self) -> LightsTimes:
        """
        Finds random solution in neighbourhood of current one

        Returns:
            SimulatedAnnealing.LightsTimes: light times of neighbour solution
        """
        new_light_times = deepcopy(self.lights_times)
        crossroad_id = random.randint(0, 3)
        direction_list = list(Direction)
        add_to = random.choice(direction_list)
        direction_list.remove(add_to)
        remove_from = random.choice(direction_list)
        if new_light_times[crossroad_id][remove_from] <= 0:
            return self.neigbour()
        new_light_times[crossroad_id][add_to] += 1
        new_light_times[crossroad_id][remove_from] -= 1
        return new_light_times

    def generate_cycle(self,
                       lights_times: LightsTimes,
                       lights_permutation: LightsPermutation
                       ) -> List[Crossroad.LightsCycle]:
        """
        Generates light cycle based on light times and lights permutation.

        Args:
            lights_times (LightsTimes)
            lights_permutation (LightsPermutation)

        Returns:
            List[Crossroad.LightsCycle]
        """
        lights_cycle_lst = []
        for crossraod_id in range(4):
            lights_cycle = []
            for direction in lights_permutation[crossraod_id]:
                lights_cycle += [direction] * \
                    lights_times[crossraod_id][direction] + [None]*5
            lights_cycle_lst.append(lights_cycle)
        return lights_cycle_lst

    def run(self) -> List[Crossroad.LightsCycle]:
        """
        Runs simulated Annealing and returns best solution

        Returns:
            List[Crossroad.LightsCycle]: _description_
        """
        lowest_score = self.fitness(self.lights_cycle)
        temperature = 1
        alfa = 0.996
        while temperature > 0.0001:
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

            temperature *= alfa
        print(self.lights_times)
        return self.lights_cycle


if __name__ == "__main__":

    optimaliztion = SimulatedAnnealing()
    optimaliztion.run()
