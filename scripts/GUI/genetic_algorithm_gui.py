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
    
    def run_evolution_gui(self, generations: int, elitism_perc: float, update_progress: Callable[[int, float], None]) -> Tuple[List[Tuple[Dict[Direction, float], List[Direction]]], List[float]]:
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
            best_fitness_per_gen.append(sorted_population[0][1])  # Dodaj najlepszą wartość fitness do listy
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

        # Przekształcenie najlepszego rozwiązania w odpowiedni format
        best_solution_raw = sorted_population[0][0]  # Najlepszy genom
        best_solution = [(crossroad[0], crossroad[1]) for crossroad in best_solution_raw]

        return best_solution, best_fitness_per_gen





class TrafficLightsOptGentetic:
    type LightsTimes = List[Dict[Direction, int]]
    type LightsPermutation = List[List[Direction]]

    def __init__(self, population_size=100, mutation_prob=0.5, crossover_type="pmx", crossover_alpha=1.0, cycles = 5) -> None:
        self.simulation = Simulation(turn_time=120, cycles=cycles)
        self.crossover_type = crossover_type

        # Mapowanie nazw na odpowiednie funkcje
        crossover_funcs = {
            "pmx": self.pmx_crossover,
            "linear": lambda p1, p2: self.linear_crossover(p1, p2, crossover_alpha)
        }

        self.genetic_algorthm = GeneticAlgorithm(
            population_size=population_size,
            generate_genome=self.generate_genome,
            fitness=self.fitness,
            mutation=lambda genome: self.mutation(genome, mutation_prob),
            crossover=crossover_funcs[self.crossover_type]
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

    def mutation(self, genome, mutation_prob) -> None:
        """
        Mutuje genom. Może modyfikować czas świateł lub zamieniać kolejność kierunków.
        """
        if random.random() < mutation_prob:
            # Wybierz losowy indeks w genomie
            i = random.randint(0, len(genome) - 1)
            
            # Mutacja permutacji listy kierunków (jeśli istnieje lista na pozycji [1])
            if isinstance(genome[i][1], list) and len(genome[i][1]) > 1:
                genome[i][1] = random.sample(genome[i][1], len(genome[i][1]))

            # Mutacja czasów świateł
            for direction in genome[i][0]:
                genome[i][0][direction] += random.uniform(-5, 5)
            
            # Normalizacja czasów świateł
            self.normalize(genome[i][0])

    def pmx_crossover(self, parent1, parent2) -> Tuple:
        """ PMX (Partially Mapped Crossover) """
        import random
        point1 = random.randint(0, len(parent1) - 1)
        point2 = random.randint(point1, len(parent1) - 1)
        
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)

        for i in range(point1, point2):
            child1[i], child2[i] = parent2[i], parent1[i]

        return child1, child2
 
    def linear_crossover(self, parent1, parent2, alpha) -> Tuple:
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        for i in range(len(child1)):
            for direction in child1[i][0]:
                child1[i][0][direction] = alpha * parent1[i][0][direction] + (1 - alpha) * parent2[i][0][direction]
                child2[i][0][direction] = alpha * parent2[i][0][direction] + (1 - alpha) * parent1[i][0][direction]
            self.normalize(child1[i][0])
            self.normalize(child2[i][0])
        return child1, child2
    




if __name__ == "__main__":
    traffic_opt = TrafficLightsOptGentetic()
    opt = traffic_opt.genetic_algorthm.run_evolution(200, 0.1)
    print(opt)
