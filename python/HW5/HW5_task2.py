import threading
from time import sleep
from typing import NoReturn



def print_num(thread_name: str) -> NoReturn:
    for i in range(1, 11):
        print(f"{thread_name} : {i}")
        sleep(1)
        

if __name__ == "__main__":
    t1 = threading.Thread(target=print_num, args=("flux 1",))
    t2 = threading.Thread(target=print_num, args=("flux 2",))
    t3 = threading.Thread(target=print_num, args=("flux 3",))  
    
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()