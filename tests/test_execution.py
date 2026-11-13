import unittest

from compiler.errors import RuntimeFault
from compiler.ir import TacInstruction as I
from compiler.memory_manager import MemoryManager
from compiler.virtual_machine import VirtualMachine

ANA = {"nombre": "Ana Ortiz", "salario": 1750905, "extras": 6}
LUIS = {"nombre": "Luis Mora", "salario": 4200000, "extras": 0}

# TAC de bakery.nc escrito a mano (como lo debe generar la fase 4), para probar sin esperar a Mora
BAKERY_TAC = [
    I("=", "1750905", None, "SMMLV"),
    I("=", "249095", None, "AUXILIO"),
    I("*", "2", "SMMLV", "t1"),
    I("=", "t1", None, "TOPE_AUXILIO"),
    I("begin_func", "horas_extra", "horas,valor_hora"),
    I("=", "1.25", None, "recargo"),
    I("*", "horas", "valor_hora", "t2"),
    I("*", "t2", "recargo", "t3"),
    I("return", "t3"),
    I("end_func", "horas_extra"),
    I("begin_employee"),
    I("/", "salario", "240", "t4"),
    I("=", "t4", None, "valor_hora"),
    I("param", "extras"),
    I("param", "valor_hora"),
    I("call", "horas_extra", "2", "t5"),
    I("+", "salario", "t5", "t6"),
    I("=", "t6", None, "devengado"),
    I("<=", "salario", "TOPE_AUXILIO", "t7"),
    I("ifFalse", "t7", None, "L1"),
    I("+", "devengado", "AUXILIO", "t8"),
    I("=", "t8", None, "devengado"),
    I("label", res="L1"),
    I("*", "salario", "0.04", "t9"),
    I("=", "t9", None, "salud"),
    I("*", "salario", "0.04", "t10"),
    I("=", "t10", None, "pension"),
    I("-", "devengado", "salud", "t11"),
    I("-", "t11", "pension", "t12"),
    I("pay", "t12"),
    I("end_employee"),
]


class VirtualMachineTest(unittest.TestCase):
    def run_bakery(self, employees):
        memory = MemoryManager()
        return VirtualMachine(memory).run(BAKERY_TAC, employees), memory

    def test_payroll_matches_hand_calculation(self):
        # A mano para Ana: valor_hora = 1.750.905 / 240 = 7.295,44; extras = 6 * 7.295,44 * 1,25 = 54.715,78
        # devengado = 1.750.905 + 54.715,78 + 249.095 (auxilio) = 2.054.715,78
        # salud = pension = 1.750.905 * 0,04 = 70.036,2  ->  neto = 1.914.643,38 -> $1.914.643
        payroll, _ = self.run_bakery([ANA, LUIS])
        ana, luis = payroll
        self.assertEqual(ana["name"], "Ana Ortiz")
        self.assertEqual(ana["pay"], 1914643)
        self.assertEqual(ana["values"]["devengado"], 2054716)
        self.assertEqual(ana["values"]["salud"], 70036)
        # Luis gana más de 2 SMMLV: no recibe auxilio ni tiene horas extra -> 4.200.000 * 0,92
        self.assertEqual(luis["pay"], 3864000)
        self.assertNotIn("t5", ana["values"])

    def test_frames_push_and_pop_during_call(self):
        _, memory = self.run_bakery([ANA])
        actions = [(e["action"], e.get("function")) for e in memory.events if e["action"] in ("push", "pop")]
        self.assertEqual(actions, [("push", "empleado#1"), ("push", "horas_extra"), ("pop", "horas_extra"), ("pop", "empleado#1")])
        snapshot = memory.snapshot()
        # El mapa de la sección 3: horas_extra encima de empleado#1 y la lista en el Heap
        self.assertEqual([f["function"] for f in snapshot["stack"]], ["empleado#1", "horas_extra"])
        self.assertEqual(snapshot["stack"][1]["locals"]["recargo"], 1.25)
        self.assertEqual(snapshot["heap"][0]["address"], "0x1000")
        self.assertEqual([d["name"] for d in snapshot["data"]], ["SMMLV", "AUXILIO", "TOPE_AUXILIO"])
        self.assertEqual(memory.events[-1]["action"], "free")

    def test_simulated_stack_overflow(self):
        recursive = [
            I("begin_func", "infinita", "n"),
            I("param", "n"),
            I("call", "infinita", "1", "t1"),
            I("return", "t1"),
            I("end_func", "infinita"),
            I("begin_employee"),
            I("param", "extras"),
            I("call", "infinita", "1", "t2"),
            I("pay", "t2"),
            I("end_employee"),
        ]
        memory = MemoryManager()
        with self.assertRaises(RuntimeFault) as context:
            VirtualMachine(memory).run(recursive, [ANA])
        self.assertIn("Stack Overflow", context.exception.message)
        self.assertEqual(memory.events[-1]["action"], "overflow")

    def test_division_by_zero(self):
        tac = [I("begin_employee"), I("/", "salario", "0", "t1"), I("pay", "t1"), I("end_employee")]
        with self.assertRaises(RuntimeFault):
            VirtualMachine(MemoryManager()).run(tac, [ANA])


if __name__ == "__main__":
    unittest.main()
