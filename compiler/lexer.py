from typing import List

from .tokens import Token


class Lexer:
    """Fase 1 · Semana 2 · Responsable: Daniers.

    Convierte el texto del programa en una lista de tokens usando TOKEN_SPECS (tokens.py).
    """

    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> List[Token]:
        # TODO (Daniers):
        # 1. Compilar los patrones de TOKEN_SPECS y recorrer el texto de izquierda a derecha,
        #    igual que tokenize() del taller de la semana 3.
        # 2. Llevar la cuenta de línea y columna (NEWLINE suma una línea y reinicia la columna).
        # 3. Descartar COMMENT, NEWLINE y SKIP.
        # 4. Reclasificar IDENTIFIER como KEYWORD si está en KEYWORDS, o como TYPE si está en DATA_TYPES.
        # 5. Si ningún patrón coincide, lanzar LexicalError("Carácter no válido '@'", line, col).
        # 6. Terminar la lista con un Token(TokenType.EOF, "", line, col).
        raise NotImplementedError("Lexer pendiente")
