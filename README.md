# Optymalizacja przełączania sygnalizacji świetlnej na skrzyżowaniu
## Problem: 
Optymalizacja przełączania sygnalizacji świetlnej na skrzyżowaniu.
## Opis problemu: 
Chcemy zmaksymalizować przepustowość na skrzyżowaniu poprzez odpowiednie przełączanie świateł. Możliwe dwa podejścia: stałe przełączanie takie samo dla każdego cyklu lub wykorzystanie systemów wizyjnych do monitorowania ruchu i dostosowywania sterowania na bieżąco.
## Model matematyczny:
### Zmienne
xi(t) – stan sygnalizacji na pasie i
qi(t) – liczba pojazdów oczekujących w kolejce na pasie i
vi(t) – przepustowość na pasie i
ai(t) – przyrost pojazdów na pasie i
### Ograniczenia:
Tmin, Tmax – minimalny i maksymalny czas trwania zielonego światła
Top – czas pomiędzy przełączeniem świateł (żółte światło)
Ci – lista pasów kolidujących z pasem i
W jednej rotacji muszą zaświecić się wszystkie światła
### Co podelga optymalizacji:
Ti_on, Ti_off - czas włączenia i wyłączenia sygnalizacji na pasie i
### Funcja celu
min(sum(q(t))
