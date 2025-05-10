from scipy.integrate import quad
import numpy as np


def debye_integrand(x):
    return (x**3) / (np.exp(x) - 1)


result, error = quad(debye_integrand, 0, np.inf)


exact = (np.pi ** 4) / 15

# Вивід
print(f"Обчислений інтеграл: {result}")
print(f"Точне значення π⁴/15: {exact}")
print(f"Абсолютна похибка: {abs(result - exact)}")

