from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import operator
import ast


app = FastAPI(title="Калькулятор")

current_expression = ""

class Operation(BaseModel):
    a: float
    b: float
    op: str # + - / *
    
class Expression(BaseModel):
    expression: str # (а+b)* c + (d - e)/(f-g)
    

@app.post("/add")
async def add(data: Operation):
    return {"result" : data.a + data.b}

@app.post("/subtract")
async def subtract(data: Operation):
    return {"result" : data.a - data.b}

@app.post("/multiply")
async def multiply(data: Operation):
    return {"result" : data.a * data.b}

@app.post("/divide")
async def divide(data: Operation):
    if data.b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль запрещено")
    return {"result" : data.a / data.b}

@app.post("/expression/add")
async def add_expression(data: Expression):
    global current_expression
    current_expression = data.expression
    return {"message" : "Выражние сохранено", "expression" : current_expression}

@app.get("/expression/view")
async def view_expression():
    if not current_expression:
        return {"message" : "Пусто"}
    return {"expression" : current_expression}

@app.get("/expression/evaluate")
async def evaluate_expression():
    if not current_expression:
        raise HTTPException(status_code=400, detail="Выражение не задано")
    
    try:
        result = safe_eval(current_expression)
        return {"expression" : current_expression, "result" : result}
    except:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении: {e}")

def safe_eval(expr: str):
    # Разрешённые операции
    allowed_ops = {
        ast.Add: operator.add,    # "+"
        ast.Sub: operator.sub,    # "-"
        ast.Mult: operator.mul,   # "*"
        ast.Div: operator.truediv,# "/"
        ast.USub: operator.neg,   # унарный минус, например -5
    }

    # Рекурсивная функция для обхода дерева
    def eval_node(node):
        if isinstance(node, ast.BinOp):
            # бинарная операция (a + b, a * b и т.д.)
            left = eval_node(node.left)
            right = eval_node(node.right)
            op_type = type(node.op)
            if op_type in allowed_ops:
                return allowed_ops[op_type](left, right)
            else:
                raise ValueError("Недопустимая операция")

        elif isinstance(node, ast.UnaryOp):
            # например "-5"
            return allowed_ops[type(node.op)](eval_node(node.operand))

        elif isinstance(node, ast.Constant):
            # просто число
            return node.value

        else:
            # если что-то другое — запретить
            raise ValueError("Недопустимый элемент в выражении")

    # Парсим строку в AST
    parsed = ast.parse(expr, mode="eval")

    # Вычисляем корень дерева
    return eval_node(parsed.body)

@app.get("/test-error")
def test_error():
    raise HTTPException(status_code=418, detail="Я чайник ☕")