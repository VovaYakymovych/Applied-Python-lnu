import os
import random
from datetime import datetime, timedelta

ips = ["192.168.1.10", "203.0.113.42", "198.51.100.17", "172.16.0.5", "10.0.0.7", "192.0.2.1"]
methods = ["GET", "POST", "PUT", "DELETE"]
paths = ["/index.html", "/login", "/dashboard", "/upload", "/admin", "/profile", "/data", "/api/items", "/contact", "/settings"]
status_codes = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]
sizes = [random.randint(100, 5000) for _ in range(100)]

def random_log_line():
    ip = random.choice(ips)
    method = random.choice(methods)
    path = random.choice(paths)
    status = random.choice(status_codes)
    size = random.choice(sizes)
    now = datetime(2025, 3, 10, 14, 0, 0) + timedelta(seconds=random.randint(0, 3600))
    date_str = now.strftime("%d/%b/%Y:%H:%M:%S +0000")
    return f'{ip} - - [{date_str}] "{method} {path} HTTP/1.1" {status} {size}'

log_lines = [random_log_line() for _ in range(50)]

os.makedirs("logs", exist_ok=True)
with open("logs/large_example.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print("Файл logs/example.log успішно створено.")
