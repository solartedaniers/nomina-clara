import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .ir import TacInstruction, TacOp

TEMP = re.compile(r"^t\d+$")

# Para "ifFalse tX goto L" se salta cuando la comparación es FALSA, así que se usa el salto contrario:
# t1 = salario <= tope ; ifFalse t1 goto L1   ->   CMP salario, tope ; JG L1  (salta si salario > tope)
INVERSE_JUMP = {
    TacOp.LESS_EQUAL: "JG",
    TacOp.LESS: "JGE",
    TacOp.GREATER: "JLE",
    TacOp.GREATER_EQUAL: "JL",
    TacOp.EQUAL: "JNE",
    TacOp.NOT_EQUAL: "JE",
}

ARITHMETIC = {TacOp.ADD: "ADD", TacOp.SUB: "SUB", TacOp.MUL: "MUL", TacOp.DIV: "DIV"}


@dataclass
class AssemblyResult:
    lines: List[str] = field(default_factory=list)
    spills: List[dict] = field(default_factory=list)
    unsupported: List[str] = field(default_factory=list)
    # R0, R1 y R2 en el momento de mayor ocupación (qué variable tenía cada uno)
    registers: Dict[str, Optional[str]] = field(default_factory=dict)
    # Opcional para subir nota: spills con el asignador del profesor vs. liberando temporales muertas
    comparison: Optional[dict] = None

    def to_dict(self) -> dict:
        data = {"lines": self.lines, "spills": self.spills, "unsupported": self.unsupported, "registers": self.registers}
        if self.comparison is not None:
            data["comparison"] = self.comparison
        return data


