import threading
import time
from typing import NoReturn

def sq(num: list) -> list:
    s = list(map(lambda x: (x**2) , num))
    print(s)
    return s

def cub(num: list) -> list:
    s = list(map(lambda x: (x**3) , num))
    print(s)
    return s

def sq2() -> NoReturn:
    for i in range(1, 11):
        print(f"square: {i**2}")
        time.sleep(1)
        
def cub2() -> NoReturn:
    for i in range(1, 11):
        print(f"Cube: {i**3}")
        time.sleep(1)

if __name__ == "__main__":
    a = [i for i in range(1, 11)]
    t1 = threading.Thread(target=sq, args=(a,))
    t2 = threading.Thread(target=cub, args=(a,))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print("Option 2")
    
    t3 = threading.Thread(target=sq2)
    t4 = threading.Thread(target=cub2)
    
    t3.start()
    t4.start()
    
    t3.join()
    t4.join()