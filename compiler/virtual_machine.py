from typing import List

from .ir import TacInstruction
from .memory_manager import MemoryManager


class VirtualMachine:
    """Ejecución · Semanas 4 y 8 · Responsable: Ramírez.

    Recorre el TAC optimizado por cada empleado y calcula el valor a pagar.
    """

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def run(self, instructions: List[TacInstruction], employees: List[dict]) -> List[dict]:
        # TODO (Ramírez):
        # 1. Guardar la lista de empleados en el heap (allocate_heap) y las constantes en data.
        # 2. Ubicar las etiquetas (label) para poder saltar con goto / ifFalse.
        # 3. Por cada empleado: push_frame("empleado#N"), cargar nombre, salario y extras,
        #    ejecutar desde begin_employee hasta end_employee y pop_frame().
        # 4. En "call": push_frame(funcion), pasar los param, ejecutar hasta return y pop_frame().
        # 5. Devolver por empleado: {"name": ..., "values": {variables del frame}, "pay": valor de pagar}.
        # 6. Redondear el dinero a pesos enteros al final.
        raise NotImplementedError("Máquina virtual pendiente")
