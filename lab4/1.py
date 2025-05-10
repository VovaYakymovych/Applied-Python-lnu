import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jn, jn_zeros

# Параметри
n = 3
m = 2
A = 1  # амплітуда
t = 0  # час

# Отримуємо m-й нуль функції Бесселя J_n
zeros = jn_zeros(n, m)
k = zeros[m - 1]  # k - m-й нуль

# Полярні координати
r = np.linspace(0, 1, 300)
theta = np.linspace(0, 2 * np.pi, 300)
R, Theta = np.meshgrid(r, theta)

# Функція коливання мембрани
Z = A * jn(n, k * R) * np.sin(n * Theta) * np.cos(k * t)

# Перетворюємо в декартову систему координат для побудови графіка
X = R * np.cos(Theta)
Y = R * np.sin(Theta)

# Побудова графіка
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
ax.set_title(f'Коливання мембрани при n={n}, m={m}, t={t}')
plt.show()
