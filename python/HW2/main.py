import re

#Task 1
def copyTextFile(file1, file2, mode_="a"):
    file1 = file1
    file2 = file2
    mode_ = mode_
    try:
        with open(file1, "r", encoding="UTF-8") as f1:
            with open(file2, mode_, encoding="UTF-8") as f2:
                f2.write(f1.read())
    except FileNotFoundError:
        print(f"Not found {file1}")
    except ValueError:
        print("Value Error")



#Task 2
def countPrice():
    total = 0
    item = []
    try:
        with open("prices.txt", "r", encoding="UTF-8") as f:
            for line in f:
                row = line.strip()
                if not line:
                    continue
                data = row.split("\t")
                if len(data) == 3:
                    prod = data[0]
                    quan = int(data[1])
                    price = float(data[2])
                    
                    prod_total = quan * price
                    total += prod_total
                    item.append((prod, quan, price, prod_total))
                    
            print('-' * 60)
            for vat in item:
                print(f"{vat[0]:15} {vat[1]:2} шт. × {vat[2]:3} руб. = {vat[3]:4} руб.")
            print('-' * 60)
            print(f"Total price: {total}")
            print('-' * 20)
    except FileNotFoundError:
        print("Not found prices.txt")
    except ValueError:
        print("Value Error")

#Task 3
def countWords():
    word = []
    with open("text_file.txt", "r", encoding="UTF-8") as f:
        for line in f:
            #new_line = line.translate(str.maketrans('', '', string.punctuation))
            new_line = re.sub(r'[^\w\s]', '', line)
            length_words = len(new_line.strip().split())
            print(length_words)
        f.close()

#Task 4
def uniqueValue(file_1, file_2):
    seen_line = set()
    unique = []
    with open(file_1, "r", encoding="UTF-8") as f:
        for line in f:
            cleaned_line = line.strip()
            if cleaned_line and cleaned_line not in seen_line:
                unique.append(cleaned_line)
                seen_line.add(cleaned_line)
        with open(file_2, "w", encoding="UTF-8") as fail:
            for line in unique:
                fail.write(line + "\n")
            print("Recorded")

if __name__ == "__main__":
    
    print("Task 1. Копирование содержимого одного файла в другой.")
    copyTextFile("source.txt", "destination.txt", "w")
    print("File copied")
    
    print("\nTask 2. Подсчёт стоимости заказа из файла.")
    countPrice()
    
    print("\nTask 3. Подсчёт количества слов в файле.")
    countWords()
    
    print("\nTask 4. Копирование уникального содержимого одного файла в другой.")
    uniqueValue("input.txt", "unique_output.txt")