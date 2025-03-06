import json
from functools import wraps


class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __lt__(self, other):
        return self.price < other.price

    def __str__(self):
        return f"{self.name}: {self.price}$ ({self.quantity} шт.)"

    def __repr__(self):
        return f"Product({self.name}, {self.price}, {self.quantity})"

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            products_data = json.load(file)
        return [cls(p["name"], p["price"], p["quantity"]) for p in products_data]


class Customer:
    def __init__(self, customer_id, first_name, last_name, phone):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self._phone = phone
        self.orders = {}

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, new_phone):
        self._phone = new_phone

    def __str__(self):
        return f"Customer {self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Customer({self.customer_id}, {self.first_name}, {self.last_name}, {self._phone})"


class Order:
    total_sold = 0

    def __init__(self, customer, products):
        self.customer = customer
        self.products = {}
        self.total_price = 0
        self.process_order(products)

    def process_order(self, products):
        unavailable = []

        for product, quantity in products.items():
            if product.quantity >= quantity:
                self.products[product] = quantity
                product.quantity -= quantity
                self.total_price += product.price * quantity
                Order.total_sold += quantity
            else:
                unavailable.append(product.name)

        if unavailable:
            self.log_unavailability(unavailable)

        self.apply_discount()

    def apply_discount(self):
        if self.products:
            most_expensive = max(self.products, key=lambda p: p.price)
            quantity = self.products[most_expensive]
            discount = 10 + quantity if quantity < 5 else 15
            self.total_price -= most_expensive.price * quantity * (discount / 100)

    def log_unavailability(self, unavailable):
        with open("order_log.txt", "a", encoding='utf-8') as file:
            file.write(
                f"{self.customer.last_name}, {self.customer.first_name}, {self.customer.phone}: Недостатньо {', '.join(unavailable)}\n")

    @staticmethod
    def total_sold_products():
        return Order.total_sold

    def __str__(self):
        return f"Order for {self.customer.first_name} {self.customer.last_name} - Total: {self.total_price}$"

    def __repr__(self):
        return f"Order({self.customer}, {self.products}, {self.total_price})"


def receipt_decorator(func):
    @wraps(func)
    def wrapper(order, *args, **kwargs):
        result = func(order, *args, **kwargs)
        print("\n===== ЧЕК =====")
        print(order)
        for product, quantity in order.products.items():
            print(f"{product.name}: {quantity} x {product.price}$")
        print(f"Загальна сума: {order.total_price}$")
        print("================\n")
        return result

    return wrapper


@receipt_decorator
def generate_receipt(order):
    return order


if __name__ == "__main__":
    product1 = Product("Ноутбук", 1000, 10)
    product2 = Product("Смартфон", 500, 5)
    product3 = Product("Планшет", 700, 0)

    customer = Customer(1, "Іван", "Петров", "+380501234567")
    order = Order(customer, {product1: 2, product2: 6, product3: 1})

    generate_receipt(order)
