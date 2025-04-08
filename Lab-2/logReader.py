import os
import re
import sys
import glob
from collections import Counter

def parse_log_line(line: str):
    """
    Повертає кортеж (ip, status_code), якщо лінія відповідає формату.
    Інакше - None.
    """
    pattern = r'^(\d+\.\d+\.\d+\.\d+).+" \d{3} \d+'
    match = re.match(r'^(\d+\.\d+\.\d+\.\d+).+?"(?:GET|POST|PUT|DELETE|HEAD) .+?" (\d{3}) \d+', line)
    if match:
        ip = match.group(1)
        status_code = int(match.group(2))
        return ip, status_code
    return None

def get_error_message(status_code: int) -> str:
    if 400 <= status_code < 500:
        return f"{status_code} Client Error"
    elif 500 <= status_code < 600:
        return f"{status_code} Server Error"
    else:
        return None

def main():
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        print("Директорія 'logs/' не знайдена.", file=sys.stderr)
        sys.exit(1)

    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    if not log_files:
        print("Файли .log не знайдені в 'logs/'", file=sys.stderr)
        sys.exit(1)

    ip_counter = Counter()
    error_counter = Counter()

    for log_file in log_files:
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = parse_log_line(line)
                    if parsed:
                        ip, status = parsed
                        ip_counter[ip] += 1
                        error_msg = get_error_message(status)
                        if error_msg:
                            error_counter[error_msg] += 1
        except Exception as e:
            print(f"Помилка при обробці файлу {log_file}: {e}", file=sys.stderr)

    try:
        with open("log_summary.txt", "w", encoding="utf-8") as out:
            out.write("Найчастіші IP-адреси:\n")
            for ip, count in ip_counter.most_common(10):
                out.write(f"{ip} - {count} запитів\n")

            out.write("\nВиявлені помилки:\n")
            for err, count in error_counter.items():
                out.write(f"{err} - {count} разів\n")

        print("Результати збережено в 'log_summary.txt'")
    except Exception as e:
        print(f"Не вдалося записати файл log_summary.txt: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

