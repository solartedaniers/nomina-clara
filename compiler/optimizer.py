import re
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional

from .ir import TacInstruction, TacOp

TEMP = re.compile(r"^t\d+$")
NUMBER = re.compile(r"^-?\d+(\.\d+)?$")

ARITHMETIC = {
    TacOp.ADD: lambda a, b: a + b,
    TacOp.SUB: lambda a, b: a - b,
    TacOp.MUL: lambda a, b: a * b,
    TacOp.DIV: lambda a, b: a / b,
}

# Operaciones cuyo resultado queda en res y que se pueden fusionar con una copia "x = tN" que las siga
PRODUCES_VALUE = set(ARITHMETIC) | {
    TacOp.ASSIGN, TacOp.CALL,
    TacOp.LESS, TacOp.LESS_EQUAL, TacOp.GREATER, TacOp.GREATER_EQUAL, TacOp.EQUAL, TacOp.NOT_EQUAL,
}

# Marcadores que abren y cierran regiones de código (funciones y bloque de empleado)
REGION_START = {TacOp.BEGIN_FUNCTION, TacOp.BEGIN_EMPLOYEE}
REGION_END = {TacOp.END_FUNCTION, TacOp.END_EMPLOYEE}


@dataclass
class OptimizationResult:
    instructions: List[TacInstruction]
    original_count: int
    steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tac": [i.to_dict() for i in self.instructions],
            "text": [i.to_text() for i in self.instructions],
            "originalCount": self.original_count,
            "optimizedCount": len(self.instructions),
            "removed": self.original_count - len(self.instructions),
            "steps": self.steps,
        }


def is_number(operand: Optional[str]) -> bool:
    return operand is not None and bool(NUMBER.match(operand))


def to_number(operand: str):
    return float(operand) if "." in operand else int(operand)


def format_number(value) -> str:
    # 3501810.0 -> "3501810"; 70036.20000000001 -> "70036.2"
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.10f}".rstrip("0").rstrip(".")
    return str(value)


