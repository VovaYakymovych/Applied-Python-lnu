import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jn, jn_zeros

n = 3
m = 2
A = 1
t = 0  # час


zeros = jn_zeros(n, m)
k = zeros[m - 1]  # k - m-й нуль


r = np.linspace(0, 1, 300)
theta = np.linspace(0, 2 * np.pi, 300)
R, Theta = np.meshgrid(r, theta)


Z = A * jn(n, k * R) * np.sin(n * Theta) * np.cos(k * t)


X = R * np.cos(Theta)
Y = R * np.sin(Theta)


fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
ax.set_title(f'Коливання мембрани при n={n}, m={m}, t={t}')
plt.show()
