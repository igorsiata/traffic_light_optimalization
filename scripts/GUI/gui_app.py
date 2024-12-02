import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scripts.GUI.genetic_algorithm_gui import TrafficLightsOptGentetic
from scripts.simulation.graphics import App, SimulationGraphic
import pygame


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
        # Aktualizacja paska postępu w głównym wątku
        progress_bar["value"] = (gen / generations) * 100
        root.update_idletasks()
        print(f"Generacja {gen}: najlepsze fitness = {best_fitness}")

    def run_algorithm_inner():
        # Uruchamiamy algorytm i zbieramy wyniki
        best_solution, fitness_history = traffic_opt.genetic_algorthm.run_evolution_gui(
            generations, elitism_perc, update_progress
        )
        # Po zakończeniu uruchamiania algorytmu wyświetlamy wyniki
        root.after(0, lambda: finalize_results(best_solution, fitness_history, traffic_opt))

    # Uruchamiamy algorytm w nowym wątku
    threading.Thread(target=run_algorithm_inner, daemon=True).start()



def finalize_results(best_solution, fitness_history, traffic_opt):
    """ Wyświetla szczegóły najlepszego rozwiązania, wykres fitness i przycisk do uruchomienia symulacji. """
    # Tworzenie nowego okna
    result_window = tk.Toplevel()
    result_window.title("Wyniki optymalizacji")
    
    # Podział okna na dwie sekcje: tekstową i wykres
    frame_left = tk.Frame(result_window, width=300, height=600, padx=10, pady=10)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    frame_right = tk.Frame(result_window, padx=10, pady=10)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Dodanie wyników do panelu tekstowego
    result_text = tk.Text(frame_left, wrap=tk.WORD, width=40, height=30)
    result_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Generowanie czytelnego tekstu wyników
    lights_info = "\n".join(
        f"Skrzyżowanie {i + 1}:\n" + "\n".join(
            f"  Kierunek {direction.name}: {round(time, 2)} s"
            for direction, time in lights_times.items()
        )
        for i, (lights_times, _) in enumerate(best_solution)
    )
    result_text.insert(tk.END, f"Najlepsze rozwiązanie:\n\n{lights_info}")
    result_text.config(state=tk.DISABLED)  # Ustawienie trybu tylko do odczytu

    # Dodanie przycisku do uruchomienia symulacji
    def start_simulation():
        try:
            cycle = best_solution
            theApp = App()
            theApp.simulation_graphics = SimulationGraphic(cycle)

            thread = threading.Thread(target=theApp.on_execute, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("Błąd symulacji", f"Nie udało się uruchomić symulacji.\n\nSzczegóły: {e}")


    start_button = tk.Button(frame_left, text="Start symulacji", command=start_simulation)
    start_button.pack(side=tk.BOTTOM, pady=10)

    # Dodanie wykresu do panelu
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fitness_history, marker='o', linestyle='-', color='b')
    ax.set_title("Postęp optymalizacji")
    ax.set_xlabel("Generacja")
    ax.set_ylabel("Fitness")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_right)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


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
        cycles = int(cycles_entry.get())

        if not (0 <= elitism_perc <= 1):
            raise ValueError("Procent elityzmu musi być w przedziale 0-1.")
        
        # Resetowanie paska postępu
        progress_bar["value"] = 0
        
        run_genetic_algorithm(
            population_size, generations, elitism_perc,
            mutation_prob, crossover_type, alpha, cycles, progress_bar
        )

    except ValueError as e:
        messagebox.showerror("Błąd", str(e))

def on_close():
    """Zamyka wszystkie zasoby i kończy aplikację."""
    try:
        pygame.quit()  # Zamyka Pygame, jeśli było uruchomione
        root.destroy()  # Niszczy główne okno Tkinter
    except Exception as e:
        print(f"Błąd podczas zamykania aplikacji: {e}")
    finally:
        exit(0)  # Wymusza zakończenie procesu Python



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
cycles_entry.insert(0, "5")
cycles_entry.grid(row=6, column=1)

# Pasek postępu
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=7, column=0, columnspan=2, pady=10)

# Przycisk uruchamiający algorytm
ttk.Button(frame, text="Uruchom algorytm", command=start_algorithm).grid(row=8, column=0, columnspan=2, pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)  # Obsługa zamykania okna
root.mainloop()

