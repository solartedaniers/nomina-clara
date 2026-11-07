from typing import List, Optional

from .ast_nodes import Program
from .errors import ParserError
from .tokens import Token, TokenType


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
        expected = value or token_type
        found = token.value if token and token.value else "fin del programa"
        line = token.line if token else 0
        col = token.col if token else 0
        raise ParserError(f"Se esperaba '{expected}' pero se encontró '{found}'", line, col)

    def parse(self) -> Program:
        # TODO (Daniers): implementar un método por regla (parse_constant, parse_function,
        # parse_employee_block, parse_block, parse_statement, parse_if, parse_comparison,
        # parse_expression, parse_term, parse_factor, parse_call) y armar el Program.
        # Al final, evaluar el AST de cada constante y guardar el resultado en evaluated_value (Semana 4).
        raise NotImplementedError("Parser pendiente")
