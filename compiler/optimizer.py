from dataclasses import dataclass, field
from typing import List

from .ir import TacInstruction


@dataclass
class OptimizationResult:
    instructions: List[TacInstruction]
    original_count: int
    steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tac": [i.to_dict() for i in self.instructions],
            "text": [i.to_text() for i in self.instructions],
            "originalCount": self.original_count,
            "optimizedCount": len(self.instructions),
            "removed": self.original_count - len(self.instructions),
            "steps": self.steps,
        }


class Optimizer:
    """Fase 6 · Semana 9 · Responsable: Mora.

    Pasadas sobre el TAC:
    1. Plegado de constantes: t1 = 2 * 1750905  ->  t1 = 3501810
    2. Propagación de constantes: reemplazar TOPE_AUXILIO y AUXILIO por su valor
    3. Eliminación de copias: t2 = a + b ; x = t2  ->  x = a + b
    Cada cambio se describe en steps para mostrarlo en la página.
    """

    def optimize(self, instructions: List[TacInstruction]) -> OptimizationResult:
        # TODO (Mora): no modificar la lista original; trabajar sobre una copia
        raise NotImplementedError("Optimizador pendiente")
