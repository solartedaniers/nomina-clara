import traceback
from typing import Callable, Dict, List, Optional

from .code_generator import TargetCodeGenerator
from .errors import CompilerError
from .ir_generator import IRGenerator
from .lexer import Lexer
from .memory_manager import MemoryManager
from .optimizer import Optimizer
from .parser import Parser
from .symbol_table import SymbolTable
from .type_checker import TypeChecker
from .virtual_machine import VirtualMachine


class PhaseStatus:
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"


PHASES = ["lexer", "parser", "semantic", "ir", "memory", "optimizer", "codegen", "execution"]


class CompilerPipeline:
    """Orquestador · Responsable: Daniers.

    Encadena las fases y arma la respuesta JSON del contrato (sección 4 del documento).
    Si una fase todavía no está implementada (NotImplementedError) queda como "pending"
    y las que dependen de ella como "skipped", para poder probar la página desde el primer día.
    """

    def __init__(self, source: str, employees: List[dict]):
        self.source = source
        self.employees = employees
        self.status: Dict[str, str] = {phase: PhaseStatus.SKIPPED for phase in PHASES}
        self.phases: Dict[str, object] = {}
        self.errors: List[dict] = []
        self.payroll: List[dict] = []

    def _run_phase(self, name: str, action: Callable[[], object]) -> Optional[object]:
        try:
            result = action()
            self.status[name] = PhaseStatus.PASSED
            return result
        except NotImplementedError as pending:
            self.status[name] = PhaseStatus.PENDING
            self.errors.append({"phase": name, "message": str(pending) or "Fase pendiente", "line": 0, "col": 0, "pending": True})
        except CompilerError as error:
            self.status[name] = PhaseStatus.FAILED
            self.errors.append(error.to_dict())
        except Exception as unexpected:
            # Error de programación dentro de una fase: se reporta sin tumbar la API
            self.status[name] = PhaseStatus.FAILED
            self.errors.append({
                "phase": name,
                "message": f"Error interno: {unexpected}",
                "line": 0,
                "col": 0,
                "trace": traceback.format_exc(limit=3),
            })
        return None

    def run(self) -> dict:
        tokens = self._run_phase("lexer", lambda: Lexer(self.source).tokenize())
        if tokens is None:
            return self._response()
        self.phases["tokens"] = [token.to_dict() for token in tokens]

        program = self._run_phase("parser", lambda: Parser(tokens).parse())
        if program is None:
            return self._response()
        self.phases["ast"] = program.to_dict()

        symbol_table = SymbolTable()
        checked = self._run_phase("semantic", lambda: TypeChecker(symbol_table).check(program) or True)
        self.phases["symbols"] = symbol_table.to_list()
        if checked is None:
            return self._response()

        tac = self._run_phase("ir", lambda: IRGenerator().generate(program))
        if tac is None:
            return self._response()
        self.phases["tac"] = {"tac": [i.to_dict() for i in tac], "text": [i.to_text() for i in tac]}

        # Si el optimizador está pendiente, las fases siguientes usan el TAC sin optimizar
        optimization = self._run_phase("optimizer", lambda: Optimizer().optimize(tac))
        final_tac = tac
        if optimization is not None:
            self.phases["optimized"] = optimization.to_dict()
            final_tac = optimization.instructions

        assembly = self._run_phase("codegen", lambda: TargetCodeGenerator().translate(final_tac))
        if assembly is not None:
            self.phases["assembly"] = assembly.to_dict()

        # La fase de memoria (Semana 8) se observa mientras la máquina virtual ejecuta la nómina
        memory = MemoryManager()
        payroll = self._run_phase("execution", lambda: VirtualMachine(memory, self._function_params(program)).run(final_tac, self.employees))
        self.status["memory"] = self.status["execution"]
        self.phases["memory"] = memory.snapshot()
        if payroll is not None:
            self.payroll = payroll

        return self._response()

    @staticmethod
    def _function_params(program) -> Dict[str, List[str]]:
        # La máquina virtual necesita los nombres de los parámetros para cargarlos en el frame de la llamada
        return {function.name: [p.name for p in function.parameters] for function in program.functions}

    def _response(self) -> dict:
        blocking = [e for e in self.errors if not e.get("pending")]
        return {
            "ok": not blocking and all(s == PhaseStatus.PASSED for s in self.status.values()),
            "status": self.status,
            "phases": self.phases,
            "payroll": self.payroll,
            "errors": self.errors,
        }


def compile_source(source: str, employees: List[dict]) -> dict:
    return CompilerPipeline(source, employees).run()
