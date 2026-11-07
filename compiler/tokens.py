from dataclasses import dataclass


class TokenType:
    KEYWORD = "KEYWORD"
    TYPE = "TYPE"
    MONEY = "MONEY"
    DECIMAL = "DECIMAL"
    INTEGER = "INTEGER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    REL_OP = "REL_OP"
    ARITH_OP = "ARITH_OP"
    ASSIGN = "ASSIGN"
    COLON = "COLON"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    EOF = "EOF"


# Palabras reservadas del lenguaje Nómina Clara (el lenguaje que compilamos es en español)
KEYWORDS = {"constante", "funcion", "para", "cada", "empleado", "si", "sino", "retornar", "pagar"}

# Tipos de datos del lenguaje
DATA_TYPES = {"entero", "decimal", "dinero", "texto", "logico"}

# Patrones regex (Semana 2). El orden importa: MONEY antes que DECIMAL e INTEGER,
# y los operadores de dos caracteres (<=, >=, ==, !=) antes que los de uno.
# Las palabras clave y los tipos se reconocen como IDENTIFIER y luego se reclasifican.
TOKEN_SPECS = [
    ("COMMENT", r"#[^\n]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r]+"),
    # Dinero con puntos de miles ($1.750.905) o sin puntos ($1750905). El lookahead final
    # impide aceptar solo una parte de algo mal formado como $1.7509.
    (TokenType.MONEY, r"\$(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?![0-9.])"),
    (TokenType.DECIMAL, r"[0-9]+\.[0-9]+"),
    (TokenType.INTEGER, r"[0-9]+"),
    (TokenType.STRING, r"\"[^\"\n]*\""),
    (TokenType.IDENTIFIER, r"[a-zA-Z_][a-zA-Z0-9_]*"),
    (TokenType.REL_OP, r"<=|>=|==|!=|<|>"),
    (TokenType.ARITH_OP, r"[+\-*/]"),
    (TokenType.ASSIGN, r"="),
    (TokenType.COLON, r":"),
    (TokenType.COMMA, r","),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
    (TokenType.LBRACE, r"\{"),
    (TokenType.RBRACE, r"\}"),
]


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    col: int

    def to_dict(self) -> dict:
        return {"type": self.type, "value": self.value, "line": self.line, "col": self.col}

    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}', {self.line}:{self.col})"
