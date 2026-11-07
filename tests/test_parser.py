import unittest

from compiler.ast_nodes import IfStatement, MoneyLiteral, NumberLiteral
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

    @pending_phase
    def test_missing_expression_message_is_clear(self):
        with self.assertRaises(ParserError) as context:
            parse(read_example("syntax_error.nc"))
        error = context.exception
        self.assertEqual((error.line, error.col), (6, 19))
        self.assertIn("Se esperaba una expresión", error.message)
        self.assertIn("'{'", error.message)

    @pending_phase
    def test_literal_values(self):
        program = parse("para cada empleado { pagar $1.750.905 + 1.25 * 240 }")
        pay = program.employee_block.body.statements[0]
        money, product = pay.value.left, pay.value.right
        self.assertIsInstance(money, MoneyLiteral)
        self.assertEqual(money.value, 1750905)
        self.assertIsInstance(money.value, int)
        self.assertIsInstance(product.left, NumberLiteral)
        self.assertEqual((product.left.value, product.left.literal_type), (1.25, "decimal"))
        self.assertIsInstance(product.left.value, float)
        self.assertEqual((product.right.value, product.right.literal_type), (240, "entero"))
        self.assertIsInstance(product.right.value, int)

    @pending_phase
    def test_nodes_keep_their_line(self):
        program = parse(read_example("bakery.nc"))
        self.assertEqual([c.line for c in program.constants], [2, 3, 4])
        self.assertEqual(program.functions[0].line, 6)
        self.assertEqual(program.employee_block.line, 11)
        lines = [s.line for s in program.employee_block.body.statements]
        self.assertEqual(lines, [12, 13, 14, 17, 18, 19])

    @pending_phase
    def test_if_with_else(self):
        program = parse("para cada empleado { si salario > 0 { pagar 1 } sino { pagar 2 } }")
        statement = program.employee_block.body.statements[0]
        self.assertEqual(statement.condition.operator, ">")
        self.assertIsNotNone(statement.else_block)
        self.assertEqual(statement.else_block.statements[0].value.value, 2)


if __name__ == "__main__":
    unittest.main()
