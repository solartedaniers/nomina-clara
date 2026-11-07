from typing import Dict, List


class MemoryManager:
    """Fase 5 · Semana 8 · Responsable: Ramírez.

    Basado en GestorMemoria del laboratorio: segmento Data para constantes,
    Stack de frames (uno por empleado y uno por llamada a función) y Heap para la lista de empleados.
    En vez de print(), cada operación se guarda en events para que la página la anime.
    """

    MAX_FRAMES = 64

    def __init__(self):
        self.data: Dict[str, object] = {}
        self.stack: List[dict] = []
        self.heap: Dict[str, dict] = {}
        self.heap_pointer = 0x1000
        self.events: List[dict] = []

    def store_global(self, name: str, value) -> None:
        # TODO (Ramírez): guardar en self.data y registrar el evento {"action": "data", ...}
        raise NotImplementedError("Gestor de memoria pendiente")

    def push_frame(self, function_name: str) -> None:
        # TODO (Ramírez): apilar {"function": nombre, "locals": {}}; si se supera MAX_FRAMES
        # lanzar RuntimeFault("Stack Overflow simulado") y registrar el evento "push"
        raise NotImplementedError("Gestor de memoria pendiente")

    def pop_frame(self) -> None:
        # TODO (Ramírez): desapilar y registrar el evento "pop"
        raise NotImplementedError("Gestor de memoria pendiente")

    def set_local(self, name: str, value) -> None:
        # TODO (Ramírez): asignar en el frame de la cima
        raise NotImplementedError("Gestor de memoria pendiente")

    def get_value(self, name: str):
        # TODO (Ramírez): buscar en el frame de la cima y luego en data
        raise NotImplementedError("Gestor de memoria pendiente")

    def allocate_heap(self, size_bytes: int, description: str, content) -> str:
        # TODO (Ramírez): reservar en heap_pointer (como reservar_heap) y devolver la dirección "0x1000"
        raise NotImplementedError("Gestor de memoria pendiente")

    def free_heap(self, address: str) -> None:
        # TODO (Ramírez): liberar el bloque (como liberar_heap)
        raise NotImplementedError("Gestor de memoria pendiente")

    def snapshot(self) -> dict:
        return {
            "data": [{"name": name, "value": value} for name, value in self.data.items()],
            "stack": [dict(frame) for frame in self.stack],
            "heap": [{"address": address, **block} for address, block in self.heap.items()],
            "events": list(self.events),
        }
