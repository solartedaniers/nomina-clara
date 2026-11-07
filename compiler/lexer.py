import re
from typing import List

from .errors import LexicalError
from .tokens import DATA_TYPES, KEYWORDS, TOKEN_SPECS, Token, TokenType

# Un solo regex con un grupo con nombre por patrón. Python prueba las alternativas en
# orden, así que se respeta la prioridad de TOKEN_SPECS (MONEY antes que DECIMAL, <= antes que <).
MASTER_PATTERN = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECS))

IGNORED = {"COMMENT", "NEWLINE", "SKIP"}

# Solo para el mensaje de error: toma el $ y los dígitos y puntos que lo siguen
MALFORMED_MONEY = re.compile(r"\$[0-9.]*")


class Lexer:
    """Fase 1 · Semana 2 · Responsable: Daniers.

    Convierte el texto del programa en una lista de tokens usando TOKEN_SPECS (tokens.py).
    """

    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        pos = 0
        line = 1
        line_start = 0  # posición donde empieza la línea actual, para calcular la columna

        while pos < len(self.source):
            match = MASTER_PATTERN.match(self.source, pos)
            col = pos - line_start + 1

            if match is None:
                char = self.source[pos]
                if char == "$":
                    # Un $ que no forma MONEY es un valor de dinero mal escrito, como $1.7509
                    amount = MALFORMED_MONEY.match(self.source, pos).group()
                    raise LexicalError(f"Valor de dinero mal formado '{amount}'", line, col)
                raise LexicalError(f"Carácter no válido '{char}'", line, col)

            kind = match.lastgroup
            value = match.group()

            if kind == "NEWLINE":
                line += 1
                line_start = match.end()
            elif kind not in IGNORED:
                if kind == TokenType.IDENTIFIER and value in KEYWORDS:
                    kind = TokenType.KEYWORD
                elif kind == TokenType.IDENTIFIER and value in DATA_TYPES:
                    kind = TokenType.TYPE
                tokens.append(Token(kind, value, line, col))

            pos = match.end()

        tokens.append(Token(TokenType.EOF, "", line, pos - line_start + 1))
        return tokens
