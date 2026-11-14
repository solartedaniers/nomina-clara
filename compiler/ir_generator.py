from typing import List, Optional

from .ast_nodes import (
    Assignment,
    BinaryOperation,
    Block,
    Comparison,
    ConstantDeclaration,
    EmployeeBlock,
    Expression,
    FunctionCall,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    MoneyLiteral,
    NumberLiteral,
    PayStatement,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
)
from .ir import TacInstruction, TacOp


class IRGenerator:
    """Fase 4 · Semana 7 · Responsable: Mora.

    "Desenrolla" el AST en código de tres direcciones con temporales t1, t2... y etiquetas L1, L2...

    Ejemplo esperado para:  si salario <= TOPE_AUXILIO { devengado = devengado + AUXILIO }
        t1 = salario <= TOPE_AUXILIO
        ifFalse t1 goto L1
        t2 = devengado + AUXILIO
        devengado = t2
        L1:

    Orden del TAC completo (el mismo que espera la máquina virtual):
        1. Constantes globales           SMMLV = 1750905
        2. Funciones                     begin_func horas_extra ... return t3 ... end_func horas_extra
        3. Bloque de empleado            begin_employee ... pay t9 ... end_employee
    """

    def __init__(self):
        self.instructions: List[TacInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        # Línea del programa fuente que se está traduciendo; se copia en cada instrucción
        self.current_line: Optional[int] = None

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op: str, arg1=None, arg2=None, res=None) -> TacInstruction:
        instruction = TacInstruction(
            op,
            None if arg1 is None else str(arg1),
            None if arg2 is None else str(arg2),
            res,
            self.current_line,
        )
        self.instructions.append(instruction)
        return instruction

    def _at(self, node) -> None:
        # Los nodos escritos a mano en las pruebas traen line=0: en ese caso no se marca línea
        line = getattr(node, "line", 0)
        self.current_line = line if line else None

    # ---------- Programa ----------

    def generate(self, program: Program) -> List[TacInstruction]:
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

        # 1. Constantes: van primero porque la máquina virtual las guarda en el segmento Data
        for constant in program.constants:
            self._constant(constant)

        # 2. Funciones
        for function in program.functions:
            self._function(function)

        # 3. Bloque "para cada empleado"
        if program.employee_block is not None:
            self._employee_block(program.employee_block)

        self.current_line = None
        return self.instructions

    def _constant(self, constant: ConstantDeclaration) -> None:
        self._at(constant)
        value = self._expression(constant.value)
        self._at(constant)
        self.emit(TacOp.ASSIGN, value, None, constant.name)

    def _function(self, function: FunctionDeclaration) -> None:
        self._at(function)
        # arg2 lleva los parámetros separados por coma para que la máquina virtual los cargue en el frame
        params = ",".join(p.name for p in function.parameters)
        self.emit(TacOp.BEGIN_FUNCTION, function.name, params or None)
        self._block(function.body)
        self._at(function)
        self.emit(TacOp.END_FUNCTION, function.name)

    def _employee_block(self, block: EmployeeBlock) -> None:
        self._at(block)
        self.emit(TacOp.BEGIN_EMPLOYEE)
        self._block(block.body)
        self._at(block)
        self.emit(TacOp.END_EMPLOYEE)

    # ---------- Sentencias ----------

    def _block(self, block: Optional[Block]) -> None:
        if block is None:
            return
        for statement in block.statements:
            self._statement(statement)

    def _statement(self, statement: Statement) -> None:
        self._at(statement)

        if isinstance(statement, (VariableDeclaration, Assignment)):
            value = self._expression(statement.value)
            self._at(statement)
            self.emit(TacOp.ASSIGN, value, None, statement.name)

        elif isinstance(statement, IfStatement):
            self._if(statement)

        elif isinstance(statement, ReturnStatement):
            value = self._expression(statement.value)
            self._at(statement)
            self.emit(TacOp.RETURN, value)

        elif isinstance(statement, PayStatement):
            value = self._expression(statement.value)
            self._at(statement)
            self.emit(TacOp.PAY, value)

        else:
            raise NotImplementedError(f"Sentencia sin traducir a TAC: {type(statement).__name__}")

    def _if(self, statement: IfStatement) -> None:
        # Sin sino:                      Con sino:
        #   tX = a <= b                    tX = a <= b
        #   ifFalse tX goto L1             ifFalse tX goto L1
        #   ...bloque si...                ...bloque si...
        #   L1:                            goto L2
        #                                  L1:
        #                                  ...bloque sino...
        #                                  L2:
        condition = self._expression(statement.condition)
        else_label = self.new_label()
        self._at(statement)
        self.emit(TacOp.IF_FALSE, condition, None, else_label)

        self._block(statement.then_block)

        if statement.else_block is not None:
            end_label = self.new_label()
            self._at(statement)
            self.emit(TacOp.GOTO, None, None, end_label)
            self.emit(TacOp.LABEL, None, None, else_label)
            self._block(statement.else_block)
            self._at(statement)
            self.emit(TacOp.LABEL, None, None, end_label)
        else:
            self._at(statement)
            self.emit(TacOp.LABEL, None, None, else_label)

    # ---------- Expresiones ----------

    def _expression(self, node: Optional[Expression]) -> str:
        """Recorrido postorden: primero los hijos, luego la operación. Devuelve el operando del resultado."""
        if node is None:
            raise NotImplementedError("Expresión vacía en el AST")

        if isinstance(node, MoneyLiteral):
            return str(node.value)

        if isinstance(node, NumberLiteral):
            return self._number(node.value, node.literal_type)

        if isinstance(node, StringLiteral):
            return f'"{node.value}"'

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, (BinaryOperation, Comparison)):
            left = self._expression(node.left)
            right = self._expression(node.right)
            temp = self.new_temp()
            self._at(node)
            self.emit(node.operator, left, right, temp)
            return temp

        if isinstance(node, FunctionCall):
            # Primero se evalúan todos los argumentos y después se apilan con param, en orden
            arguments = [self._expression(argument) for argument in node.arguments]
            self._at(node)
            for argument in arguments:
                self.emit(TacOp.PARAM, argument)
            temp = self.new_temp()
            self.emit(TacOp.CALL, node.name, len(arguments), temp)
            return temp

        raise NotImplementedError(f"Expresión sin traducir a TAC: {type(node).__name__}")

    @staticmethod
    def _number(value, literal_type: str) -> str:
        if literal_type == "entero":
            return str(int(value))
        # repr da la forma más corta (1.25, 0.04) sin ceros de más
        return repr(float(value))
