from typing import Optional

from .ast_nodes import (
    EMPLOYEE_FIELDS,
    Assignment,
    BinaryOperation,
    Block,
    Comparison,
    ConstantDeclaration,
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
from .errors import SemanticError
from .symbol_table import SymbolKind, SymbolTable

MONEY = "dinero"
INTEGER = "entero"
DECIMAL = "decimal"
TEXT = "texto"
LOGICAL = "logico"
NUMBERS = (INTEGER, DECIMAL)

VERBS = {"+": "sumar", "-": "restar", "*": "multiplicar", "/": "dividir"}


class TypeChecker:
    """Fase 3b · Semana 6 · Responsable: Ramírez.

    Recorre el AST, llena la tabla de símbolos con los ámbitos y valida los tipos.
    Es el "guardián semántico" del laboratorio de la semana 6: cada nodo devuelve su tipo
    y si la combinación no está en la tabla de reglas se lanza SemanticError con la línea.

    Reglas (sección 2 del documento):
    - dinero +/- dinero -> dinero
    - dinero * o / (entero | decimal) -> dinero
    - entero con decimal -> decimal (promoción implícita)
    - comparación entre dos dineros o dos números -> logico
    - la condición de "si" debe ser logico
    - "retornar" debe coincidir con el tipo de la función; "pagar" debe ser dinero
    - llamada: mismo número y tipo de argumentos que los parámetros
    """

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.current_function: Optional[FunctionDeclaration] = None
        self.in_employee_block = False
        self.current_line = 0

    # ---------- Programa ----------

    def check(self, program: Program) -> None:
        table = self.symbol_table
        table.enter_scope("global")

        # 1. Constantes, en orden: cada una puede usar las anteriores (TOPE_AUXILIO = 2 * SMMLV)
        for constant in program.constants:
            self._check_constant(constant)

        # 2. Primero se declaran todas las funciones, así una puede llamar a otra (o a sí misma)
        for function in program.functions:
            table.declare(
                function.name,
                self._signature(function),
                SymbolKind.FUNCTION,
                function.line,
                param_types=[p.declared_type for p in function.parameters],
                return_type=function.return_type,
            )
        for function in program.functions:
            self._check_function(function)

        # 3. Bloque "para cada empleado": los campos de la tabla de la página ya vienen declarados
        if program.employee_block is None:
            raise SemanticError("Falta el bloque 'para cada empleado'", program.line)
        block = program.employee_block
        table.enter_scope("empleado")
        for name, field_type in EMPLOYEE_FIELDS.items():
            table.declare(name, field_type, SymbolKind.VARIABLE, block.line)
        self.in_employee_block = True
        statements = block.body.statements if block.body else []
        self._check_block_statements(statements)
        if not self._contains(statements, PayStatement):
            raise SemanticError("El bloque 'para cada empleado' debe tener una sentencia 'pagar'", block.line)
        self.in_employee_block = False
        table.exit_scope()

        table.exit_scope()

    @staticmethod
    def _signature(function: FunctionDeclaration) -> str:
        params = ", ".join(p.declared_type for p in function.parameters)
        return f"funcion({params}): {function.return_type}"

    def _check_constant(self, constant: ConstantDeclaration) -> None:
        self.current_line = constant.line
        value_type = self._expr(constant.value)
        self._require_assignable(value_type, constant.declared_type, f"la constante '{constant.name}'", constant.line)
        self.symbol_table.declare(constant.name, constant.declared_type, SymbolKind.CONSTANT, constant.line)

    def _check_function(self, function: FunctionDeclaration) -> None:
        table = self.symbol_table
        table.enter_scope(function.name)
        for parameter in function.parameters:
            table.declare(parameter.name, parameter.declared_type, SymbolKind.PARAMETER, parameter.line or function.line)
        self.current_function = function
        statements = function.body.statements if function.body else []
        self._check_block_statements(statements)
        if not self._contains(statements, ReturnStatement):
            raise SemanticError(f"La función '{function.name}' debe tener 'retornar'", function.line)
        self.current_function = None
        table.exit_scope()

    # ---------- Sentencias ----------

    def _check_block_statements(self, statements) -> None:
        for statement in statements:
            self._statement(statement)

    def _nested_block(self, block: Optional[Block], scope_name: str) -> None:
        # Cada "si" / "sino" abre su propio ámbito, pero usa el frame de la función o del empleado
        self.symbol_table.enter_scope(scope_name, owns_frame=False)
        self._check_block_statements(block.statements if block else [])
        self.symbol_table.exit_scope()

    def _statement(self, statement: Statement) -> None:
        self.current_line = statement.line or self.current_line
        line = self.current_line

        if isinstance(statement, VariableDeclaration):
            value_type = self._expr(statement.value)
            self._require_assignable(value_type, statement.declared_type, f"la variable '{statement.name}'", line)
            self.symbol_table.declare(statement.name, statement.declared_type, SymbolKind.VARIABLE, line)

        elif isinstance(statement, Assignment):
            symbol = self.symbol_table.lookup(statement.name)
            if symbol is None:
                raise SemanticError(f"La variable '{statement.name}' no ha sido declarada", line)
            if symbol.kind == SymbolKind.CONSTANT:
                raise SemanticError(f"No se puede modificar la constante '{statement.name}'", line)
            if symbol.kind == SymbolKind.FUNCTION:
                raise SemanticError(f"'{statement.name}' es una función, no se le puede asignar un valor", line)
            value_type = self._expr(statement.value)
            self._require_assignable(value_type, symbol.type, f"la variable '{statement.name}'", line)

        elif isinstance(statement, IfStatement):
            condition_type = self._expr(statement.condition)
            if condition_type != LOGICAL:
                raise SemanticError(f"La condición de 'si' debe ser logico y es {condition_type}", line)
            self._nested_block(statement.then_block, f"si:{line}")
            if statement.else_block is not None:
                self._nested_block(statement.else_block, f"sino:{line}")

        elif isinstance(statement, ReturnStatement):
            if self.current_function is None:
                raise SemanticError("'retornar' solo se puede usar dentro de una función", line)
            value_type = self._expr(statement.value)
            expected = self.current_function.return_type
            if not self._assignable(value_type, expected):
                raise SemanticError(
                    f"La función '{self.current_function.name}' debe retornar {expected} y retorna {value_type}", line
                )

        elif isinstance(statement, PayStatement):
            if not self.in_employee_block or self.current_function is not None:
                raise SemanticError("'pagar' solo se puede usar en el bloque 'para cada empleado'", line)
            value_type = self._expr(statement.value)
            if value_type != MONEY:
                raise SemanticError(f"'pagar' debe recibir dinero y recibe {value_type}", line)

        else:
            raise SemanticError(f"Sentencia no reconocida: {type(statement).__name__}", line)

    # ---------- Expresiones ----------

    def _expr(self, expression: Optional[Expression]) -> str:
        if expression is None:
            raise SemanticError("Falta una expresión", self.current_line)
        line = expression.line or self.current_line
        result = self._expr_type(expression, line)
        expression.inferred_type = result
        return result

    def _expr_type(self, expression: Expression, line: int) -> str:
        if isinstance(expression, MoneyLiteral):
            return MONEY
        if isinstance(expression, NumberLiteral):
            return DECIMAL if expression.literal_type == DECIMAL else INTEGER
        if isinstance(expression, StringLiteral):
            return TEXT

        if isinstance(expression, Identifier):
            symbol = self.symbol_table.lookup(expression.name)
            if symbol is None:
                raise SemanticError(f"La variable '{expression.name}' no ha sido declarada o está fuera de su ámbito", line)
            if symbol.kind == SymbolKind.FUNCTION:
                raise SemanticError(f"'{expression.name}' es una función: hay que llamarla con paréntesis", line)
            return symbol.type

        if isinstance(expression, BinaryOperation):
            left = self._expr(expression.left)
            right = self._expr(expression.right)
            return self._arithmetic(expression.operator, left, right, line)

        if isinstance(expression, Comparison):
            left = self._expr(expression.left)
            right = self._expr(expression.right)
            both_money = left == MONEY and right == MONEY
            both_numbers = left in NUMBERS and right in NUMBERS
            same_equality = left == right and left in (TEXT, LOGICAL) and expression.operator in ("==", "!=")
            if both_money or both_numbers or same_equality:
                return LOGICAL
            raise SemanticError(f"No se puede comparar {left} con {right} usando '{expression.operator}'", line)

        if isinstance(expression, FunctionCall):
            return self._call(expression, line)

        raise SemanticError(f"Expresión no reconocida: {type(expression).__name__}", line)

    @staticmethod
    def _arithmetic(operator: str, left: str, right: str, line: int) -> str:
        if left in NUMBERS and right in NUMBERS:
            if operator == "/" or DECIMAL in (left, right):
                return DECIMAL  # promoción implícita de entero a decimal
            return INTEGER
        if operator in ("+", "-") and left == MONEY and right == MONEY:
            return MONEY
        if operator == "*" and MONEY in (left, right) and (left in NUMBERS or right in NUMBERS):
            return MONEY
        if operator == "/" and left == MONEY and right in NUMBERS:
            return MONEY
        verb = VERBS.get(operator, f"operar con '{operator}'")
        raise SemanticError(f"No se puede {verb} {left} con {right}", line)

    def _call(self, call: FunctionCall, line: int) -> str:
        symbol = self.symbol_table.lookup(call.name)
        if symbol is None:
            raise SemanticError(f"La función '{call.name}' no ha sido declarada", line)
        if symbol.kind != SymbolKind.FUNCTION:
            raise SemanticError(f"'{call.name}' no es una función", line)
        expected = symbol.param_types
        if len(call.arguments) != len(expected):
            raise SemanticError(
                f"La función '{call.name}' espera {len(expected)} argumento(s) y recibió {len(call.arguments)}", line
            )
        for position, (argument, param_type) in enumerate(zip(call.arguments, expected), start=1):
            argument_type = self._expr(argument)
            if not self._assignable(argument_type, param_type):
                raise SemanticError(
                    f"El argumento {position} de '{call.name}' debe ser {param_type} y es {argument_type}", line
                )
        return symbol.return_type

    # ---------- Utilidades ----------

    @staticmethod
    def _assignable(value_type: str, target_type: str) -> bool:
        return value_type == target_type or (value_type == INTEGER and target_type == DECIMAL)

    def _require_assignable(self, value_type: str, target_type: str, target: str, line: int) -> None:
        if not self._assignable(value_type, target_type):
            raise SemanticError(f"No se puede asignar {value_type} a {target} de tipo {target_type}", line)

    @classmethod
    def _contains(cls, statements, node_type) -> bool:
        for statement in statements:
            if isinstance(statement, node_type):
                return True
            if isinstance(statement, IfStatement):
                for block in (statement.then_block, statement.else_block):
                    if block and cls._contains(block.statements, node_type):
                        return True
        return False
