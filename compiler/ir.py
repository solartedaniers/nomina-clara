from dataclasses import dataclass
from typing import Optional


class TacOp:
    """Operaciones del TAC. Las aritméticas y relacionales usan el mismo símbolo del lenguaje."""

    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    ASSIGN = "="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    EQUAL = "=="
    NOT_EQUAL = "!="
    IF_FALSE = "ifFalse"
    GOTO = "goto"
    LABEL = "label"
    PARAM = "param"
    CALL = "call"
    RETURN = "return"
    PAY = "pay"
    BEGIN_FUNCTION = "begin_func"
    END_FUNCTION = "end_func"
    BEGIN_EMPLOYEE = "begin_employee"
    END_EMPLOYEE = "end_employee"


@dataclass
class TacInstruction:
    """Formato compartido del TAC: el mismo diccionario que recibe el generador del profesor."""

    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    res: Optional[str] = None

    def to_dict(self) -> dict:
        return {"op": self.op, "arg1": self.arg1, "arg2": self.arg2, "res": self.res}

    def to_text(self) -> str:
        if self.op == TacOp.LABEL:
            return f"{self.res}:"
        if self.op == TacOp.GOTO:
            return f"goto {self.res}"
        if self.op == TacOp.IF_FALSE:
            return f"ifFalse {self.arg1} goto {self.res}"
        if self.op == TacOp.ASSIGN:
            return f"{self.res} = {self.arg1}"
        if self.op == TacOp.PARAM:
            return f"param {self.arg1}"
        if self.op == TacOp.CALL:
            return f"{self.res} = call {self.arg1}, {self.arg2}"
        if self.op in (TacOp.RETURN, TacOp.PAY):
            return f"{self.op} {self.arg1}"
        if self.op in (TacOp.BEGIN_FUNCTION, TacOp.END_FUNCTION, TacOp.BEGIN_EMPLOYEE, TacOp.END_EMPLOYEE):
            return f"{self.op} {self.arg1 or ''}".strip()
        return f"{self.res} = {self.arg1} {self.op} {self.arg2}"
