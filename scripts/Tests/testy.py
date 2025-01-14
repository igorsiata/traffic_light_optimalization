import csv
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from scripts.optimalization.genetic_algorithm import TrafficLightsOptGentetic, Control

# Ścieżki plików
TESTS_FILE = "test_configurations.csv"
RESULTS_FILE = "test_results.csv"
FITNESS_HISTORY_FILE = "fitness_history.csv"

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

# Funkcja do wykonywania testów
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

        # Wykonaj każdy test
        for test_index, config in enumerate(configurations):
            population_size = int(config["population_size"])
            generations = int(config["generations"])
            elitism_perc = float(config["elitism_perc"])
            mutation_prob = float(config["mutation_prob"])
            crossover_type = config["crossover_type"]
            selection_type = config["selection_type"]
            alpha = float(config["alpha"])
            cycles = int(config["cycles"])

            print(f"Rozpoczynam test: {config}")

            for run in range(5):
                print(f"  Wykonanie {run + 1}/5")

                # Uruchom algorytm genetyczny
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

                # Zapis wyników
                writer.writerow([
                    population_size, generations, elitism_perc, mutation_prob,
                    crossover_type, selection_type, alpha, cycles,
                    fitness_history[-1], run + 1
                ])

                # Zapis historii fitness
                for generation, fitness in enumerate(fitness_history):
                    history_writer.writerow([test_index, run + 1, generation, fitness])

            print(f"Zakończono test: {config}\n")

if __name__ == "__main__":
    run_tests()
