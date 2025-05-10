from scipy.integrate import quad
import numpy as np

# Підінтегральна функція
def debye_integrand(x):
    return (x**3) / (np.exp(x) - 1)

# Обчислення інтегралу
result, error = quad(debye_integrand, 0, np.inf)

# Точне значення
exact = (np.pi ** 4) / 15

# Вивід
print(f"Обчислений інтеграл: {result}")
print(f"Точне значення π⁴/15: {exact}")
print(f"Абсолютна похибка: {abs(result - exact)}")

