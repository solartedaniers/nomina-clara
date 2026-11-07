import functools
import os

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples")


def read_example(name: str) -> str:
    with open(os.path.join(EXAMPLES_DIR, name), encoding="utf-8") as file:
        return file.read()


def pending_phase(test):
    # Si la fase aún lanza NotImplementedError, la prueba se marca como "skipped" en vez de fallar
    @functools.wraps(test)
    def wrapper(self, *args, **kwargs):
        try:
            return test(self, *args, **kwargs)
        except NotImplementedError as pending:
            self.skipTest(f"Fase pendiente: {pending}")

    return wrapper
