import unittest

from compiler.ast_nodes import IfStatement
from compiler.errors import ParserError
from compiler.lexer import Lexer
from compiler.parser import Parser
from tests.helpers import pending_phase, read_example


def parse(source: str):
    return Parser(Lexer(source).tokenize()).parse()


class ParserTest(unittest.TestCase):
    @pending_phase
    def test_builds_program_from_bakery_example(self):
        program = parse(read_example("bakery.nc"))
        self.assertEqual([c.name for c in program.constants], ["SMMLV", "AUXILIO", "TOPE_AUXILIO"])
        self.assertEqual(program.functions[0].name, "horas_extra")
        self.assertIsNotNone(program.employee_block)

    @pending_phase
    def test_evaluates_constants(self):
        program = parse(read_example("bakery.nc"))
        self.assertEqual(program.constants[2].evaluated_value, 3501810)

    @pending_phase
    def test_respects_precedence(self):
        program = parse("para cada empleado { pagar salario + salario * 2 }")
        pay = program.employee_block.body.statements[0]
        self.assertEqual(pay.value.operator, "+")
        self.assertEqual(pay.value.right.operator, "*")

    @pending_phase
    def test_if_statement_node(self):
        program = parse(read_example("bakery.nc"))
        statements = program.employee_block.body.statements
        self.assertTrue(any(isinstance(s, IfStatement) for s in statements))

    @pending_phase
    def test_reports_missing_expression(self):
        with self.assertRaises(ParserError) as context:
            parse(read_example("syntax_error.nc"))
        self.assertEqual(context.exception.line, 6)


if __name__ == "__main__":
    unittest.main()
