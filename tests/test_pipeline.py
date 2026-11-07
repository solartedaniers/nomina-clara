import unittest

from compiler import compile_source
from compiler.pipeline import PHASES
from tests.helpers import read_example

EMPLOYEES = [
    {"nombre": "Ana Ortiz", "salario": 1750905, "extras": 6},
    {"nombre": "Luis Mora", "salario": 4200000, "extras": 0},
]


class PipelineContractTest(unittest.TestCase):
    def test_response_follows_contract(self):
        response = compile_source(read_example("bakery.nc"), EMPLOYEES)
        self.assertEqual(set(response.keys()), {"ok", "status", "phases", "payroll", "errors"})
        self.assertEqual(list(response["status"].keys()), PHASES)

    def test_bakery_payroll_when_everything_is_implemented(self):
        response = compile_source(read_example("bakery.nc"), EMPLOYEES)
        if not response["ok"]:
            self.skipTest("Todavía hay fases pendientes")
        self.assertEqual(response["payroll"][0]["pay"], 1914643)


if __name__ == "__main__":
    unittest.main()
