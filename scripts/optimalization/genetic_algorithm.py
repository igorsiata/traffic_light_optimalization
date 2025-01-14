import random
from typing import List, Tuple, Callable
from math import floor
from scripts.simulation.simulation import *
from copy import deepcopy


class Control:
    def __init__(self):
        self.stop = False


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
                 crossover: CrossoverFunc,
                 selection,
                 control: Control) -> None:
        self.size = population_size
        self.generate_genome = generate_genome
        self.fitness = fitness
        self.mutation = mutation
        self.crossover = crossover
        self.selection = selection
        self.control = control

    def generate_solutions(self) -> Population:
        return [self.generate_genome() for _ in range(self.size)]

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

    def run_evolution_gui(self,
                          generations: int,
                          elitism_perc: float,
                          update_progress: Callable[[int, float], None]
                          ) -> Tuple[List[Tuple[Dict[Direction, float], List[Direction]]], List[float]]:
        """
        Przystosowana funkcja run_evolution do GUI.

        Args:
            generations (int): Liczba generacji.
            elitism_perc (float): Procent elityzmu.
            update_progress (Callable): Funkcja aktualizująca pasek postępu.

        Returns:
            Tuple: Najlepszy genom (z czasami i kolejnością świateł) i lista wartości fitness z każdej generacji.
        """
        population = self.generate_solutions()
        best_fitness_per_gen = []
        for generation in range(generations):
            sorted_population = self.sort_solutions(population)
            # Dodaj najlepszą wartość fitness do listy
            best_fitness_per_gen.append(sorted_population[0][1])
            elite = self.elite_solutions(sorted_population, elitism_perc)
            next_generation = list(elite)
            while len(next_generation) < self.size:
                parent1, parent2 = self.selection(sorted_population)
                children = self.crossover(parent1, parent2)
                for child in children:
                    self.mutation(child)
                    next_generation.append(child)
            population = next_generation[:self.size]
            # Aktualizacja paska postępu w GUI
            update_progress(generation + 1, best_fitness_per_gen[-1])
            if self.control.stop == True:
                best_solution_raw = sorted_population[0][0]  # Najlepszy genom
                best_solution = [(crossroad[0], crossroad[1])
                                 for crossroad in best_solution_raw]
                return best_solution, best_fitness_per_gen

        # Przekształcenie najlepszego rozwiązania w odpowiedni format
        best_solution_raw = sorted_population[0][0]  # Najlepszy genom
        best_solution = [(crossroad[0], crossroad[1])
                         for crossroad in best_solution_raw]
        return best_solution, best_fitness_per_gen


class TrafficLightsOptGentetic:
    type LightsTimes = List[Dict[Direction, int]]
    type LightsPermutation = List[List[Direction]]

    def __init__(self,
                 control: Control,
                 population_size=100,
                 mutation_prob=0.5,
                 crossover_type="linear",
                 selection_type="wagowo",
                 crossover_alpha=1.0,
                 cycles=5) -> None:
        # To find neighbour easly light cycle can be represented as
        # list of times for each direction and
        # list of permutations specifying order of lights
        # this can be converted to lights_cycle (List[Direction])
        self.simulation = Simulation(
            turn_time=120, cycles=cycles)
        self.cycles = cycles
        self.crossover_type = crossover_type
        self.selection_type = selection_type
        # Mapowanie nazw na odpowiednie funkcje
        crossover_funcs = {
            "blx": lambda p1, p2: self.blx_alpha_crossover(p1, p2, crossover_alpha),
            "linear": lambda p1, p2: self.linear_crossover(p1, p2, crossover_alpha)
        }
        selection_funcs = {
            "ranking": lambda sorted_solutions: self.selection_ranking(sorted_solutions),
            "wagowo": lambda sorted_solutions: self.selection_weights(sorted_solutions),
        }
        self.genetic_algorthm = GeneticAlgorithm(
            control=control,
            population_size=population_size,
            generate_genome=self.generate_genome,
            fitness=self.fitness,
            mutation=lambda genome: self.mutation(genome, mutation_prob),
            crossover=crossover_funcs[self.crossover_type],
            selection=selection_funcs[self.selection_type]
        )

    def generate_genome(self) -> GeneticAlgorithm.Genome:

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
        return (1000000)/self.simulation.run(genome)

    def mutation(self, genome, mutation_prob) -> None:
        """
        mutate genome inplace

        Returns:
            None
        """
        # Swap permuation
        if random.random() < mutation_prob:
            # mutate direction order
            i = random.randint(0, 3)
            s1, s2 = random.randint(0, 3), random.randint(0, 3)
            genome[i][1][s1], genome[i][1][s2] = genome[i][1][s2], genome[i][1][s1]

            # mutate lights times
            i = random.randint(0, 3)
            for dir in genome[i][0].keys():
                genome[i][0][dir] += random.gauss()*4
                self.normalize(genome[i][0])
        pass

    def blx_alpha_crossover(self, parent1, parent2, alpha) -> Tuple:
        """ BLX """
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        for i in range(len(child1)):
            for direction in child1[i][0]:
                norm = abs(parent1[i][0][direction] - parent2[i][0][direction])
                child1[i][0][direction] = min(
                    parent1[i][0][direction], parent2[i][0][direction]) - alpha*norm
                child2[i][0][direction] = max(
                    parent1[i][0][direction], parent2[i][0][direction]) + alpha*norm
            self.normalize(child1[i][0])
            self.normalize(child2[i][0])

        return child1, child2

    def linear_crossover(self, parent1, parent2, alpha) -> Tuple:
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        for i in range(len(child1)):
            for direction in child1[i][0]:
                child1[i][0][direction] = alpha * parent1[i][0][direction] + \
                    (1 - alpha) * parent2[i][0][direction]
                child2[i][0][direction] = alpha * parent2[i][0][direction] + \
                    (1 - alpha) * parent1[i][0][direction]
            self.normalize(child1[i][0])
            self.normalize(child2[i][0])
        return child1, child2

    def selection_weights(self,
                          sorted_solutions
                          ):
        solutions, weights = zip(*sorted_solutions)
        return tuple(random.choices(solutions,
                                    weights=weights,
                                    k=2))

    def selection_ranking(self,
                          sorted_solutions
                          ):
        solutions, weights = zip(*sorted_solutions)
        weights = [i for i in range(len(solutions), 0, -1)]
        return tuple(random.choices(solutions,
                                    weights=weights,
                                    k=2))


if __name__ == "__main__":
    traffic_opt = TrafficLightsOptGentetic()
    opt = traffic_opt.genetic_algorthm.run_evolution(200, 0.1)
    print(opt)
