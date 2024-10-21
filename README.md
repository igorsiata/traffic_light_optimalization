# Optymalizacja przełączania sygnalizacji świetlnej na skrzyżowaniu

## Problem:
Optymalizacja przełączania sygnalizacji świetlnej na skrzyżowaniu.

## Opis problemu:
Chcemy zmaksymalizować przepustowość na skrzyżowaniu poprzez odpowiednie przełączanie świateł. Możliwe dwa podejścia: stałe przełączanie takie samo dla każdego cyklu lub wykorzystanie systemów wizyjnych do monitorowania ruchu i dostosowywania sterowania na bieżąco.

## Model matematyczny:

### Zmienne
- \( x_i(t) \) – stan sygnalizacji na pasie \( i \) w czasie \( t \)  
- \( q_i(t) \) – liczba pojazdów oczekujących w kolejce na pasie \( i \)  
- \( v_i(t) \) – przepustowość na pasie \( i \)  
- \( a_i(t) \) – przyrost pojazdów na pasie \( i \)  

### Ograniczenia:
- \( T_{\text{min}} \), \( T_{\text{max}} \) – minimalny i maksymalny czas trwania zielonego światła  
- \( T_{\text{op}} \) – czas pomiędzy przełączeniem świateł (żółte światło)  
- \( C_i \) – lista pasów kolidujących z pasem \( i \)

Dodatkowo:

- Zielone światło musi trwać co najmniej \( T_{\text{min}} \) i nie może przekraczać \( T_{\text{max}} \) dla każdego pasa \( i \):
  \[
  T_{\text{min}} \leq T_i^{on} \leq T_{\text{max}}
  \]

- Dwa pasy \( i \) i \( j \), które są kolizyjne, nie mogą mieć jednocześnie zielonego światła:
  \[
  x_i(t) + x_j(t) \leq 1 \quad \forall j \in C_i
  \]

- W każdym cyklu rotacyjnym każdy pas musi mieć co najmniej raz zielone światło:
  \[
  \sum_{i} T_i^{on} \leq T_{\text{cycle}}
  \]

- Pomiędzy zmianą z zielonego na czerwone (lub odwrotnie) musi być zachowana minimalna przerwa (żółte światło).

### Co podlega optymalizacji:
- \( T_i^{on} \) – czas włączenia sygnalizacji na pasie \( i \)  
- \( T_i^{off} \) – czas wyłączenia sygnalizacji na pasie \( i \)  

### Funkcja celu:
Celem jest minimalizacja sumy liczby pojazdów oczekujących w kolejce:
\[
\text{min} \sum_{i} q_i(t)
\]
gdzie \( q_i(t+1) \) zależy od przepustowości \( v_i(t) \) i przyrostu pojazdów \( a_i(t) \):
\[
q_i(t+1) = q_i(t) + a_i(t) - v_i(t) \cdot x_i(t)
\]

### Możliwe podejścia:
#### 1. Stały czas przełączania (fixed time control):
Określone czasy trwania zielonego światła są takie same dla każdego cyklu, niezależnie od aktualnego natężenia ruchu.

#### 2. Adaptacyjne sterowanie (adaptive control):
Wykorzystanie danych o bieżącym natężeniu ruchu (np. z systemów wizyjnych, sensorów) do dynamicznego dostosowywania czasu trwania zielonego światła.

### Metody optymalizacji:
- **Programowanie dynamiczne (dynamic programming):** Może być użyte do obliczania optymalnych czasów przełączania świateł w zależności od bieżących stanów \( q_i(t) \) i \( a_i(t) \).
- **Algorytmy genetyczne lub metaheurystyki:** Mogą być zastosowane w celu przeszukiwania przestrzeni rozwiązań w przypadku bardziej skomplikowanych interakcji pomiędzy pasami.
- **Rozwiązania oparte na teorii kolejek:** Mogą być wykorzystane do modelowania przepływu ruchu i optymalizacji sterowania.