class Optimizer:
    """Fase 6 · Semana 9 · Responsable: Mora.

    Pasadas sobre el TAC:
    1. Plegado de constantes: t1 = 2 * 1750905  ->  t1 = 3501810
    2. Propagación de constantes: reemplazar TOPE_AUXILIO y AUXILIO por su valor
    3. Eliminación de copias: t2 = a + b ; x = t2  ->  x = a + b
    Cada cambio se describe en steps para mostrarlo en la página.

    Las tres pasadas se repiten hasta que ya no cambia nada, porque una abre camino a la otra:
    propagar SMMLV deja "2 * 1750905", que ya se puede plegar.
    """

    MAX_ROUNDS = 20

    def __init__(self):
        self.steps: List[str] = []

    def optimize(self, instructions: List[TacInstruction]) -> OptimizationResult:
        # No se modifica la lista original: la página muestra el TAC antes y después
        code = [replace(instruction) for instruction in instructions]
        self.steps = []

        for _ in range(self.MAX_ROUNDS):
            changed = False
            changed |= self._propagate_constants(code)
            changed |= self._fold_constants(code)
            new_code = self._eliminate_copies(code)
            changed |= len(new_code) != len(code)
            code = new_code
            if not changed:
                break

        return OptimizationResult(code, len(instructions), list(self.steps))

    # ---------- 1. Plegado de constantes ----------

    def _fold_constants(self, code: List[TacInstruction]) -> bool:
        changed = False
        for instruction in code:
            if instruction.op not in ARITHMETIC:
                continue
            if not (is_number(instruction.arg1) and is_number(instruction.arg2)):
                continue
            left, right = to_number(instruction.arg1), to_number(instruction.arg2)
            if instruction.op == TacOp.DIV and right == 0:
                # La división por cero se deja para que la reporte la máquina virtual
                continue
            before = instruction.to_text()
            value = format_number(ARITHMETIC[instruction.op](left, right))
            instruction.op, instruction.arg1, instruction.arg2 = TacOp.ASSIGN, value, None
            self.steps.append(f"Plegado de constantes: {before}  →  {instruction.to_text()}")
            changed = True
        return changed

    # ---------- 2. Propagación de constantes ----------

    def _constant_values(self, code: List[TacInstruction]) -> Dict[str, str]:
        """Nombres que valen siempre lo mismo: constantes globales y temporales con un valor numérico."""
        assignments: Dict[str, int] = {}
        for instruction in code:
            if instruction.res and instruction.op not in (TacOp.LABEL, TacOp.GOTO, TacOp.IF_FALSE):
                assignments[instruction.res] = assignments.get(instruction.res, 0) + 1

        # Un parámetro o variable local con el mismo nombre de una constante la taparía: esa no se propaga
        shadowed = set()
        for instruction in code:
            if instruction.op == TacOp.BEGIN_FUNCTION and instruction.arg2:
                shadowed.update(p.strip() for p in instruction.arg2.split(","))

        values: Dict[str, str] = {}
        depth = 0
        for instruction in code:
            if instruction.res in shadowed:
                continue
            if instruction.op in REGION_START:
                depth += 1
            elif instruction.op in REGION_END:
                depth -= 1
            elif instruction.op == TacOp.ASSIGN and is_number(instruction.arg1) and assignments.get(instruction.res) == 1:
                # Global (fuera de funciones y del bloque de empleado) o temporal: se asignan una sola vez
                if depth == 0 or TEMP.match(instruction.res):
                    values[instruction.res] = instruction.arg1
        return values

    def _propagate_constants(self, code: List[TacInstruction]) -> bool:
        values = self._constant_values(code)
        if not values:
            return False

        changed = False
        for instruction in code:
            if instruction.op in (TacOp.BEGIN_FUNCTION, TacOp.END_FUNCTION, TacOp.CALL, TacOp.LABEL, TacOp.GOTO):
                continue
            for slot in ("arg1", "arg2"):
                operand = getattr(instruction, slot)
                if operand in values:
                    before = instruction.to_text()
                    setattr(instruction, slot, values[operand])
                    self.steps.append(
                        f"Propagación de constantes: {operand} vale {values[operand]}; {before}  →  {instruction.to_text()}"
                    )
                    changed = True
        return changed

    # ---------- 3. Eliminación de copias ----------

    def _eliminate_copies(self, code: List[TacInstruction]) -> List[TacInstruction]:
        uses = self._count_uses(code)
        result: List[TacInstruction] = []
        index = 0
        while index < len(code):
            current = code[index]
            following = code[index + 1] if index + 1 < len(code) else None
            if (
                following is not None
                and current.op in PRODUCES_VALUE
                and current.res is not None
                and TEMP.match(current.res)
                and following.op == TacOp.ASSIGN
                and following.arg1 == current.res
                and uses.get(current.res, 0) == 1
            ):
                merged = replace(current, res=following.res, line=following.line or current.line)
                self.steps.append(
                    f"Eliminación de copias: {current.to_text()} ; {following.to_text()}  →  {merged.to_text()}"
                )
                result.append(merged)
                index += 2
                continue

            # Temporales que quedaron con un valor ya propagado y nadie más usa: se eliminan
            if (
                current.op == TacOp.ASSIGN
                and current.res is not None
                and TEMP.match(current.res)
                and uses.get(current.res, 0) == 0
            ):
                self.steps.append(f"Eliminación de copias: {current.to_text()} ya no se usa y se elimina")
                index += 1
                continue

            result.append(current)
            index += 1
        return result

    @staticmethod
    def _count_uses(code: List[TacInstruction]) -> Dict[str, int]:
        uses: Dict[str, int] = {}
        for instruction in code:
            if instruction.op in (TacOp.BEGIN_FUNCTION, TacOp.END_FUNCTION, TacOp.CALL, TacOp.LABEL, TacOp.GOTO):
                operands: List[str] = []
            else:
                operands = [a for a in (instruction.arg1, instruction.arg2) if a is not None]
            for operand in operands:
                uses[operand] = uses.get(operand, 0) + 1
        return uses
