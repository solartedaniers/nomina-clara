import copy
from typing import Dict, List, Optional

from .errors import RuntimeFault


class MemoryManager:
    """Fase 5 · Semana 8 · Responsable: Ramírez.

    Basado en GestorMemoria del laboratorio: segmento Data para constantes,
    Stack de frames (uno por empleado y uno por llamada a función) y Heap para la lista de empleados.
    En vez de print(), cada operación se guarda en events para que la página la anime.

    Equivalencias con el laboratorio:
        push_stack_frame -> push_frame      pop_stack_frame -> pop_frame
        asignar_local    -> set_local       reservar_heap   -> allocate_heap
        liberar_heap     -> free_heap
    """

    MAX_FRAMES = 64

    def __init__(self):
        self.data: Dict[str, object] = {}
        self.stack: List[dict] = []
        self.heap: Dict[str, dict] = {}
        self.heap_pointer = 0x1000
        self.events: List[dict] = []
        # Foto de la memoria en el momento de mayor profundidad de la pila
        # (p. ej. frame horas_extra encima de empleado#1 con la lista en el Heap): es el mapa de la sección 3
        self._peak: Optional[dict] = None
        self._peak_depth = 0

    # ---------- Eventos ----------

    def _event(self, action: str, **details) -> None:
        event = {"step": len(self.events) + 1, "action": action, **details}
        event["stack"] = [frame["function"] for frame in self.stack]
        event["heap"] = list(self.heap.keys())
        self.events.append(event)

    # ---------- Data ----------

    def store_global(self, name: str, value) -> None:
        self.data[name] = value
        self._event("data", name=name, value=value)

    # ---------- Stack ----------

    def push_frame(self, function_name: str) -> None:
        if len(self.stack) >= self.MAX_FRAMES:
            self._event("overflow", function=function_name, limit=self.MAX_FRAMES)
            raise RuntimeFault(
                f"Stack Overflow simulado: se superó el límite de {self.MAX_FRAMES} frames al llamar a '{function_name}'"
            )
        self.stack.append({"function": function_name, "locals": {}})
        self._event("push", function=function_name)
        if len(self.stack) > self._peak_depth:
            self._peak_depth = len(self.stack)
            self._peak = {"stack": copy.deepcopy(self.stack), "heap": copy.deepcopy(self.heap)}

    def pop_frame(self) -> dict:
        if not self.stack:
            raise RuntimeFault("No hay frames en la pila para desapilar")
        # Antes de destruir el frame se actualiza la foto si este es el frame más profundo
        if len(self.stack) == self._peak_depth and self._peak and self._peak["stack"][-1]["function"] == self.stack[-1]["function"]:
            self._peak["stack"][-1] = copy.deepcopy(self.stack[-1])
        frame = self.stack.pop()
        self._event("pop", function=frame["function"], locals=dict(frame["locals"]))
        return frame

    def set_local(self, name: str, value) -> None:
        if not self.stack:
            raise RuntimeFault(f"No hay frame activo para guardar '{name}'")
        self.stack[-1]["locals"][name] = value

    def get_value(self, name: str):
        if self.stack and name in self.stack[-1]["locals"]:
            return self.stack[-1]["locals"][name]
        if name in self.data:
            return self.data[name]
        raise RuntimeFault(f"La variable '{name}' no tiene valor en memoria")

    # ---------- Heap ----------

    def allocate_heap(self, size_bytes: int, description: str, content) -> str:
        address = f"0x{self.heap_pointer:X}"
        self.heap[address] = {"size": size_bytes, "description": description, "content": content}
        self.heap_pointer += size_bytes
        self._event("alloc", address=address, size=size_bytes, description=description)
        return address

    def free_heap(self, address: str) -> None:
        if address not in self.heap:
            raise RuntimeFault(f"No hay un bloque reservado en {address}")
        block = self.heap.pop(address)
        self._event("free", address=address, description=block["description"])

    # ---------- Salida para la página ----------

    def snapshot(self) -> dict:
        # Data es el estado final; Stack y Heap salen de la foto de mayor profundidad,
        # porque al terminar la liquidación la pila queda vacía y el Heap liberado.
        stack = self._peak["stack"] if self._peak else self.stack
        heap = self._peak["heap"] if self._peak else self.heap
        return {
            "data": [{"name": name, "value": value} for name, value in self.data.items()],
            "stack": [copy.deepcopy(frame) for frame in stack],
            "heap": [{"address": address, **block} for address, block in heap.items()],
            "events": list(self.events),
        }
