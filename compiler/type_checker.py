from .ast_nodes import Program
from .symbol_table import SymbolTable


class TypeChecker:
    """Fase 3b · Semana 6 · Responsable: Ramírez.

    Recorre el AST, llena la tabla de símbolos con los ámbitos y valida los tipos.

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

    def check(self, program: Program) -> None:
        # TODO (Ramírez):
        # 1. enter_scope("global"): declarar constantes y funciones.
        # 2. Por cada función: enter_scope(nombre), declarar parámetros, revisar el cuerpo, exit_scope().
        # 3. enter_scope("empleado"): declarar EMPLOYEE_FIELDS (ast_nodes.py) y revisar el bloque.
        # 4. Cada "si" abre su propio ámbito.
        # 5. Guardar el tipo calculado en expression.inferred_type y lanzar SemanticError con línea si algo no cuadra.
        raise NotImplementedError("Verificador de tipos pendiente")
