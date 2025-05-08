import nashpy as nash
import numpy as np

# Матриці виграшів для Гаррі (гравець 1) і Волдеморта (гравець 2)
A = np.array([
    [0, 5],
    [-5, 2]
])

B = np.array([
    [0, -5],
    [5, 2]
])

# Створюємо гру
game = nash.Game(A, B)

# Шукаємо рівноваги Неша
equilibria = list(game.support_enumeration())

print("Рівноваги Неша:")
for eq in equilibria:
    print(eq)

# Додатково виводимо тип гри
if np.array_equal(A, -B):
    print("\nГра є грою з нульовою сумою.")
else:
    print("\nГра є біматричною грою.")
