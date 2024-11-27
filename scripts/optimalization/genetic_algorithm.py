import random
from typing import List, Tuple, Callable
from math import floor
from scripts.simulation.simulation import *
from copy import deepcopy


class GeneticAlgorithm:
    Genome = List[List[Crossroad.LightsTimes]]
    Population = List[Genome]
    FitnessFunc = Callable[[Genome], float]
    GenomeFunc = Callable[[], Genome]
    MutationFunc = Callable[[Genome], Genome]
    CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome]]

    def __init__(self,
                 population_size: int,
                 generate_genome: GenomeFunc,
                 fitness: FitnessFunc,
                 mutation: MutationFunc,
                 crossover: CrossoverFunc) -> None:
        self.size = population_size
        self.generate_genome = generate_genome
        self.fitness = fitness
        self.mutation = mutation
        self.crossover = crossover

    def generate_solutions(self) -> Population:
        return [self.generate_genome() for _ in range(self.size)]

    def selection(self,
                  sorted_solutions: Population
                  ) -> Population:
        solutions, weights = zip(*sorted_solutions)
        return tuple(random.choices(solutions,
                                    weights=weights,
                                    k=2))

    def sort_solutions(self,
                       solutions: Population
                       ) -> Population:
        sorted_solutions = [(solution, self.fitness(solution))
                            for solution in solutions]
        return sorted(sorted_solutions,
                      key=lambda x: x[1],
                      reverse=True)

    def elite_solutions(self,
                        sorted_solutions: Population,
                        percentage: float
                        ) -> Population:
        if percentage >= 1.0:
            raise ValueError("Elitism percentage must be in range [0,1.0)")
        elite_solutions_weights = sorted_solutions[:int(
            floor(percentage*len(sorted_solutions)))]

        if not elite_solutions_weights:
            return []
        elite_solutions, _ = zip(*elite_solutions_weights)

        return list(elite_solutions)

    def run_evolution(self, generations: int, elitism_perc: float = 0.0) -> Genome:
        newGeneration = self.generate_solutions()
        for i in range(generations):
            sorted_solutions = self.sort_solutions(newGeneration[:self.size])
            newGeneration = self.elite_solutions(
                sorted_solutions, elitism_perc)
            while (len(newGeneration) < self.size):
                parent1, parent2 = self.selection(sorted_solutions)
                children = self.crossover(parent1, parent2)
                for child in children:
                    self.mutation(child)
                    newGeneration += [child]
            print(f"generation {i} best solution: {sorted_solutions[0][1]}")
        return self.sort_solutions(newGeneration)[0]


class TrafficLightsOptGentetic:
    type LightsTimes = List[Dict[Direction, int]]
    type LightsPermutation = List[List[Direction]]

    def __init__(self) -> None:
        # To find neighbour easly light cycle can be represented as
        # list of times for each direction and
        # list of permutations specifying order of lights
        # this can be converted to lights_cycle (List[Direction])
        self.simulation = Simulation(turn_time=120, cycles=5)
        self.genetic_algorthm = GeneticAlgorithm(
            population_size=100,
            generate_genome=self.generate_genome,
            fitness=self.fitness,
            mutation=self.mutation,
            crossover=self.crossover
        )

    def generate_genome(self) -> GeneticAlgorithm.Genome:
        # TODO
        genome = []
        for _ in range(4):
            lights_times = {Direction.SOUTH: random.random(),
                            Direction.WEST: random.random(),
                            Direction.NORTH: random.random(),
                            Direction.EAST: random.random()}
            self.normalize(lights_times)
            lights_order = [Direction.SOUTH,
                            Direction.WEST,
                            Direction.NORTH,
                            Direction.EAST]
            random.shuffle(lights_order)
            genome.append([lights_times, lights_order])
        return genome

    def normalize(self, lights_times: Crossroad.LightsTimes) -> None:
        """Normalizes lights times inplace so they sum to 100

        Args:
            lights_times (Crossroad.LightsTimes): _description_

        Returns:
            None
        """
        for direction in lights_times.keys():
            lights_times[direction] = max(5, lights_times[direction])
        sum_times = sum(lights_times.values())

        for direction in lights_times.keys():
            lights_times[direction] = lights_times[direction] / \
                sum_times * 100

    def fitness(self, genome) -> int:
        """
        Evaluates solution

        Args:
            lights_cycle (List[Crossroad.LightsCycle]): Solution to evaluate

        Returns:
            int: score
        """
        return 100000000/self.simulation.run(genome)

    def mutation(self, genome) -> None:
        """
        mutate genome inplace

        Returns:
            None
        """
        r = random.random()
        # Swap permuation
        if r < 0.5:
            i = random.randint(0, 3)
            s1, s2 = random.randint(0, 3), random.randint(0, 3)
            genome[i][1][s1], genome[i][1][s2] = genome[i][1][s2], genome[i][1][s1]
        else:
            i = random.randint(0, 3)
            for dir in genome[i][0].keys():
                genome[i][0][dir] += random.gauss()*20
                self.normalize(genome[i][0])
        pass

    def crossover(self, parent1, parent2):
        alpha_lst = [-0.5, 1.5]
        children = []
        for alpha in alpha_lst:
            child = []
            for i in range(4):
                child_light_times = {
                    Direction.SOUTH: parent1[i][0][Direction.SOUTH]*(alpha) + parent2[i][0][Direction.SOUTH]*(alpha),
                    Direction.WEST: parent1[i][0][Direction.WEST]*(alpha) + parent2[i][0][Direction.WEST]*(alpha),
                    Direction.NORTH: parent1[i][0][Direction.NORTH]*(alpha) + parent2[i][0][Direction.NORTH]*(alpha),
                    Direction.EAST: parent1[i][0][Direction.EAST]*(alpha) + parent2[i][0][Direction.EAST]*(alpha),
                }
                self.normalize(child_light_times)
                child.append([child_light_times, deepcopy(parent1[i][1])])
            children.append(child)
        return children


if __name__ == "__main__":
    traffic_opt = TrafficLightsOptGentetic()
    opt = traffic_opt.genetic_algorthm.run_evolution(200, 0.1)
    print(opt)
