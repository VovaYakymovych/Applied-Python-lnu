import nashpy as nash
import numpy as np

# Введи свою кількість літер у прізвищі тут:
k = 8

# Створюємо матрицю гри
A = np.array([
    [4, 3, 4, 2],
    [3, 4, 6, 5],
    [2, 5, k, 3]
])

# Оскільки у задачі вказана тільки одна матриця, припустимо, що гра є з нульовою сумою
# тобто друга матриця B = -A
B = -A

# Створення гри
game = nash.Game(A, B)

# Пошук рівноваг Неша
equilibria = list(game.support_enumeration())

# Виведення результату
print("Рівноваги Неша:")
for eq in equilibria:
    print(eq)

# Додаткова інформація про гру
if np.array_equal(A, -B):
    print("\nГра є грою з нульовою сумою.")
else:
    print("\nГра є біматричною грою.")
