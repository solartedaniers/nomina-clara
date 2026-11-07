from dataclasses import dataclass, field
from typing import Dict, List

from .ir import TacInstruction, TacOp


@dataclass
class AssemblyResult:
    lines: List[str] = field(default_factory=list)
    spills: List[dict] = field(default_factory=list)
    unsupported: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"lines": self.lines, "spills": self.spills, "unsupported": self.unsupported}


class TargetCodeGenerator:
    """Fase 7 · Semana 10 · Responsable: Mora.

    Traducción a inglés del GeneradorCodigoObjetivo del profesor, con el mismo comportamiento:
    3 registros físicos, reutilización de registros y spill a la RAM cuando se llenan.
    La única diferencia es que en vez de print() devuelve las líneas y los spills.
    """

    PHYSICAL_REGISTERS = ["R0", "R1", "R2"]

    def __init__(self):
        self.register_map: Dict[str, str] = {}
        self.busy_registers: Dict[str, str] = {}
        self.spill_area: Dict[str, str] = {}
        self.stack_pointer = 0x2000
        self.result = AssemblyResult()

    def _emit(self, instruction: str) -> None:
        self.result.lines.append(instruction)

    def get_register(self, variable: str) -> str:
        # 1. Si la variable ya tiene registro, se reutiliza
        if variable in self.register_map:
            return self.register_map[variable]

        # 2. Buscar un registro libre
        for register in self.PHYSICAL_REGISTERS:
            if register not in self.busy_registers:
                self.register_map[variable] = register
                self.busy_registers[register] = variable
                return register

        # 3. Spill: se desaloja siempre R0 (misma política que el código del profesor)
        register_to_free = self.PHYSICAL_REGISTERS[0]
        evicted = self.busy_registers[register_to_free]
        address = f"0x{self.stack_pointer:X}"
        self.spill_area[evicted] = address
        self.stack_pointer += 4

        self._emit(f"STORE [{register_to_free}], [{address}]")
        self.result.spills.append({"variable": evicted, "register": register_to_free, "address": address})

        del self.register_map[evicted]
        self.register_map[variable] = register_to_free
        self.busy_registers[register_to_free] = variable
        return register_to_free

    def translate(self, instructions: List[TacInstruction]) -> AssemblyResult:
        for instruction in instructions:
            op, arg1, arg2, res = instruction.op, instruction.arg1, instruction.arg2, instruction.res

            # Si el operando 1 estaba desbordado en RAM, se carga antes de operarlo
            if arg1 in self.spill_area:
                aux_register = self.get_register(arg1)
                self._emit(f"LOAD [{aux_register}], [{self.spill_area[arg1]}]")

            if op == TacOp.ADD:
                target = self.get_register(res)
                self._emit(f"MOV [{target}], [{arg1}]")
                self._emit(f"ADD [{target}], [{arg2}]")
            elif op == TacOp.MUL:
                target = self.get_register(res)
                self._emit(f"MOV [{target}], [{arg1}]")
                self._emit(f"MUL [{target}], [{arg2}]")
            elif op == TacOp.SUB:
                target = self.get_register(res)
                self._emit(f"MOV [{target}], [{arg1}]")
                self._emit(f"SUB [{target}], [{arg2}]")
            elif op == TacOp.ASSIGN:
                target = self.get_register(res)
                self._emit(f"MOV [{target}], [{arg1}]")
            else:
                # TODO (Mora): agregar DIV, comparaciones (CMP), ifFalse/goto (JG, JL, JMP...),
                # etiquetas, param/call/return y pay. Mientras tanto se reportan como pendientes.
                self.result.unsupported.append(instruction.to_text())

        return self.result
