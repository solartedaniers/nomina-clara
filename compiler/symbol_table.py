from dataclasses import dataclass
from typing import Dict, List, Optional


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


class SymbolTable:
    """Fase 3a · Semana 5 · Responsable: Ramírez.

    Pila de ámbitos: global -> funcion / empleado -> bloques si.
    """

    def __init__(self):
        self.scopes: List[Scope] = []
        # Historial de todos los símbolos declarados, para mostrarlos en la página
        self.history: List[Symbol] = []

    def enter_scope(self, name: str) -> None:
        # TODO (Ramírez): apilar un nuevo Scope
        raise NotImplementedError("Tabla de símbolos pendiente")

    def exit_scope(self) -> None:
        # TODO (Ramírez): desapilar el Scope actual
        raise NotImplementedError("Tabla de símbolos pendiente")

    def declare(self, name: str, symbol_type: str, kind: str, line: int = 0) -> Symbol:
        # TODO (Ramírez): lanzar SemanticError si el nombre ya existe en el ámbito actual,
        # calcular la dirección (data+N para globales, frame+N para locales) y guardarlo en history
        raise NotImplementedError("Tabla de símbolos pendiente")

    def lookup(self, name: str) -> Optional[Symbol]:
        # TODO (Ramírez): buscar desde la cima de la pila hasta el ámbito global
        raise NotImplementedError("Tabla de símbolos pendiente")

    def to_list(self) -> List[dict]:
        return [symbol.to_dict() for symbol in self.history]
