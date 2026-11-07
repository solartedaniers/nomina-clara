class CompilerPhase:
    LEXICAL = "lexical"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    RUNTIME = "runtime"


class CompilerError(Exception):
    """Error base del compilador: guarda la fase donde falló y la posición en el código."""

    phase = CompilerPhase.RUNTIME

    def __init__(self, message: str, line: int = 0, col: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col

    def to_dict(self) -> dict:
        return {"phase": self.phase, "message": self.message, "line": self.line, "col": self.col}


class LexicalError(CompilerError):
    phase = CompilerPhase.LEXICAL


class ParserError(CompilerError):
    # No se llama SyntaxError para no tapar la excepción nativa de Python
    phase = CompilerPhase.SYNTAX


class SemanticError(CompilerError):
    phase = CompilerPhase.SEMANTIC


class RuntimeFault(CompilerError):
    phase = CompilerPhase.RUNTIME
