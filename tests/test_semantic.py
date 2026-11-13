import unittest

from compiler.ast_nodes import (
    Assignment,
    BinaryOperation,
    Block,
    EmployeeBlock,
    Identifier,
    PayStatement,
    Program,
    VariableDeclaration,
)
from compiler.errors import SemanticError
from compiler.symbol_table import SymbolKind, SymbolTable
from compiler.type_checker import TypeChecker
from compiler.lexer import Lexer
from compiler.parser import Parser
from tests.helpers import pending_phase, read_example


def check_source(source: str) -> SymbolTable:
    table = SymbolTable()
    TypeChecker(table).check(Parser(Lexer(source).tokenize()).parse())
    return table


FUNCTION = """
constante SMMLV: dinero = $1.750.905
funcion horas_extra(horas: entero, valor_hora: dinero): dinero {
    recargo: decimal = 1.25
    retornar horas * valor_hora * recargo
}
"""


def employee_program(*statements) -> Program:
    # AST escrito a mano: permite probar la fase 3 sin esperar al parser
    return Program(employee_block=EmployeeBlock(body=Block(statements=list(statements))))


class SymbolTableTest(unittest.TestCase):
    @pending_phase
    def test_lookup_goes_from_inner_to_global(self):
        table = SymbolTable()
        table.enter_scope("global")
        table.declare("SMMLV", "dinero", SymbolKind.CONSTANT)
        table.enter_scope("empleado")
        table.declare("devengado", "dinero", SymbolKind.VARIABLE)
        self.assertEqual(table.lookup("SMMLV").scope, "global")
        self.assertEqual(table.lookup("devengado").scope, "empleado")
        table.exit_scope()
        self.assertIsNone(table.lookup("devengado"))

    @pending_phase
    def test_rejects_duplicate_in_same_scope(self):
        table = SymbolTable()
        table.enter_scope("global")
        table.declare("SMMLV", "dinero", SymbolKind.CONSTANT)
        with self.assertRaises(SemanticError):
            table.declare("SMMLV", "dinero", SymbolKind.CONSTANT)


class TypeCheckerTest(unittest.TestCase):
    @pending_phase
    def test_money_plus_text_is_rejected(self):
        program = employee_program(
            VariableDeclaration(line=2, name="devengado", declared_type="dinero", value=Identifier(name="salario")),
            Assignment(
                line=3,
                name="devengado",
                value=BinaryOperation(operator="+", left=Identifier(name="devengado"), right=Identifier(name="nombre")),
            ),
            PayStatement(line=4, value=Identifier(name="devengado")),
        )
        with self.assertRaises(SemanticError) as context:
            TypeChecker(SymbolTable()).check(program)
        self.assertEqual(context.exception.line, 3)

    @pending_phase
    def test_undeclared_variable_is_rejected(self):
        program = employee_program(PayStatement(line=1, value=Identifier(name="bono")))
        with self.assertRaises(SemanticError):
            TypeChecker(SymbolTable()).check(program)


class SemanticRulesTest(unittest.TestCase):
    def assert_semantic_error(self, body: str, fragment: str):
        with self.assertRaises(SemanticError) as context:
            check_source(FUNCTION + "para cada empleado {\n" + body + "\n}")
        self.assertIn(fragment, context.exception.message)
        self.assertGreater(context.exception.line, 0)

    @pending_phase
    def test_bakery_is_valid_and_addresses_match_document(self):
        table = check_source(read_example("bakery.nc"))
        rows = {(s.name, s.scope): s for s in table.history}
        self.assertEqual(rows[("TOPE_AUXILIO", "global")].address, "data+8")
        self.assertEqual(rows[("horas_extra", "global")].type, "funcion(entero, dinero): dinero")
        self.assertEqual(rows[("recargo", "horas_extra")].address, "frame+8")
        self.assertEqual(rows[("valor_hora", "empleado")].address, "frame+12")
        # valor_hora existe en dos ámbitos distintos sin chocar
        self.assertIn(("valor_hora", "horas_extra"), rows)

    @pending_phase
    def test_undeclared_variable(self):
        self.assert_semantic_error("devengado: dinero = salario\ndevengado = devengado + bono\npagar devengado", "bono")

    @pending_phase
    def test_variable_out_of_scope(self):
        self.assert_semantic_error("pagar salario * recargo", "recargo")

    @pending_phase
    def test_if_scope_is_closed(self):
        self.assert_semantic_error("si salario <= SMMLV {\n bono: dinero = SMMLV\n}\npagar bono", "bono")

    @pending_phase
    def test_money_plus_text(self):
        self.assert_semantic_error("pagar salario + nombre", "No se puede sumar dinero con texto")

    @pending_phase
    def test_money_times_money_and_number_divided_by_money(self):
        self.assert_semantic_error("pagar salario * salario", "multiplicar dinero con dinero")
        self.assert_semantic_error("x: dinero = 240 / salario\npagar x", "dividir entero con dinero")

    @pending_phase
    def test_too_few_and_too_many_arguments(self):
        self.assert_semantic_error("pagar horas_extra(extras)", "espera 2 argumento(s) y recibió 1")
        self.assert_semantic_error("pagar horas_extra(extras, salario, 3)", "recibió 3")

    @pending_phase
    def test_argument_type(self):
        self.assert_semantic_error("pagar horas_extra(salario, salario)", "argumento 1")

    @pending_phase
    def test_if_condition_and_pay_types(self):
        self.assert_semantic_error('si salario <= "alto" {\n}\npagar salario', "comparar dinero con texto")
        self.assert_semantic_error("pagar nombre", "'pagar' debe recibir dinero")

    @pending_phase
    def test_constant_cannot_change(self):
        self.assert_semantic_error("SMMLV = salario\npagar salario", "constante")

    @pending_phase
    def test_integer_promotes_to_decimal(self):
        table = check_source("para cada empleado {\n f: decimal = extras * 2\n pagar salario * f\n}")
        self.assertEqual(table.history[-1].type, "decimal")


if __name__ == "__main__":
    unittest.main()
