from dataclasses import dataclass, field
from typing import List, Optional


# Formato compartido del AST (Semanas 3 y 4).
# Todos los nodos tienen to_dict() para enviarlos a la página, igual que NumNode y BinOpNode del taller.


@dataclass
class Node:
    line: int = 0

    def to_dict(self) -> dict:
        raise NotImplementedError


@dataclass
class Expression(Node):
    # El verificador de tipos (Ramírez) llena este campo con el tipo calculado
    inferred_type: Optional[str] = None


@dataclass
class NumberLiteral(Expression):
    value: float = 0
    literal_type: str = "entero"

    def to_dict(self) -> dict:
        return {"kind": "NumberLiteral", "value": self.value, "type": self.literal_type}


@dataclass
class MoneyLiteral(Expression):
    value: int = 0

    def to_dict(self) -> dict:
        return {"kind": "MoneyLiteral", "value": self.value}


@dataclass
class StringLiteral(Expression):
    value: str = ""

    def to_dict(self) -> dict:
        return {"kind": "StringLiteral", "value": self.value}


@dataclass
class Identifier(Expression):
    name: str = ""

    def to_dict(self) -> dict:
        return {"kind": "Identifier", "name": self.name}


@dataclass
class BinaryOperation(Expression):
    operator: str = "+"
    left: Optional[Expression] = None
    right: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {
            "kind": "BinaryOperation",
            "operator": self.operator,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }


@dataclass
class Comparison(Expression):
    operator: str = "<="
    left: Optional[Expression] = None
    right: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {
            "kind": "Comparison",
            "operator": self.operator,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }


@dataclass
class FunctionCall(Expression):
    name: str = ""
    arguments: List[Expression] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"kind": "FunctionCall", "name": self.name, "arguments": [a.to_dict() for a in self.arguments]}


@dataclass
class Statement(Node):
    pass


@dataclass
class Block(Node):
    statements: List[Statement] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"kind": "Block", "statements": [s.to_dict() for s in self.statements]}


@dataclass
class VariableDeclaration(Statement):
    name: str = ""
    declared_type: str = ""
    value: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {
            "kind": "VariableDeclaration",
            "name": self.name,
            "type": self.declared_type,
            "value": self.value.to_dict() if self.value else None,
        }


@dataclass
class Assignment(Statement):
    name: str = ""
    value: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {"kind": "Assignment", "name": self.name, "value": self.value.to_dict() if self.value else None}


@dataclass
class IfStatement(Statement):
    condition: Optional[Comparison] = None
    then_block: Optional[Block] = None
    else_block: Optional[Block] = None

    def to_dict(self) -> dict:
        return {
            "kind": "IfStatement",
            "condition": self.condition.to_dict() if self.condition else None,
            "then": self.then_block.to_dict() if self.then_block else None,
            "else": self.else_block.to_dict() if self.else_block else None,
        }


@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {"kind": "ReturnStatement", "value": self.value.to_dict() if self.value else None}


@dataclass
class PayStatement(Statement):
    value: Optional[Expression] = None

    def to_dict(self) -> dict:
        return {"kind": "PayStatement", "value": self.value.to_dict() if self.value else None}


@dataclass
class ConstantDeclaration(Node):
    name: str = ""
    declared_type: str = ""
    value: Optional[Expression] = None
    # Valor calculado al evaluar el AST de la constante (Semana 4)
    evaluated_value: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "kind": "ConstantDeclaration",
            "name": self.name,
            "type": self.declared_type,
            "value": self.value.to_dict() if self.value else None,
            "evaluated": self.evaluated_value,
        }


@dataclass
class Parameter(Node):
    name: str = ""
    declared_type: str = ""

    def to_dict(self) -> dict:
        return {"kind": "Parameter", "name": self.name, "type": self.declared_type}


@dataclass
class FunctionDeclaration(Node):
    name: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    return_type: str = ""
    body: Optional[Block] = None

    def to_dict(self) -> dict:
        return {
            "kind": "FunctionDeclaration",
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "returnType": self.return_type,
            "body": self.body.to_dict() if self.body else None,
        }


@dataclass
class EmployeeBlock(Node):
    body: Optional[Block] = None

    def to_dict(self) -> dict:
        return {"kind": "EmployeeBlock", "body": self.body.to_dict() if self.body else None}


@dataclass
class Program(Node):
    constants: List[ConstantDeclaration] = field(default_factory=list)
    functions: List[FunctionDeclaration] = field(default_factory=list)
    employee_block: Optional[EmployeeBlock] = None

    def to_dict(self) -> dict:
        return {
            "kind": "Program",
            "constants": [c.to_dict() for c in self.constants],
            "functions": [f.to_dict() for f in self.functions],
            "employeeBlock": self.employee_block.to_dict() if self.employee_block else None,
        }


# Campos que trae cada empleado desde la tabla de la página.
# Entran como variables ya declaradas en el ámbito del bloque "para cada empleado".
EMPLOYEE_FIELDS = {"nombre": "texto", "salario": "dinero", "extras": "entero"}
