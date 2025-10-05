import random
#import math

class OddNumber(Exception):
    def __init__(self, msg = "It has a odd number"):
        self.message = msg
        super().__init__(self.message)
class NegativeNumber(Exception):
    def __init__(self, msg = "It has a negative number"):
        self.message = msg
        super().__init__(self.message)
        
# TASK 1. function division by 0. working out the "Try" block. Task 2 is inside this function.
def division() -> float:
    try:
        num1 = int(input("Entry a numerator: "))
        num2 = int(input("Entry a denominator:"))
        result = num1 / num2
#TASK 2.        
    except ValueError:
        print(f"Number one or Number two isn't number")    
    except ZeroDivisionError:
        print("Dividing by 0 is not possible")
    else:
        print(f'The function is working, and it displays the value: {result}')
        return result

# TASK 3. Return the return value is a summed integer. working out the "Try" block
def sum_integers(set: int) -> int:
    for i in set:
        if i < 0:
            raise NegativeNumber
        elif i % 2 == 0:
            raise OddNumber
    return sum(set)
def isIndexInSet(set: int):
    num = int(input("Entry a index: "))
    return set[num]

def changeStrInNum():
    str = input("Entry a number: ")
    try:
        str_float = float(str)
    except ValueError:
        print("There are several characters in the string or a comma is used")
    else:
        return str_float

def sqrtNum():
    num = input("Entry a number: ")
    try:
        num_f = float(num)
    except ValueError:
        print("There are several characters in the string or a comma is used")
    else:
        try:
            return math.sqrt(num_f)
        except ValueError:
            print("Negative a number or a comma is used")
        except NameError:
            print("Did you forget to import 'math'?")
    
    

if __name__ == "__main__":
    
    #Task1,2
    print("Task 1: Entry second number 0")
    division()
    print("\nTask 2: Enter a character ")
    division()
    #Task  3
    print("\nTask 3:")
    print("Below generation random set")
    set = [random.randint(-2, 10) for _ in range(10)]
    print(f"{set}")
    
    try:
        result = sum_integers(set)
    except OddNumber as e:
        print(e)
    except NegativeNumber as e:
        print(e)
    else:
        print(f"Result sum: {result}")
    set = [1, 3, 5, 5, 3]
    print(f"\nA new set {set} to verify that the function is working. Value: {sum_integers(set)}")
    
    #Task4
    print("\nTask 4:")
    print("Function is working and searches for the index value")
    try:
        num_index = isIndexInSet(set)
    except IndexError:
        print("This index not found")
    else:
        print(f"Return: {num_index}")
    
    #Task 5
    print("\nTask 5:")
    print("Enter a number to convert it to the float type. If the number is not an integer, use a dot.")
    print("Result:", changeStrInNum())
    
    #Task 6 (comment line number 2)
    print("\nTask 6:")
    print("Enter a number to calculate the square root of the number")
    print("Result:", sqrtNum())
    
