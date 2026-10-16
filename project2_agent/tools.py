
import ast
import operator
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool


# Student grades
GRADES = {
    "mona": {"math": 92, "ai": 81},
    "ali": {"math": 85, "ai": 90},
}


# Safe arithmetic operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression: str):
    """Evaluate a mathematical expression using allowed AST nodes only."""

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large.")

            return OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported mathematical expression.")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)


@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression using +, -, *, /, and **."""

    try:
        return str(safe_calculate(expression))
    except (ValueError, TypeError, SyntaxError, ZeroDivisionError, OverflowError) as error:
        return f"Error: {error}"


@tool
def current_datetime() -> str:
    """Get the current local date and time."""

    return datetime.now().astimezone().strftime(
        "%A %d %B %Y, %H:%M %Z"
    )


@tool
def get_student_grades(name: str) -> str:
    """Get the math and AI grades for a student by name."""

    student_name = name.strip().lower()
    grades = GRADES.get(student_name)

    if grades is None:
        return f"No student called {name}."

    return str(grades)


@tool
def save_note(note: str) -> str:
    """Append a note to notes.txt inside the project2_agent folder."""

    notes_path = Path(__file__).resolve().parent / "notes.txt"

    with notes_path.open("a", encoding="utf-8") as file:
        file.write(note.strip() + "\n")

    return f"Note saved: {note}"


ALL_TOOLS = [
    calculator,
    current_datetime,
    get_student_grades,
    save_note,
]
