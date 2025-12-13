import random

brands = ['Xiaomi', 'Huawei', 'Samsung', 'Apple', 'Irbis', 'Lenovo']
types = ['Смартфон', 'Телефон', 'Планшет', 'Робот-пылесос', 'Часы']
models = ['Note', 'Pro', 'Ultra', 'S', 'GT', 'X']
colors = ['синий', 'черный', 'белый', 'красный', 'зелёный', 'серебристый']
storages = ['4/64GB', '8/128GB', '12/256GB', '16/512GB']
screens = ['6.1"', '6.7"', '10.1"', '11"', '12.3"']

# Генерация catalog.txt
with open('catalog.txt', 'w', encoding='utf-8') as f:
    for i in range(100000):  # 1000 товаров в каталоге
        brand = random.choice(brands)
        typ = random.choice(types)
        model = random.choice(models)
        color = random.choice(colors)
        storage = random.choice(storages)
        screen = random.choice(screens)
        title = f"{typ} {brand} {model} {screen} {storage} {color}"
        f.write(f"{1000+i}\t{title}\n")

# Генерация new_items.txt
with open('new_items.txt', 'w', encoding='utf-8') as f:
    for i in range(5000):  # 200 новых товаров
        if i % 5 == 0:
            # вставим «почти дубликаты» из каталога
            cat_idx = random.randint(0, 999)
            title_base = f"{types[cat_idx%len(types)]} {brands[cat_idx%len(brands)]} {models[cat_idx%len(models)]} {screens[cat_idx%len(screens)]} {storages[cat_idx%len(storages)]} {colors[cat_idx%len(colors)]}"
            # немного изменяем: удаляем слово, меняем регистр
            title = title_base.replace(' ', '  ').upper() if random.random()<0.5 else title_base.lower()
        else:
            brand = random.choice(brands)
            typ = random.choice(types)
            model = random.choice(models)
            color = random.choice(colors)
            storage = random.choice(storages)
            screen = random.choice(screens)
            title = f"{typ} {brand} {model} {screen} {storage} {color}"
        f.write(f"{2000+i}\t{title}\n")

print("Test files 'catalog.txt' (1000 items) and 'new_items.txt' (200 items) generated.")