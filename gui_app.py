import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from genetic_algorithm import TrafficLightsOptGentetic

def run_genetic_algorithm(population_size, generations, elitism_perc, mutation_prob, crossover_type, alpha, cycles, progress_bar):
    """ Uruchamia algorytm genetyczny i aktualizuje GUI w głównym wątku. """
    
    traffic_opt = TrafficLightsOptGentetic(
        population_size=population_size,
        mutation_prob=mutation_prob,
        crossover_type=crossover_type,
        crossover_alpha=alpha,
        cycles=cycles
    )

    def update_progress(gen, best_fitness):
        # Aktualizacja paska postępu w głównym wątku (teraz pasek postępu jest usunięty)
        print(f"Generacja {gen}: najlepsze fitness = {best_fitness}")

    def run_algorithm_inner():
        # Uruchamiamy algorytm i zbieramy wyniki
        best_solution, fitness_history = traffic_opt.genetic_algorthm.run_evolution_gui(
            generations, elitism_perc, update_progress
        )
        # Po zakończeniu uruchamiania algorytmu wyświetlamy wykres
        root.after(0, lambda: show_results(fitness_history))

    # Uruchamiamy algorytm w nowym wątku
    threading.Thread(target=run_algorithm_inner).start()

def show_results(scores):
    """ Wyświetla wykres fitness. """
    plt.figure(figsize=(8, 6))
    plt.plot(scores, marker='o', linestyle='-', color='b')
    plt.title("Postęp optymalizacji")
    plt.xlabel("Generacja")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.show()

def start_algorithm():
    """ Zbiera dane z GUI i uruchamia algorytm. """
    try:
        population_size = int(pop_size_entry.get())
        generations = int(gen_entry.get())
        elitism_perc = float(elitism_entry.get())
        mutation_prob = float(mutation_entry.get())
        crossover_type = crossover_type_combo.get()
        alpha = float(alpha_entry.get())
        cycles = int(cycles_entry.get())  # Dodano liczbę cykli

        if not (0 <= elitism_perc <= 1):
            raise ValueError("Procent elityzmu musi być w przedziale 0-1.")
        
        # Pasek postępu został usunięty, teraz uruchamiamy algorytm bez niego
        run_genetic_algorithm(
            population_size, generations, elitism_perc,
            mutation_prob, crossover_type, alpha, cycles, None
        )

    except ValueError as e:
        messagebox.showerror("Błąd", str(e))

# Tworzenie GUI
root = tk.Tk()
root.title("Optymalizacja świateł drogowych - Algorytm genetyczny")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Pola do wprowadzania parametrów
ttk.Label(frame, text="Rozmiar populacji:").grid(row=0, column=0, sticky=tk.W)
pop_size_entry = ttk.Entry(frame)
pop_size_entry.insert(0, "100")
pop_size_entry.grid(row=0, column=1)

ttk.Label(frame, text="Liczba generacji:").grid(row=1, column=0, sticky=tk.W)
gen_entry = ttk.Entry(frame)
gen_entry.insert(0, "50")
gen_entry.grid(row=1, column=1)

ttk.Label(frame, text="Procent elityzmu (0-1):").grid(row=2, column=0, sticky=tk.W)
elitism_entry = ttk.Entry(frame)
elitism_entry.insert(0, "0.1")
elitism_entry.grid(row=2, column=1)

ttk.Label(frame, text="Prawdopodobieństwo mutacji (0-1):").grid(row=3, column=0, sticky=tk.W)
mutation_entry = ttk.Entry(frame)
mutation_entry.insert(0, "0.5")
mutation_entry.grid(row=3, column=1)

ttk.Label(frame, text="Typ crossover:").grid(row=4, column=0, sticky=tk.W)
crossover_type_combo = ttk.Combobox(frame, values=["pmx", "linear"])
crossover_type_combo.set("pmx")
crossover_type_combo.grid(row=4, column=1)

ttk.Label(frame, text="Alpha (dla PMX i linear):").grid(row=5, column=0, sticky=tk.W)
alpha_entry = ttk.Entry(frame)
alpha_entry.insert(0, "1.5")
alpha_entry.grid(row=5, column=1)

ttk.Label(frame, text="Liczba cykli:").grid(row=6, column=0, sticky=tk.W)
cycles_entry = ttk.Entry(frame)
cycles_entry.insert(0, "5")  # Domyślna wartość 5 cykli
cycles_entry.grid(row=6, column=1)

# Przycisk uruchamiający algorytm
ttk.Button(frame, text="Uruchom algorytm", command=start_algorithm).grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()
