import unittest

from compiler.ast_nodes import (
    Assignment,
    BinaryOperation,
    Block,
    Comparison,
    EmployeeBlock,
    Identifier,
    IfStatement,
    Program,
)
from compiler.code_generator import TargetCodeGenerator
from compiler.ir import TacInstruction, TacOp
from compiler.ir_generator import IRGenerator
from compiler.optimizer import Optimizer
from tests.helpers import pending_phase


class TargetCodeGeneratorTest(unittest.TestCase):
    def test_professor_example(self):
        result = TargetCodeGenerator().translate([TacInstruction("+", "a", "b", "t1")])
        self.assertEqual(result.lines, ["MOV [R0], [a]", "ADD [R0], [b]"])

    def test_spill_when_registers_are_full(self):
        tac = [
            TacInstruction("-", "salario", "salud", "t1"),
            TacInstruction("*", "t1", "2", "t2"),
            TacInstruction("+", "pension", "salud", "t3"),
            TacInstruction("*", "t3", "3", "t4"),
        ]
        result = TargetCodeGenerator().translate(tac)
        self.assertEqual(result.spills[0], {"variable": "t1", "register": "R0", "address": "0x2000"})


class IRGeneratorTest(unittest.TestCase):
    @pending_phase
    def test_if_statement_produces_jump_and_label(self):
        rule = IfStatement(
            condition=Comparison(operator="<=", left=Identifier(name="salario"), right=Identifier(name="TOPE_AUXILIO")),
            then_block=Block(statements=[
                Assignment(
                    name="devengado",
                    value=BinaryOperation(operator="+", left=Identifier(name="devengado"), right=Identifier(name="AUXILIO")),
                )
            ]),
        )
        program = Program(employee_block=EmployeeBlock(body=Block(statements=[rule])))
        text = [i.to_text() for i in IRGenerator().generate(program)]
        self.assertIn("t1 = salario <= TOPE_AUXILIO", text)
        self.assertIn("ifFalse t1 goto L1", text)
        self.assertIn("L1:", text)


class OptimizerTest(unittest.TestCase):
    @pending_phase
    def test_constant_folding(self):
        tac = [TacInstruction(TacOp.MUL, "2", "1750905", "t1"), TacInstruction(TacOp.ASSIGN, "t1", None, "TOPE_AUXILIO")]
        result = Optimizer().optimize(tac)
        self.assertIn("TOPE_AUXILIO = 3501810", [i.to_text() for i in result.instructions])
        self.assertLess(len(result.instructions), len(tac))


if __name__ == "__main__":
    unittest.main()
