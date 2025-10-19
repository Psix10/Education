class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
    def __str__(self):
        return(f"{self.name} {self.price} {self.stock}")
    
    def update_stock(self, quantity):
        if self.stock + quantity < 0:
            raise ValueError(f"Недостаточно товара '{self.name}'. В наличии: {self.stock}")
        self.stock += quantity

class Order:
    def __init__(self, order_id):
        self.products = {}
        self.order_id = order_id
    
    def __repr__(self):
        if not self.products:
            return "Заказ пуст"
        
        order_details = f"Заказ #{self.order_id}:\n"
        for product, quantity in self.products.items():
            order_details += f"  {product.name}: {quantity} x {product.price} = {product.price * quantity}\n"
        order_details += f"Итого: {self.calculate_total()}"
        return order_details
    
    def add_product(self, product, quantity=1):
        if quantity <= 0:
            print("Количество должно быть положительным")
        
        if product.stock < quantity:
            print(f"Недостаточно товара '{product.name}'. В наличии: {product.stock}")
            return
        
        if product in self.products:
            self.products[product] += quantity
        else:
            self.products[product] = quantity
            
        product.update_stock(-quantity)
        print(f"Товар '{product.name}' в количестве {quantity} добавлен в заказ")
    
    def calculate_total(self):
        total = 0
        for product, quantity in self.products.items():
            total += product.price * quantity
        return total
    
    def remove_product(self, product, quantity):
        if self.products[product] > 0:
            self.products[product] -= quantity
        
        if self.products[product] <= 0:
            del self.products[product]
        
        if quantity == 1:
            print(f"Удален {quantity} продукт")
        elif 2 <= quantity <= 4:
            print(f"Удалено {quantity} продукта")
        else:
            print(f"Удалено {quantity} продуктов")
        
    def return_product(self, product, quantity):
        if quantity > self.products[product] + product.stock:
            quantity = int(self.products[product])
        if quantity > 0 & quantity < self.products[product] + product.stock:
            self.products[product] -= quantity
            product.update_stock(+quantity)
        else:
            product.update_stock(self.products[product])
        
        if self.products[product] <= 0:
            del self.products[product]
        
            

class Store():
    def __init__(self):
        self.products = []
        self.orders = []
        self._next_order_id = 1
    
    def __str__(self):
        return (f"{self.products}")
    
    def add_product(self, product):
        self.products.append(product)
        print(f"Товар '{product.name}' добавлен в магазин")
        
    def list_products(self):
        if not self.products:
            print("В магазине нет товаров")
            return
        
        print(f"{'Название':15} {'Цена':10} {'Остатки':5}")
        print(40 * '-')
        for i in self.products:
            value = str(i)
            value2 = value.split()
            print(f"{value2[0]:<15} {value2[1]:<10} {value2[2]:<10}")
            print(40 * '-')
    
    def create_order(self):
        order = Order(self._next_order_id)
        self.orders.append(order)
        self._next_order_id += 1
        print(f"Создан заказ #{order.order_id}")
        return order
        
if __name__ == "__main__":
    store = Store()
    product1 = Product("Ноутбук", 1000, 5)
    product2 = Product("Смартфон", 50, 10)
    store.add_product(product1)
    store.add_product(product2)
    print("\n")
    #store.list_products()
    print("\n")
    order = store.create_order()
    print("\n")
    order.add_product(product1, 3)
    order.add_product(product2, 3)
    print("\n")
    print(order)
    print("\n")
    store.list_products()

    order.return_product(product1, 2)
    print(order)
    store.list_products()