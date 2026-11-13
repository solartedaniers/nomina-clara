import re
from typing import Dict, List, Optional

from .errors import RuntimeFault
from .ir import TacInstruction, TacOp
from .memory_manager import MemoryManager

TEMP = re.compile(r"^t\d+$")
NUMBER = re.compile(r"^-?\d+(\.\d+)?$")
EMPLOYEE_RECORD_BYTES = 12  # nombre, salario y extras: 3 palabras de 4 bytes


def round_pesos(value):
    # Redondeo comercial a pesos enteros (0.5 sube), sin el redondeo bancario de round()
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)


class VirtualMachine:
    """Ejecución · Semanas 4 y 8 · Responsable: Ramírez.

    Recorre el TAC optimizado por cada empleado y calcula el valor a pagar,
    usando los frames del MemoryManager (fase 5).

    Formato de TAC que entiende (ir.py):
        SMMLV = 1750905                    constantes, antes de las funciones
        begin_func horas_extra             arg2 opcional: parámetros "horas,valor_hora"
        t1 = a + b / t2 = a <= b           aritmética y comparaciones
        ifFalse t1 goto L1 / goto L1 / L1: saltos y etiquetas
        param x ... t3 = call f, 2         llamada con sus argumentos
        return t4 / end_func horas_extra
        begin_employee ... pay t9 ... end_employee
    """

    MAX_STEPS = 200_000

    def __init__(self, memory: MemoryManager, functions: Optional[Dict[str, List[str]]] = None):
        self.memory = memory
        # Parámetros de cada función, si no vienen en el arg2 de begin_func
        self.function_params: Dict[str, List[str]] = dict(functions or {})
        self.code: List[TacInstruction] = []
        self.labels: Dict[str, int] = {}
        self.function_start: Dict[str, int] = {}
        self.employee_start: Optional[int] = None
        self.steps = 0

    # ---------- Preparación ----------

    def _load(self, instructions: List[TacInstruction]) -> List[int]:
        """Ubica etiquetas, funciones y el bloque de empleado. Devuelve las instrucciones globales."""
        self.code = list(instructions)
        global_code: List[int] = []
        inside: Optional[str] = None
        for index, instruction in enumerate(self.code):
            op = instruction.op
            if op == TacOp.LABEL:
                self.labels[instruction.res] = index
            elif op == TacOp.BEGIN_FUNCTION:
                name = instruction.arg1
                self.function_start[name] = index + 1
                if instruction.arg2 and name not in self.function_params:
                    self.function_params[name] = [p.strip() for p in instruction.arg2.split(",") if p.strip()]
                inside = "func"
            elif op == TacOp.BEGIN_EMPLOYEE:
                self.employee_start = index + 1
                inside = "employee"
            elif op in (TacOp.END_FUNCTION, TacOp.END_EMPLOYEE):
                inside = None
            elif inside is None:
                global_code.append(index)
        if self.employee_start is None:
            raise RuntimeFault("El TAC no tiene bloque begin_employee")
        return global_code

    def _run_globals(self, indexes: List[int]) -> None:
        # Las constantes van al segmento Data; las temporales globales (t1 = 2 * SMMLV) solo viven aquí
        temps: Dict[str, object] = {}
        for index in indexes:
            instruction = self.code[index]
            if instruction.res is None:
                continue
            value = self._compute(instruction, lambda name: temps[name] if name in temps else self._value(name))
            if TEMP.match(instruction.res):
                temps[instruction.res] = value
            else:
                self.memory.store_global(instruction.res, value)

    # ---------- Ejecución ----------

    def run(self, instructions: List[TacInstruction], employees: List[dict]) -> List[dict]:
        global_code = self._load(instructions)

        # 1. Lista de empleados en el Heap (su tamaño solo se conoce en ejecución) y constantes en Data
        records = [dict(employee) for employee in employees]
        address = self.memory.allocate_heap(
            max(1, len(records)) * EMPLOYEE_RECORD_BYTES, f"lista_empleados ({len(records)} registros)", records
        )
        self._run_globals(global_code)

        # 2. Un frame por empleado
        payroll = []
        for number, employee in enumerate(records, start=1):
            self.memory.push_frame(f"empleado#{number}")
            self.memory.set_local("nombre", str(employee.get("nombre", "")))
            self.memory.set_local("salario", self._number(employee.get("salario", 0)))
            self.memory.set_local("extras", self._number(employee.get("extras", 0)))
            pay = self._execute(self.employee_start, TacOp.END_EMPLOYEE)
            frame = self.memory.pop_frame()
            if pay is None:
                raise RuntimeFault(f"El empleado #{number} terminó sin ejecutar 'pagar'")
            values = {
                name: round_pesos(value)
                for name, value in frame["locals"].items()
                if name != "nombre" and not TEMP.match(name)
            }
            payroll.append({"name": frame["locals"]["nombre"], "values": values, "pay": round_pesos(pay)})

        # 3. Al terminar la liquidación se libera el Heap
        self.memory.free_heap(address)
        return payroll

    def _execute(self, pc: int, end_op: str):
        """Ejecuta desde pc hasta end_op. Devuelve el valor de 'pay' o de 'return'."""
        pending_params: List[object] = []
        while pc < len(self.code):
            self.steps += 1
            if self.steps > self.MAX_STEPS:
                raise RuntimeFault("La ejecución superó el límite de pasos (¿ciclo infinito?)")
            instruction = self.code[pc]
            op = instruction.op

            if op == end_op:
                return None
            if op == TacOp.LABEL:
                pass
            elif op == TacOp.GOTO:
                pc = self._jump(instruction.res)
                continue
            elif op == TacOp.IF_FALSE:
                if not self._value(instruction.arg1):
                    pc = self._jump(instruction.res)
                    continue
            elif op == TacOp.PARAM:
                pending_params.append(self._value(instruction.arg1))
            elif op == TacOp.CALL:
                count = int(instruction.arg2 or len(pending_params))
                arguments = pending_params[len(pending_params) - count:] if count else []
                del pending_params[len(pending_params) - count:]
                result = self._call(instruction.arg1, arguments)
                if instruction.res:
                    self.memory.set_local(instruction.res, result)
            elif op in (TacOp.RETURN, TacOp.PAY):
                return self._value(instruction.arg1)
            elif op in (TacOp.BEGIN_FUNCTION, TacOp.END_FUNCTION, TacOp.BEGIN_EMPLOYEE, TacOp.END_EMPLOYEE):
                raise RuntimeFault(f"Instrucción '{op}' fuera de lugar en la posición {pc}")
            else:
                self.memory.set_local(instruction.res, self._compute(instruction, self._value))
            pc += 1
        raise RuntimeFault(f"El TAC terminó sin encontrar '{end_op}'")

    def _call(self, name: str, arguments: List[object]):
        if name not in self.function_start:
            raise RuntimeFault(f"La función '{name}' no existe en el TAC")
        params = self.function_params.get(name, [])
        if len(params) != len(arguments):
            raise RuntimeFault(f"La función '{name}' espera {len(params)} argumento(s) y recibió {len(arguments)}")
        # Cada llamada abre su frame encima del empleado y se destruye al retornar
        self.memory.push_frame(name)
        for param, value in zip(params, arguments):
            self.memory.set_local(param, value)
        result = self._execute(self.function_start[name], TacOp.END_FUNCTION)
        self.memory.pop_frame()
        if result is None:
            raise RuntimeFault(f"La función '{name}' terminó sin 'retornar'")
        return result

    # ---------- Valores ----------

    def _jump(self, label: str) -> int:
        if label not in self.labels:
            raise RuntimeFault(f"La etiqueta '{label}' no existe")
        return self.labels[label]

    @staticmethod
    def _number(value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        text = str(value).replace("$", "").replace(".", "").strip() if str(value).startswith("$") else str(value)
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                raise RuntimeFault(f"El valor '{value}' no es un número")

    def _value(self, operand):
        if operand is None:
            raise RuntimeFault("Falta un operando en el TAC")
        text = str(operand)
        if NUMBER.match(text) or text.startswith("$"):
            return self._number(text)
        if len(text) >= 2 and text[0] == text[-1] == '"':
            return text[1:-1]
        if text in ("verdadero", "True"):
            return True
        if text in ("falso", "False"):
            return False
        return self.memory.get_value(text)

    @staticmethod
    def _compute(instruction: TacInstruction, read):
        op = instruction.op
        if op == TacOp.ASSIGN:
            return read(instruction.arg1)
        left = read(instruction.arg1)
        right = read(instruction.arg2)
        if op == TacOp.ADD:
            return left + right
        if op == TacOp.SUB:
            return left - right
        if op == TacOp.MUL:
            return left * right
        if op == TacOp.DIV:
            if right == 0:
                raise RuntimeFault(f"División por cero en {instruction.to_text()}")
            return left / right
        comparisons = {
            TacOp.LESS: lambda: left < right,
            TacOp.LESS_EQUAL: lambda: left <= right,
            TacOp.GREATER: lambda: left > right,
            TacOp.GREATER_EQUAL: lambda: left >= right,
            TacOp.EQUAL: lambda: left == right,
            TacOp.NOT_EQUAL: lambda: left != right,
        }
        if op in comparisons:
            return comparisons[op]()
        raise RuntimeFault(f"Operación de TAC no soportada: '{op}'")