class TargetCodeGenerator:
    """Fase 7 · Semana 10 · Responsable: Mora.

    Traducción a inglés del GeneradorCodigoObjetivo del profesor, con el mismo comportamiento:
    3 registros físicos, reutilización de registros y spill a la RAM cuando se llenan.
    En vez de print() devuelve las líneas y los spills.

    Lo que se le agregó al código del profesor:
    - DIV, CMP y los saltos (JMP, JG, JGE, JL, JLE, JE, JNE) con sus etiquetas.
    - Llamadas: PUSH de cada parámetro, CALL, y el valor de retorno en el registro especial RV.
    - Cuando el resultado es una variable del programa (no una temporal) se guarda en memoria: MOV [x], [Rn].
    - Si un operando está en un registro se usa el registro; si estaba desbordado se carga con LOAD.
    - free_dead_temps=True libera el registro de una temporal cuando ya no se vuelve a usar
      (el asignador del profesor nunca libera registros).
    """

    PHYSICAL_REGISTERS = ["R0", "R1", "R2"]
    RETURN_REGISTER = "RV"

    def __init__(self, free_dead_temps: bool = False):
        self.free_dead_temps = free_dead_temps
        self.register_map: Dict[str, str] = {}
        self.busy_registers: Dict[str, str] = {}
        self.spill_area: Dict[str, str] = {}
        self.stack_pointer = 0x2000
        self.result = AssemblyResult()
        # Última comparación vista: tX -> operador, para escoger el salto de ifFalse
        self.comparisons: Dict[str, str] = {}
        self.last_use: Dict[str, int] = {}
        self.peak_busy = -1

    def _emit(self, instruction: str) -> None:
        self.result.lines.append(instruction)

    # ---------- Registros (código del profesor) ----------

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

        self._snapshot_registers(force=True)
        self._emit(f"STORE [{register_to_free}], [{address}]")
        self.result.spills.append({"variable": evicted, "register": register_to_free, "address": address})

        del self.register_map[evicted]
        self.register_map[variable] = register_to_free
        self.busy_registers[register_to_free] = variable
        return register_to_free

    def _snapshot_registers(self, force: bool = False) -> None:
        # Se guarda la foto de los registros cuando están más llenos (o justo antes del primer spill)
        busy = len(self.busy_registers)
        if (force and not self.result.spills) or busy > self.peak_busy:
            self.peak_busy = busy if not force else len(self.PHYSICAL_REGISTERS) + 1
            self.result.registers = {r: self.busy_registers.get(r) for r in self.PHYSICAL_REGISTERS}

    def _release(self, variable: str) -> None:
        register = self.register_map.pop(variable, None)
        if register is not None:
            self.busy_registers.pop(register, None)

    def _reset_registers(self) -> None:
        # Al entrar a una función o al bloque de empleado los registros empiezan vacíos
        self.register_map.clear()
        self.busy_registers.clear()

    # ---------- Operandos ----------

    def _operand(self, operand: Optional[str]) -> str:
        """Devuelve [Rn] si el valor está en un registro, o lo carga si estaba desbordado en la RAM."""
        if operand is None:
            return "[]"
        if operand in self.spill_area:
            address = self.spill_area.pop(operand)
            register = self.get_register(operand)
            self._emit(f"LOAD [{register}], [{address}]")
            return f"[{register}]"
        if operand in self.register_map:
            return f"[{self.register_map[operand]}]"
        return f"[{operand}]"

    def _after_spill(self, operand: Optional[str], text: str, target: str) -> str:
        # Si al pedir el registro destino se desalojó justo el segundo operando, el MOV lo pisaría:
        # se lee desde la dirección de la RAM donde quedó guardado
        if operand in self.spill_area and text == f"[{target}]":
            return f"[{self.spill_area[operand]}]"
        return text

    def _store_if_variable(self, name: str, register: str) -> None:
        # Las temporales viven solo en registros; las variables del programa se guardan en memoria
        if not TEMP.match(name):
            self._emit(f"MOV [{name}], [{register}]")
            self._release(name)

    def _free_dead(self, index: int, instruction: TacInstruction, slots=("arg1", "arg2")) -> None:
        # Solo el registro del primer operando se puede reutilizar como destino (x = x op y);
        # el del segundo se libera después de emitir, para no pisarlo antes de leerlo
        if not self.free_dead_temps:
            return
        for operand in (getattr(instruction, slot) for slot in slots):
            if operand and TEMP.match(operand) and self.last_use.get(operand) == index:
                self._release(operand)

    def _compute_last_use(self, instructions: List[TacInstruction]) -> None:
        self.last_use = {}
        for index, instruction in enumerate(instructions):
            if instruction.op in (TacOp.CALL, TacOp.BEGIN_FUNCTION, TacOp.END_FUNCTION):
                continue
            for operand in (instruction.arg1, instruction.arg2):
                if operand and TEMP.match(operand):
                    self.last_use[operand] = index

    # ---------- Traducción ----------

    def translate(self, instructions: List[TacInstruction]) -> AssemblyResult:
        self._translate(instructions)

        # Comparación del opcional: se vuelve a traducir liberando las temporales muertas
        if not self.free_dead_temps:
            improved = TargetCodeGenerator(free_dead_temps=True)._translate(instructions)
            self.result.comparison = {
                "professorSpills": len(self.result.spills),
                "freeingSpills": len(improved.spills),
                "freeingLines": improved.lines,
            }
        return self.result

    def _translate(self, instructions: List[TacInstruction]) -> AssemblyResult:
        self._compute_last_use(instructions)

        for index, instruction in enumerate(instructions):
            op, arg1, arg2, res = instruction.op, instruction.arg1, instruction.arg2, instruction.res
            self._snapshot_registers()

            if op in ARITHMETIC:
                left, right = self._operand(arg1), self._operand(arg2)
                self._free_dead(index, instruction, ("arg1",))
                target = self.get_register(res)
                right = self._after_spill(arg2, right, target)
                if left != f"[{target}]":
                    self._emit(f"MOV [{target}], {left}")
                self._emit(f"{ARITHMETIC[op]} [{target}], {right}")
                self._free_dead(index, instruction, ("arg2",))
                self._store_if_variable(res, target)

            elif op == TacOp.ASSIGN:
                value = self._operand(arg1)
                self._free_dead(index, instruction)
                target = self.get_register(res)
                if value != f"[{target}]":
                    self._emit(f"MOV [{target}], {value}")
                self._store_if_variable(res, target)

            elif op in INVERSE_JUMP:
                # La comparación deja las banderas listas; el salto lo pone el ifFalse que sigue
                left, right = self._operand(arg1), self._operand(arg2)
                self._free_dead(index, instruction, ("arg1",))
                target = self.get_register(res)
                right = self._after_spill(arg2, right, target)
                if left != f"[{target}]":
                    self._emit(f"MOV [{target}], {left}")
                self._emit(f"CMP [{target}], {right}")
                self._free_dead(index, instruction, ("arg2",))
                self.comparisons[res] = op
                self._release(res)

            elif op == TacOp.IF_FALSE:
                comparison = self.comparisons.get(arg1)
                if comparison is not None:
                    self._emit(f"{INVERSE_JUMP[comparison]} {res}")
                else:
                    # Condición que no viene de una comparación (p. ej. ya plegada): falso es 0
                    self._emit(f"CMP {self._operand(arg1)}, [0]")
                    self._emit(f"JE {res}")

            elif op == TacOp.GOTO:
                self._emit(f"JMP {res}")

            elif op == TacOp.LABEL:
                self._emit(f"{res}:")

            elif op == TacOp.PARAM:
                self._emit(f"PUSH {self._operand(arg1)}")
                self._free_dead(index, instruction)

            elif op == TacOp.CALL:
                self._emit(f"CALL {arg1}")
                if res:
                    target = self.get_register(res)
                    self._emit(f"MOV [{target}], [{self.RETURN_REGISTER}]")
                    self._store_if_variable(res, target)

            elif op == TacOp.RETURN:
                self._emit(f"MOV [{self.RETURN_REGISTER}], {self._operand(arg1)}")
                self._emit("RET")

            elif op == TacOp.PAY:
                # Pseudo-instrucción de la máquina de Nómina Clara: entrega el neto del empleado
                self._emit(f"PAY {self._operand(arg1)}")

            elif op == TacOp.BEGIN_FUNCTION:
                self._reset_registers()
                self._emit(f"{arg1}:")

            elif op == TacOp.END_FUNCTION:
                self._reset_registers()

            elif op == TacOp.BEGIN_EMPLOYEE:
                self._reset_registers()
                self._emit("EMPLOYEE:")

            elif op == TacOp.END_EMPLOYEE:
                self._emit("HALT")
                self._reset_registers()

            else:
                self.result.unsupported.append(instruction.to_text())

        self._snapshot_registers()
        return self.result
