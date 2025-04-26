import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

# Базовий клас Person
class Person:
    def __init__(self):
        self.name = None
        self.byear = None

    def input(self):
        try:
            self.name = input("Введіть прізвище працівника: ")
            self.byear = int(input("Введіть рік народження працівника: "))
            self.check_by(self.byear)
        except ValueError:
            self.byear = int(input("Введіть коректний рік народження працівника: "))
            self.check_by(self.byear)

    @staticmethod
    def check_by(by, cur_year=2025):
        correct = 1 if by in range(cur_year - 65, cur_year - 17) else 0
        while not correct:
            by = int(input("Введіть коректний рік народження працівника: "))
            correct = 1 if by in range(cur_year - 65, cur_year - 17) else 0
        return by

# Клас Employee, що наслідується від Person
class Employee(Person):
    def __init__(self):
        super().__init__()
        self.id_number = None
        self.salary_per_hour = None
        self.work_log = []

    def input_employee(self):
        self.name = simpledialog.askstring("Введення", "Введіть прізвище працівника:")
        self.byear = self.check_by(int(simpledialog.askinteger("Введення", "Введіть рік народження працівника:")))
        self.id_number = simpledialog.askstring("Введення", "Введіть табельний номер працівника:")
        self.salary_per_hour = simpledialog.askfloat("Введення", "Введіть погодинну ставку:")

    def input_work_log(self, min_hours_per_day):
        self.work_log = []
        for day in range(1, 31):  # 30 днів місяця
            hours = simpledialog.askinteger("Табель", f"Введіть кількість годин за {day} день:")
            self.work_log.append(hours if hours is not None else 0)

    def calculate_salary(self, min_hours_per_day):
        total_hours = sum(self.work_log)
        expected_hours = min_hours_per_day * 30
        salary = self.salary_per_hour * total_hours

        if total_hours < expected_hours:
            salary *= 0.8  # Якщо менше мінімальної норми — 80% зарплати
        return salary

    def to_dict(self):
        return {
            'name': self.name,
            'byear': self.byear,
            'id_number': self.id_number,
            'salary_per_hour': self.salary_per_hour,
            'work_log': self.work_log
        }

    @staticmethod
    def from_dict(data):
        emp = Employee()
        emp.name = data['name']
        emp.byear = data['byear']
        emp.id_number = data['id_number']
        emp.salary_per_hour = data['salary_per_hour']
        emp.work_log = data['work_log']
        return emp

# Основна програма з вікнами
class PayrollApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Розрахунок зарплати працівників")
        self.employees = []
        self.min_hours_per_day = 4  # Мінімальна кількість годин в день

        # Кнопки
        tk.Button(root, text="Додати працівника", command=self.add_employee).pack(pady=5)
        tk.Button(root, text="Ввести табель працівника", command=self.add_work_log).pack(pady=5)
        tk.Button(root, text="Показати заробітну плату", command=self.show_salaries).pack(pady=5)
        tk.Button(root, text="Зберегти у файл", command=self.save_data).pack(pady=5)
        tk.Button(root, text="Завантажити з файлу", command=self.load_data).pack(pady=5)

    def add_employee(self):
        emp = Employee()
        emp.input_employee()
        self.employees.append(emp)
        messagebox.showinfo("Успіх", "Працівника додано!")

    def add_work_log(self):
        if not self.employees:
            messagebox.showwarning("Помилка", "Спочатку додайте працівника!")
            return
        choices = [f"{i}: {emp.name}" for i, emp in enumerate(self.employees)]
        choice = simpledialog.askinteger("Вибір працівника", f"Виберіть працівника за номером:\n" + "\n".join(choices))
        if choice is not None and 0 <= choice < len(self.employees):
            self.employees[choice].input_work_log(self.min_hours_per_day)
            messagebox.showinfo("Успіх", "Табель збережено!")

    def show_salaries(self):
        window = tk.Toplevel(self.root)
        window.title("Список працівників та зарплата")
        for emp in self.employees:
            salary = emp.calculate_salary(self.min_hours_per_day)
            tk.Label(window, text=f"{emp.name} (Табельний №: {emp.id_number}): {salary:.2f} грн").pack()

    def save_data(self):
        data = [emp.to_dict() for emp in self.employees]
        with open('employees.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успіх", "Дані збережено у файл!")

    def load_data(self):
        if not os.path.exists('employees.json'):
            messagebox.showwarning("Помилка", "Файл не знайдено!")
            return
        with open('employees.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.employees = [Employee.from_dict(emp_data) for emp_data in data]
        messagebox.showinfo("Успіх", "Дані завантажено з файлу!")

# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollApp(root)
    root.mainloop()
