from typing import List

from .ast_nodes import Program
from .ir import TacInstruction


class IRGenerator:
    """Fase 4 · Semana 7 · Responsable: Mora.

    "Desenrolla" el AST en código de tres direcciones con temporales t1, t2... y etiquetas L1, L2...

    Ejemplo esperado para:  si salario <= TOPE_AUXILIO { devengado = devengado + AUXILIO }
        t1 = salario <= TOPE_AUXILIO
        ifFalse t1 goto L1
        t2 = devengado + AUXILIO
        devengado = t2
        L1:
    """

    def __init__(self):
        self.instructions: List[TacInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op: str, arg1=None, arg2=None, res=None) -> TacInstruction:
        instruction = TacInstruction(op, None if arg1 is None else str(arg1), None if arg2 is None else str(arg2), res)
        self.instructions.append(instruction)
        return instruction

    def generate(self, program: Program) -> List[TacInstruction]:
        # TODO (Mora):
        # 1. Constantes: "SMMLV = 1750905" (TacOp.ASSIGN).
        # 2. Funciones: begin_func nombre ... return valor ... end_func nombre.
        # 3. Bloque de empleado: begin_employee ... pay valor ... end_employee.
        # 4. Expresiones: recorrido postorden del árbol, una temporal por operación.
        # 5. Si: comparación en temporal, ifFalse tX goto Lsino, bloque, goto Lfin, Lsino:, bloque sino, Lfin:.
        # 6. Llamadas: param arg1, param arg2, tX = call nombre, 2.
        raise NotImplementedError("Generador de TAC pendiente")
