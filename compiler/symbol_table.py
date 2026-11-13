from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .errors import SemanticError


class SymbolKind:
    CONSTANT = "const"
    VARIABLE = "var"
    PARAMETER = "param"
    FUNCTION = "func"


@dataclass
class Symbol:
    """Formato compartido de una entrada de la tabla de símbolos."""

    name: str
    type: str
    scope: str
    address: str
    kind: str
    line: int = 0
    # Solo para funciones: tipos de los parámetros y tipo de retorno (no se envían a la página)
    param_types: List[str] = field(default_factory=list)
    return_type: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "scope": self.scope,
            "address": self.address,
            "kind": self.kind,
            "line": self.line,
        }


@dataclass
class Scope:
    name: str
    symbols: Dict[str, Symbol]
    # Los ámbitos que abren un frame (global, funcion, empleado) llevan su propio contador de bytes;
    # los bloques "si" usan el frame del ámbito que los contiene, como en la sección 3 del documento.
    owns_frame: bool = True
    next_offset: int = 0


WORD_SIZE = 4


class SymbolTable:
    """Fase 3a · Semana 5 · Responsable: Ramírez.

    Pila de ámbitos: global -> funcion / empleado -> bloques si.
    Basada en el laboratorio de la semana 5 (enter_scope, define, lookup, exit_scope),
    pero con una lista como pila y guardando tipo, ámbito y dirección de cada símbolo.
    """

    def __init__(self):
        self.scopes: List[Scope] = []
        # Historial de todos los símbolos declarados, para mostrarlos en la página
        self.history: List[Symbol] = []

    @property
    def current_scope(self) -> Optional[Scope]:
        return self.scopes[-1] if self.scopes else None

    def enter_scope(self, name: str, owns_frame: bool = True) -> None:
        self.scopes.append(Scope(name=name, symbols={}, owns_frame=owns_frame))

    def exit_scope(self) -> None:
        if not self.scopes:
            raise SemanticError("No hay ámbito abierto para cerrar")
        self.scopes.pop()

    def _frame_scope(self) -> Scope:
        for scope in reversed(self.scopes):
            if scope.owns_frame:
                return scope
        return self.scopes[0]

    def _next_address(self, kind: str) -> str:
        if kind == SymbolKind.FUNCTION:
            return "text"
        frame = self._frame_scope()
        offset = frame.next_offset
        frame.next_offset += WORD_SIZE
        prefix = "data" if frame is self.scopes[0] else "frame"
        return f"{prefix}+{offset}"

    def declare(self, name: str, symbol_type: str, kind: str, line: int = 0,
                param_types: Optional[List[str]] = None, return_type: Optional[str] = None) -> Symbol:
        scope = self.current_scope
        if scope is None:
            raise SemanticError(f"No hay ámbito abierto para declarar '{name}'", line)
        if name in scope.symbols:
            previous = scope.symbols[name]
            raise SemanticError(
                f"'{name}' ya fue declarado en el ámbito '{scope.name}' (línea {previous.line})", line
            )
        symbol = Symbol(
            name=name, type=symbol_type, scope=scope.name, address=self._next_address(kind),
            kind=kind, line=line, param_types=list(param_types or []), return_type=return_type,
        )
        scope.symbols[name] = symbol
        self.history.append(symbol)
        return symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope.symbols:
                return scope.symbols[name]
        return None

    def to_list(self) -> List[dict]:
        return [symbol.to_dict() for symbol in self.history]
