import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import calendar
from datetime import datetime
import re


class Person:
    def __init__(self):
        self.name = None  # прізвище
        self.byear = None  # рік народження

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


class Employee(Person):
    def __init__(self):
        super().__init__()
        self.employee_id = None
        self.hourly_rate = None
        self.required_hours = None

    def input_gui(self, name, byear, employee_id, hourly_rate, required_hours):
        self.name = name

        try:
            self.byear = int(byear)
            self.check_by(self.byear)
        except ValueError:
            return False, "Рік народження має бути числом"

        try:
            self.employee_id = int(employee_id)
            if self.employee_id <= 0:
                return False, "Табельний номер має бути додатним числом"
        except ValueError:
            return False, "Табельний номер має бути числом"

        try:
            self.hourly_rate = float(hourly_rate)
            if self.hourly_rate <= 0:
                return False, "Погодинна ставка має бути додатним числом"
        except ValueError:
            return False, "Погодинна ставка має бути числом"

        try:
            self.required_hours = float(required_hours)
            if self.required_hours <= 0 or self.required_hours > 24:
                return False, "Кількість обов'язкових годин має бути в межах (0, 24]"
        except ValueError:
            return False, "Кількість обов'язкових годин має бути числом"

        return True, "Дані введено успішно"

    def calculate_salary(self, worked_hours, total_work_days):
        """
        Розрахунок зарплати за відпрацьованими годинами
        """
        total_required_hours = self.required_hours * total_work_days

        if worked_hours >= total_required_hours:
            return worked_hours * self.hourly_rate
        else:

            return (worked_hours / total_required_hours) * (total_required_hours * self.hourly_rate)

    def __str__(self):
        return f"Працівник: {self.name}, Рік народження: {self.byear}, Табельний номер: {self.employee_id}"


