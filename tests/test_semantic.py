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
from tests.helpers import pending_phase


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


if __name__ == "__main__":
    unittest.main()
