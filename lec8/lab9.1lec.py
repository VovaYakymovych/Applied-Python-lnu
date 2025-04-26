import json

def count_words(text):
    words = text.lower().split()
    word_count = {}

    for word in words:
        word = word.strip(",.!?;:")  # прибираємо розділові знаки
        if word:
            word_count[word] = word_count.get(word, 0) + 1

    return word_count

def main():
    text = input("Введіть рядок: ")
    result = count_words(text)

    with open("words_count.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("Результат записано у файл words_count.json")

if __name__ == "__main__":
    main()
