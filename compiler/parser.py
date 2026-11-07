from typing import Dict, List, Optional

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
    Parameter,
    PayStatement,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
)
from .errors import ParserError
from .tokens import Token, TokenType

# Nombres legibles de los tokens para los mensajes de error
READABLE_TOKENS = {
    TokenType.IDENTIFIER: "un nombre",
    TokenType.TYPE: "un tipo de dato",
    TokenType.REL_OP: "un operador de comparación",
    TokenType.ASSIGN: "'='",
    TokenType.COLON: "':'",
    TokenType.COMMA: "','",
    TokenType.LPAREN: "'('",
    TokenType.RPAREN: "')'",
    TokenType.LBRACE: "'{'",
    TokenType.RBRACE: "'}'",
    TokenType.EOF: "el fin del programa",
}


class Parser:
    """Fase 2 · Semanas 3 y 4 · Responsable: Daniers.

    Parser descendente recursivo: un método por cada regla de la gramática EBNF.

    programa        -> { declaracion } bloque_empleado
    declaracion     -> constante | funcion
    constante       -> "constante" ID ":" TIPO "=" expr
    funcion         -> "funcion" ID "(" [ param { "," param } ] ")" ":" TIPO bloque
    param           -> ID ":" TIPO
    bloque_empleado -> "para" "cada" "empleado" bloque
    bloque          -> "{" { sentencia } "}"
    sentencia       -> declaracion_var | asignacion | si | retornar | pagar
    declaracion_var -> ID ":" TIPO "=" expr
    asignacion      -> ID "=" expr
    si              -> "si" comparacion bloque [ "sino" bloque ]
    retornar        -> "retornar" expr
    pagar           -> "pagar" expr
    comparacion     -> expr OP_REL expr
    expr            -> term { ("+" | "-") term }
    term            -> factor { ("*" | "/") factor }
    factor          -> DINERO | DECIMAL | ENTERO | TEXTO | llamada | ID | "(" expr ")"
    llamada         -> ID "(" [ expr { "," expr } ] ")"
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current(self) -> Optional[Token]:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def peek(self, offset: int = 1) -> Optional[Token]:
        index = self.position + offset
        return self.tokens[index] if index < len(self.tokens) else None

    def check(self, token_type: str, value: Optional[str] = None) -> bool:
        token = self.current()
        return token is not None and token.type == token_type and (value is None or token.value == value)

    def eat(self, token_type: str, value: Optional[str] = None) -> Token:
        # Igual que eat() del taller: consume el token esperado o lanza error sintáctico
        token = self.current()
        if self.check(token_type, value):
            self.position += 1
            return token
        expected = f"'{value}'" if value else READABLE_TOKENS.get(token_type, token_type)
        raise self.error(f"Se esperaba {expected}")

    def error(self, message: str) -> ParserError:
        # Arma el ParserError con lo que se encontró y la posición del token actual
        token = self.current()
        found = f"'{token.value}'" if token and token.value else "el fin del programa"
        line = token.line if token else 0
        col = token.col if token else 0
        return ParserError(f"{message} pero se encontró {found}", line, col)

    def parse(self) -> Program:
        start = self.current()
        program = Program(line=start.line if start else 0)

        while self.check(TokenType.KEYWORD, "constante") or self.check(TokenType.KEYWORD, "funcion"):
            if self.check(TokenType.KEYWORD, "constante"):
                program.constants.append(self.parse_constant())
            else:
                program.functions.append(self.parse_function())

        program.employee_block = self.parse_employee_block()
        self.eat(TokenType.EOF)

        self.evaluate_constants(program.constants)
        return program

    # ---------- Declaraciones ----------

    def parse_constant(self) -> ConstantDeclaration:
        keyword = self.eat(TokenType.KEYWORD, "constante")
        name = self.eat(TokenType.IDENTIFIER).value
        self.eat(TokenType.COLON)
        declared_type = self.eat(TokenType.TYPE).value
        self.eat(TokenType.ASSIGN)
        value = self.parse_expression()
        return ConstantDeclaration(line=keyword.line, name=name, declared_type=declared_type, value=value)

    def parse_function(self) -> FunctionDeclaration:
        keyword = self.eat(TokenType.KEYWORD, "funcion")
        name = self.eat(TokenType.IDENTIFIER).value
        self.eat(TokenType.LPAREN)
        parameters: List[Parameter] = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.check(TokenType.COMMA):
                self.eat(TokenType.COMMA)
                parameters.append(self.parse_parameter())
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        return_type = self.eat(TokenType.TYPE).value
        body = self.parse_block()
        return FunctionDeclaration(line=keyword.line, name=name, parameters=parameters, return_type=return_type, body=body)

    def parse_parameter(self) -> Parameter:
        name = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.COLON)
        declared_type = self.eat(TokenType.TYPE).value
        return Parameter(line=name.line, name=name.value, declared_type=declared_type)

    def parse_employee_block(self) -> EmployeeBlock:
        keyword = self.eat(TokenType.KEYWORD, "para")
        self.eat(TokenType.KEYWORD, "cada")
        self.eat(TokenType.KEYWORD, "empleado")
        return EmployeeBlock(line=keyword.line, body=self.parse_block())

    # ---------- Bloques y sentencias ----------

    def parse_block(self) -> Block:
        brace = self.eat(TokenType.LBRACE)
        block = Block(line=brace.line)
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            block.statements.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        return block

    def parse_statement(self) -> Statement:
        if self.check(TokenType.KEYWORD, "si"):
            return self.parse_if()
        if self.check(TokenType.KEYWORD, "retornar"):
            keyword = self.eat(TokenType.KEYWORD, "retornar")
            return ReturnStatement(line=keyword.line, value=self.parse_expression())
        if self.check(TokenType.KEYWORD, "pagar"):
            keyword = self.eat(TokenType.KEYWORD, "pagar")
            return PayStatement(line=keyword.line, value=self.parse_expression())
        if self.check(TokenType.IDENTIFIER):
            # Con un token de anticipación se distingue "x: tipo = ..." de "x = ..."
            following = self.peek()
            if following and following.type == TokenType.COLON:
                return self.parse_variable_declaration()
            if following and following.type == TokenType.ASSIGN:
                return self.parse_assignment()
            self.position += 1
            raise self.error("Se esperaba ':' o '=' después del nombre")
        raise self.error("Se esperaba una sentencia (declaración, asignación, si, retornar o pagar)")

    def parse_variable_declaration(self) -> VariableDeclaration:
        name = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.COLON)
        declared_type = self.eat(TokenType.TYPE).value
        self.eat(TokenType.ASSIGN)
        value = self.parse_expression()
        return VariableDeclaration(line=name.line, name=name.value, declared_type=declared_type, value=value)

    def parse_assignment(self) -> Assignment:
        name = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        return Assignment(line=name.line, name=name.value, value=self.parse_expression())

    def parse_if(self) -> IfStatement:
        keyword = self.eat(TokenType.KEYWORD, "si")
        condition = self.parse_comparison()
        then_block = self.parse_block()
        else_block = None
        if self.check(TokenType.KEYWORD, "sino"):
            self.eat(TokenType.KEYWORD, "sino")
            else_block = self.parse_block()
        return IfStatement(line=keyword.line, condition=condition, then_block=then_block, else_block=else_block)

    # ---------- Expresiones ----------

    def parse_comparison(self) -> Comparison:
        left = self.parse_expression()
        operator = self.eat(TokenType.REL_OP)
        right = self.parse_expression()
        return Comparison(line=operator.line, operator=operator.value, left=left, right=right)

    def parse_expression(self) -> Expression:
        # Un ciclo por nivel hace que + y - sean asociativos a la izquierda
        node = self.parse_term()
        while self.check(TokenType.ARITH_OP, "+") or self.check(TokenType.ARITH_OP, "-"):
            operator = self.eat(TokenType.ARITH_OP)
            node = BinaryOperation(line=operator.line, operator=operator.value, left=node, right=self.parse_term())
        return node

    def parse_term(self) -> Expression:
        # * y / se resuelven aquí, un nivel más abajo, por eso tienen más precedencia que + y -
        node = self.parse_factor()
        while self.check(TokenType.ARITH_OP, "*") or self.check(TokenType.ARITH_OP, "/"):
            operator = self.eat(TokenType.ARITH_OP)
            node = BinaryOperation(line=operator.line, operator=operator.value, left=node, right=self.parse_factor())
        return node

    def parse_factor(self) -> Expression:
        token = self.current()
        if self.check(TokenType.MONEY):
            self.position += 1
            # $1.750.905 -> 1750905: se quitan el $ y los puntos de miles
            return MoneyLiteral(line=token.line, value=int(token.value[1:].replace(".", "")))
        if self.check(TokenType.DECIMAL):
            self.position += 1
            return NumberLiteral(line=token.line, value=float(token.value), literal_type="decimal")
        if self.check(TokenType.INTEGER):
            self.position += 1
            return NumberLiteral(line=token.line, value=int(token.value), literal_type="entero")
        if self.check(TokenType.STRING):
            self.position += 1
            return StringLiteral(line=token.line, value=token.value[1:-1])
        if self.check(TokenType.IDENTIFIER):
            following = self.peek()
            if following and following.type == TokenType.LPAREN:
                return self.parse_call()
            self.position += 1
            return Identifier(line=token.line, name=token.value)
        if self.check(TokenType.LPAREN):
            self.eat(TokenType.LPAREN)
            node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return node
        raise self.error("Se esperaba una expresión (un número, dinero, texto, nombre o paréntesis)")

    def parse_call(self) -> FunctionCall:
        name = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        arguments: List[Expression] = []
        if not self.check(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.check(TokenType.COMMA):
                self.eat(TokenType.COMMA)
                arguments.append(self.parse_expression())
        self.eat(TokenType.RPAREN)
        return FunctionCall(line=name.line, name=name.value, arguments=arguments)

    # ---------- Evaluación de constantes (Semana 4) ----------

    def evaluate_constants(self, constants: List[ConstantDeclaration]) -> None:
        # Cada constante puede usar las anteriores, por eso se evalúan en orden
        values: Dict[str, float] = {}
        for constant in constants:
            constant.evaluated_value = evaluate(constant.value, values)
            if constant.evaluated_value is not None:
                values[constant.name] = constant.evaluated_value


def evaluate(node: Optional[Expression], values: Dict[str, float]) -> Optional[float]:
    # Recorre el AST en postorden. Devuelve None si la expresión no se puede calcular
    # aquí (texto, llamadas, nombres que no son constantes o división entre cero);
    # esos casos los reporta el análisis semántico.
    if isinstance(node, (MoneyLiteral, NumberLiteral)):
        return node.value
    if isinstance(node, Identifier):
        return values.get(node.name)
    if isinstance(node, BinaryOperation):
        left = evaluate(node.left, values)
        right = evaluate(node.right, values)
        if left is None or right is None:
            return None
        if node.operator == "+":
            return left + right
        if node.operator == "-":
            return left - right
        if node.operator == "*":
            return left * right
        if node.operator == "/" and right != 0:
            return left / right
    return None
