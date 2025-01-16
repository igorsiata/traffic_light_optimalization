import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from scripts.optimalization.genetic_algorithm import TrafficLightsOptGentetic, Control

# Ścieżki plików
TESTS_FILE = "test_configurations.csv"
RESULTS_FILE = "test_results2.csv"
FITNESS_HISTORY_FILE = "fitness_history2.csv"

# Funkcja do generowania pliku z konfiguracjami testów
def generate_test_configurations():
    with open(TESTS_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Nagłówki kolumn
        writer.writerow(["population_size", "generations", "elitism_perc", "mutation_prob", "crossover_type", "selection_type", "alpha", "cycles"])
        
        # Przykładowe konfiguracje
        test_cases = [
            [50, 20, 0.1, 0.5, "blx", "ranking", 1.5, 5],
            [100, 50, 0.2, 0.3, "linear", "wagowo", 1.0, 10],
            [200, 100, 0.05, 0.7, "blx", "wagowo", 2.0, 7],
        ]

        # Zapis konfiguracji
        writer.writerows(test_cases)

# Funkcja do uruchamiania pojedynczego testu
def execute_test(test_index, config, run):
    population_size = int(config["population_size"])
    generations = int(config["generations"])
    elitism_perc = float(config["elitism_perc"])
    mutation_prob = float(config["mutation_prob"])
    crossover_type = config["crossover_type"]
    selection_type = config["selection_type"]
    alpha = float(config["alpha"])
    cycles = int(config["cycles"])

    control = Control()
    optimizer = TrafficLightsOptGentetic(
        control=control,
        population_size=population_size,
        mutation_prob=mutation_prob,
        crossover_type=crossover_type,
        selection_type=selection_type,
        crossover_alpha=alpha,
        cycles=cycles
    )

    best_solution, fitness_history = optimizer.genetic_algorthm.run_evolution_gui(
        generations, elitism_perc, lambda gen, fitness: None
    )
    
    results = {
        "test_index": test_index,
        "run": run,
        "config": config,
        "best_fitness": fitness_history[-1],
        "fitness_history": fitness_history,
    }
    return results

# Funkcja do wykonywania testów wieloprocesowo
def run_tests():
    if not os.path.exists(TESTS_FILE):
        print(f"Plik {TESTS_FILE} nie istnieje. Generuję przykładowe konfiguracje testów.")
        generate_test_configurations()

    # Wczytaj konfiguracje testów
    with open(TESTS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        configurations = list(reader)

    # Przygotowanie do zapisu wyników
    with open(RESULTS_FILE, mode='w', newline='') as results_file, \
         open(FITNESS_HISTORY_FILE, mode='w', newline='') as history_file:
        writer = csv.writer(results_file)
        history_writer = csv.writer(history_file)

        # Nagłówki wyników
        writer.writerow(["population_size", "generations", "elitism_perc", "mutation_prob", "crossover_type", "selection_type", "alpha", "cycles", "best_fitness", "run"])

        # Nagłówki historii fitness
        history_writer.writerow(["test_index", "run", "generation", "fitness"])

        # Lista zadań do wykonania
        tasks = []
        with ProcessPoolExecutor(max_workers=8) as executor:
            for test_index, config in enumerate(configurations):
                for run in range(5):
                    tasks.append(executor.submit(execute_test, test_index, config, run + 1))

            for future in as_completed(tasks):
                result = future.result()
                test_index = result["test_index"]
                run = result["run"]
                config = result["config"]
                best_fitness = result["best_fitness"]
                fitness_history = result["fitness_history"]

                # Zapis wyników
                writer.writerow([
                    config["population_size"], config["generations"], config["elitism_perc"], config["mutation_prob"],
                    config["crossover_type"], config["selection_type"], config["alpha"], config["cycles"],
                    best_fitness, run
                ])

                # Zapis historii fitness
                for generation, fitness in enumerate(fitness_history):
                    history_writer.writerow([test_index, run, generation, fitness])

                print(f"Zakończono test {test_index}, uruchomienie {run}")

if __name__ == "__main__":
    run_tests()