class Database:
    def __init__(self, db_name="payroll.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблиця працівників
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            birth_year INTEGER NOT NULL,
            hourly_rate REAL NOT NULL,
            required_hours REAL NOT NULL
        )
        ''')

        # Таблиця табелів
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timesheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            hours_worked REAL NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')

        self.conn.commit()

    def add_employee(self, employee):
        try:
            self.cursor.execute(
                "INSERT INTO employees (id, name, birth_year, hourly_rate, required_hours) VALUES (?, ?, ?, ?, ?)",
                (employee.employee_id, employee.name, employee.byear, employee.hourly_rate, employee.required_hours)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_employee(self, employee):
        try:
            self.cursor.execute(
                "UPDATE employees SET name=?, birth_year=?, hourly_rate=?, required_hours=? WHERE id=?",
                (employee.name, employee.byear, employee.hourly_rate, employee.required_hours, employee.employee_id)
            )
            self.conn.commit()
            return True
        except:
            return False

    def delete_employee(self, employee_id):
        try:

            self.cursor.execute("DELETE FROM timesheets WHERE employee_id=?", (employee_id,))

            self.cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))

            self.conn.commit()
            return True
        except:
            return False

    def get_employee(self, employee_id):
        self.cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
        result = self.cursor.fetchone()

        if result:
            employee = Employee()
            employee.employee_id = result[0]
            employee.name = result[1]
            employee.byear = result[2]
            employee.hourly_rate = result[3]
            employee.required_hours = result[4]
            return employee

        return None

    def get_all_employees(self):
        self.cursor.execute("SELECT * FROM employees ORDER BY name")
        results = self.cursor.fetchall()

        employees = []
        for result in results:
            employee = Employee()
            employee.employee_id = result[0]
            employee.name = result[1]
            employee.byear = result[2]
            employee.hourly_rate = result[3]
            employee.required_hours = result[4]
            employees.append(employee)

        return employees

    def add_timesheet_entry(self, employee_id, work_date, hours_worked):
        try:

            self.cursor.execute(
                "SELECT id FROM timesheets WHERE employee_id=? AND work_date=?",
                (employee_id, work_date)
            )
            existing = self.cursor.fetchone()

            if existing:

                self.cursor.execute(
                    "UPDATE timesheets SET hours_worked=? WHERE employee_id=? AND work_date=?",
                    (hours_worked, employee_id, work_date)
                )
            else:

                self.cursor.execute(
                    "INSERT INTO timesheets (employee_id, work_date, hours_worked) VALUES (?, ?, ?)",
                    (employee_id, work_date, hours_worked)
                )

            self.conn.commit()
            return True
        except:
            return False

    def get_timesheet(self, employee_id, month=None, year=None):
        if month and year:

            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"

            self.cursor.execute(
                "SELECT work_date, hours_worked FROM timesheets WHERE employee_id=? AND work_date >= ? AND work_date < ? ORDER BY work_date",
                (employee_id, start_date, end_date)
            )
        else:
            # Отримання всього табеля
            self.cursor.execute(
                "SELECT work_date, hours_worked FROM timesheets WHERE employee_id=? ORDER BY work_date",
                (employee_id,)
            )

        return self.cursor.fetchall()

    def get_total_hours(self, employee_id, month, year):
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        self.cursor.execute(
            "SELECT SUM(hours_worked) FROM timesheets WHERE employee_id=? AND work_date >= ? AND work_date < ?",
            (employee_id, start_date, end_date)
        )

        result = self.cursor.fetchone()[0]
        return result if result else 0

    def close(self):
        if self.conn:
            self.conn.close()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Система обліку заробітної плати")
        self.root.geometry("900x600")

        self.db = Database()

        # Поточний місяць і рік для розрахунків
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year

        # Створення вкладок
        self.tab_control = ttk.Notebook(root)

        self.tab_employees = ttk.Frame(self.tab_control)
        self.tab_timesheet = ttk.Frame(self.tab_control)
        self.tab_salaries = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_employees, text="Працівники")
        self.tab_control.add(self.tab_timesheet, text="Табель")
        self.tab_control.add(self.tab_salaries, text="Зарплати")

        self.tab_control.pack(expand=1, fill="both")

        self.init_employees_tab()
        self.init_timesheet_tab()
        self.init_salaries_tab()

        self.load_employees()

    def init_employees_tab(self):

        frame_list = ttk.Frame(self.tab_employees)
        frame_list.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("ID", "Прізвище", "Рік народження", "Ставка", "Годин в день")
        self.tree_employees = ttk.Treeview(frame_list, columns=columns, show="headings")

        for col in columns:
            self.tree_employees.heading(col, text=col)
            if col == "Прізвище":
                self.tree_employees.column(col, width=150)
            else:
                self.tree_employees.column(col, width=100)

        self.tree_employees.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree_employees.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_employees.configure(yscrollcommand=scrollbar.set)

        frame_buttons = ttk.Frame(self.tab_employees)
        frame_buttons.pack(pady=10, padx=10, fill="x")

        ttk.Button(frame_buttons, text="Додати працівника", command=self.add_employee_dialog).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Редагувати працівника", command=self.edit_employee_dialog).pack(side="left",
                                                                                                        padx=5)
        ttk.Button(frame_buttons, text="Видалити працівника", command=self.delete_employee).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Оновити список", command=self.load_employees).pack(side="left", padx=5)

    def init_timesheet_tab(self):

        frame_select = ttk.Frame(self.tab_timesheet)
        frame_select.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_select, text="Вибрати працівника:").pack(side="left", padx=5)

        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(frame_select, textvariable=self.employee_var, state="readonly", width=30)
        self.employee_combo.pack(side="left", padx=5)
        self.employee_combo.bind("<<ComboboxSelected>>", self.load_timesheet)

        ttk.Label(frame_select, text="Місяць:").pack(side="left", padx=5)

        self.month_var = tk.StringVar()
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
        self.month_combo = ttk.Combobox(frame_select, textvariable=self.month_var, state="readonly", width=10,
                                        values=[m[1] for m in months])
        self.month_combo.current(self.current_month - 1)
        self.month_combo.pack(side="left", padx=5)

        ttk.Label(frame_select, text="Рік:").pack(side="left", padx=5)

        self.year_var = tk.StringVar(value=str(self.current_year))
        years = [str(y) for y in range(self.current_year - 5, self.current_year + 2)]
        self.year_combo = ttk.Combobox(frame_select, textvariable=self.year_var, state="readonly", width=5,
                                       values=years)
        self.year_combo.pack(side="left", padx=5)

        ttk.Button(frame_select, text="Показати", command=self.load_timesheet).pack(side="left", padx=5)

        frame_timesheet = ttk.Frame(self.tab_timesheet)
        frame_timesheet.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Дата", "Години")
        self.tree_timesheet = ttk.Treeview(frame_timesheet, columns=columns, show="headings")

        for col in columns:
            self.tree_timesheet.heading(col, text=col)
            self.tree_timesheet.column(col, width=150)

        self.tree_timesheet.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_timesheet, orient="vertical", command=self.tree_timesheet.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_timesheet.configure(yscrollcommand=scrollbar.set)

        frame_buttons = ttk.Frame(self.tab_timesheet)
        frame_buttons.pack(pady=10, padx=10, fill="x")

        ttk.Button(frame_buttons, text="Додати/Редагувати запис", command=self.add_timesheet_entry_dialog).pack(
            side="left", padx=5)
        ttk.Button(frame_buttons, text="Заповнити табель", command=self.fill_timesheet_dialog).pack(side="left", padx=5)

    def init_salaries_tab(self):

        frame_select = ttk.Frame(self.tab_salaries)
        frame_select.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_select, text="Місяць:").pack(side="left", padx=5)

        self.salary_month_var = tk.StringVar()
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
        self.salary_month_combo = ttk.Combobox(frame_select, textvariable=self.salary_month_var, state="readonly",
                                               width=10,
                                               values=[m[1] for m in months])
        self.salary_month_combo.current(self.current_month - 1)
        self.salary_month_combo.pack(side="left", padx=5)

        ttk.Label(frame_select, text="Рік:").pack(side="left", padx=5)

        self.salary_year_var = tk.StringVar(value=str(self.current_year))
        years = [str(y) for y in range(self.current_year - 5, self.current_year + 2)]
        self.salary_year_combo = ttk.Combobox(frame_select, textvariable=self.salary_year_var, state="readonly",
                                              width=5,
                                              values=years)
        self.salary_year_combo.pack(side="left", padx=5)

        ttk.Button(frame_select, text="Розрахувати зарплати", command=self.calculate_salaries).pack(side="left", padx=5)

        frame_results = ttk.Frame(self.tab_salaries)
        frame_results.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Табельний номер", "Прізвище", "Відпрацьовано годин", "Зарплата")
        self.tree_salaries = ttk.Treeview(frame_results, columns=columns, show="headings")

        for col in columns:
            self.tree_salaries.heading(col, text=col)
            if col in ("Прізвище", "Зарплата"):
                self.tree_salaries.column(col, width=150)
            else:
                self.tree_salaries.column(col, width=100)

        self.tree_salaries.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=self.tree_salaries.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_salaries.configure(yscrollcommand=scrollbar.set)

    def load_employees(self):

        for item in self.tree_employees.get_children():
            self.tree_employees.delete(item)

        employees = self.db.get_all_employees()
        for emp in employees:
            self.tree_employees.insert("", "end", values=(
                emp.employee_id, emp.name, emp.byear, emp.hourly_rate, emp.required_hours
            ))

        self.update_employee_combo()

    def update_employee_combo(self):
        employees = self.db.get_all_employees()
        self.employee_combo["values"] = [f"{emp.employee_id} - {emp.name}" for emp in employees]
        if employees:
            self.employee_combo.current(0)

    def add_employee_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("Додати працівника")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Прізвище:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Рік народження:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        byear_entry = ttk.Entry(dialog, width=30)
        byear_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Табельний номер:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        id_entry = ttk.Entry(dialog, width=30)
        id_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Погодинна ставка:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        rate_entry = ttk.Entry(dialog, width=30)
        rate_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Обов'язкові години в день:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        hours_entry = ttk.Entry(dialog, width=30)
        hours_entry.grid(row=4, column=1, padx=10, pady=5)

        def save_employee():
            emp = Employee()
            success, message = emp.input_gui(
                name_entry.get(),
                byear_entry.get(),
                id_entry.get(),
                rate_entry.get(),
                hours_entry.get()
            )

            if success:
                if self.db.add_employee(emp):
                    messagebox.showinfo("Успіх", "Працівника додано успішно")
                    dialog.destroy()
                    self.load_employees()
                else:
                    messagebox.showerror("Помилка", "Працівник з таким табельним номером вже існує")
            else:
                messagebox.showerror("Помилка", message)

        ttk.Button(dialog, text="Зберегти", command=save_employee).grid(row=5, column=0, columnspan=2, pady=10)

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def edit_employee_dialog(self):

        selected = self.tree_employees.selection()
        if not selected:
            messagebox.showinfo("Інформація", "Виберіть працівника для редагування")
            return

        emp_id = self.tree_employees.item(selected[0], "values")[0]
        employee = self.db.get_employee(emp_id)

        if not employee:
            messagebox.showerror("Помилка", "Не вдалося отримати дані працівника")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редагувати працівника #{emp_id}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Прізвище:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, employee.name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Рік народження:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        byear_entry = ttk.Entry(dialog, width=30)
        byear_entry.insert(0, employee.byear)
        byear_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Табельний номер:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        id_entry = ttk.Entry(dialog, width=30, state="readonly")
        id_entry.insert(0, employee.employee_id)
        id_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Погодинна ставка:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        rate_entry = ttk.Entry(dialog, width=30)
        rate_entry.insert(0, employee.hourly_rate)
        rate_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Обов'язкові години в день:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        hours_entry = ttk.Entry(dialog, width=30)
        hours_entry.insert(0, employee.required_hours)
        hours_entry.grid(row=4, column=1, padx=10, pady=5)

        def save_employee():
            emp = Employee()
            success, message = emp.input_gui(
                name_entry.get(),
                byear_entry.get(),
                employee.employee_id,  # Використовуємо існуючий ID
                rate_entry.get(),
                hours_entry.get()
            )

            if success:
                if self.db.update_employee(emp):
                    messagebox.showinfo("Успіх", "Дані працівника оновлено успішно")
                    dialog.destroy()
                    self.load_employees()
                else:
                    messagebox.showerror("Помилка", "Не вдалося оновити дані працівника")
            else:
                messagebox.showerror("Помилка", message)

        ttk.Button(dialog, text="Зберегти", command=save_employee).grid(row=5, column=0, columnspan=2, pady=10)

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def delete_employee(self):

        selected = self.tree_employees.selection()
        if not selected:
            messagebox.showinfo("Інформація", "Виберіть працівника для видалення")
            return

        emp_id = self.tree_employees.item(selected[0], "values")[0]
        employee = self.db.get_employee(emp_id)

        if not employee:
            messagebox.showerror("Помилка", "Не вдалося отримати дані працівника")
            return

        confirm = messagebox.askyesno("Підтвердження",
                                      f"Ви дійсно хочете видалити працівника {employee.name} (ID: {employee.employee_id})?")
        if confirm:
            if self.db.delete_employee(employee.employee_id):
                messagebox.showinfo("Успіх", "Працівника видалено успішно")
                self.load_employees()
            else:
                messagebox.showerror("Помилка", "Не вдалося видалити працівника")

    def load_timesheet(self, event=None):

        for item in self.tree_timesheet.get_children():
            self.tree_timesheet.delete(item)

        selected = self.employee_combo.get()
        if not selected:
            return

        emp_id = selected.split(" - ")[0]

        month_name = self.month_var.get()
        months = {name: idx for idx, name in enumerate(calendar.month_name) if idx > 0}
        month = months.get(month_name)

        year = int(self.year_var.get())

        timesheet = self.db.get_timesheet(emp_id, month, year)
        for date, hours in timesheet:
            self.tree_timesheet.insert("", "end", values=(date, hours))

    def add_timesheet_entry_dialog(self):

        selected = self.employee_combo.get()
        if not selected:
            messagebox.showinfo("Інформація", "Виберіть працівника")
            return

        emp_id = selected.split(" - ")[0]

        dialog = tk.Toplevel(self.root)
        dialog.title("Додати/Редагувати запис табеля")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Дата (РРРР-ММ-ДД):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        date_entry = ttk.Entry(dialog, width=20)
        date_entry.grid(row=0, column=1, padx=10, pady=5)

        current_date = datetime.now().strftime("%Y-%m-%d")
        date_entry.insert(0, current_date)

        ttk.Label(dialog, text="Відпрацьовані години:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        hours_entry = ttk.Entry(dialog, width=20)
        hours_entry.grid(row=1, column=1, padx=10, pady=5)
        hours_entry.insert(0, "8.0")

        def save_entry():

            try:
                hours = float(hours_entry.get())
                if hours < 0 or hours > 24:
                    messagebox.showerror("Помилка", "Кількість годин має бути в межах [0, 24]")
                    return
            except ValueError:
                messagebox.showerror("Помилка", "Неправильний формат годин")
                return

            if self.db.add_timesheet_entry(emp_id, hours):
                messagebox.showinfo("Успіх", "Запис додано/оновлено успішно")
                dialog.destroy()
                self.load_timesheet()
            else:
                messagebox.showerror("Помилка", "Не вдалося додати/оновити запис")

        ttk.Button(dialog, text="Зберегти", command=save_entry).grid(row=2, column=0, columnspan=2, pady=10)

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def fill_timesheet_dialog(self):

        selected = self.employee_combo.get()
        if not selected:
            messagebox.showinfo("Інформація", "Виберіть працівника")
            return

        emp_id = selected.split(" - ")[0]
        employee = self.db.get_employee(emp_id)

        if not employee:
            messagebox.showerror("Помилка", "Не вдалося отримати дані працівника")
            return

        month_name = self.month_var.get()
        months = {name: idx for idx, name in enumerate(calendar.month_name) if idx > 0}
        month = months.get(month_name)

        year = int(self.year_var.get())

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Заповнити табель для {employee.name} за {month_name} {year}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        days_in_month = calendar.monthrange(year, month)[1]

        frame_canvas = ttk.Frame(dialog)
        frame_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_canvas)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame_content = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_content, anchor="nw")

        timesheet = self.db.get_timesheet(emp_id, month, year)
        timesheet_dict = {date: hours for date, hours in timesheet}

        entries = {}

        ttk.Label(frame_content, text="День").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame_content, text="Дата").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_content, text="День тижня").grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(frame_content, text="Години").grid(row=0, column=3, padx=5, pady=5)

        for day in range(1, days_in_month + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            weekday = calendar.day_name[calendar.weekday(year, month, day)]

            ttk.Label(frame_content, text=str(day)).grid(row=day, column=0, padx=5, pady=2)
            ttk.Label(frame_content, text=date_str).grid(row=day, column=1, padx=5, pady=2)
            ttk.Label(frame_content, text=weekday).grid(row=day, column=2, padx=5, pady=2)

            hours_entry = ttk.Entry(frame_content, width=10)
            hours_entry.grid(row=day, column=3, padx=5, pady=2)

            if date_str in timesheet_dict:
                hours_entry.insert(0, str(timesheet_dict[date_str]))
            elif weekday in ('Saturday', 'Sunday'):  # Вихідні
                hours_entry.insert(0, "0")
            else:
                hours_entry.insert(0, str(employee.required_hours))

            entries[date_str] = hours_entry

        def save_timesheet():
            success = True
            for date, entry in entries.items():
                try:
                    hours = float(entry.get())
                    if hours < 0 or hours > 24:
                        messagebox.showerror("Помилка", f"Кількість годин для {date} має бути в межах [0, 24]")
                        return

                    if not self.db.add_timesheet_entry(emp_id, date, hours):
                        success = False
                except ValueError:
                    messagebox.showerror("Помилка", f"Неправильний формат годин для {date}")
                    return

            if success:
                messagebox.showinfo("Успіх", "Табель заповнено успішно")
                dialog.destroy()
                self.load_timesheet()
            else:
                messagebox.showerror("Помилка", "Виникли помилки при заповненні табеля")

        ttk.Button(dialog, text="Зберегти табель", command=save_timesheet).pack(pady=10)

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def calculate_salaries(self):

        for item in self.tree_salaries.get_children():
            self.tree_salaries.delete(item)

        month_name = self.salary_month_var.get()
        months = {name: idx for idx, name in enumerate(calendar.month_name) if idx > 0}
        month = months.get(month_name)

        year = int(self.salary_year_var.get())

        _, days_in_month = calendar.monthrange(year, month)
        work_days = sum(1 for day in range(1, days_in_month + 1)
                        if calendar.weekday(year, month, day) < 5)  # Пн-Пт

        employees = self.db.get_all_employees()
        for emp in employees:
            worked_hours = self.db.get_total_hours(emp.employee_id, month, year)

            salary = emp.calculate_salary(worked_hours, work_days)

            self.tree_salaries.insert("", "end", values=(
                emp.employee_id, emp.name, worked_hours, f"{salary:.2f} грн"
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
