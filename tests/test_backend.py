import unittest

from compiler.ast_nodes import (
    Assignment,
    BinaryOperation,
    Block,
    Comparison,
    EmployeeBlock,
    Identifier,
    IfStatement,
    MoneyLiteral,
    PayStatement,
    Program,
)
from compiler.code_generator import TargetCodeGenerator
from compiler.ir import TacInstruction, TacOp
from compiler.ir_generator import IRGenerator
from compiler.lexer import Lexer
from compiler.memory_manager import MemoryManager
from compiler.optimizer import Optimizer
from compiler.parser import Parser
from compiler.pipeline import compile_source
from compiler.virtual_machine import VirtualMachine
from tests.helpers import read_example

EMPLOYEES = [
    {"nombre": "Ana Ortiz", "salario": 1750905, "extras": 6},
    {"nombre": "Luis Mora", "salario": 4200000, "extras": 0},
    {"nombre": "Eva Pantoja", "salario": 2500000, "extras": 3},
]


def tac_of(source: str):
    program = Parser(Lexer(source).tokenize()).parse()
    params = {f.name: [p.name for p in f.parameters] for f in program.functions}
    return IRGenerator().generate(program), params


def run_vm(tac, params):
    return VirtualMachine(MemoryManager(), params).run(tac, EMPLOYEES)


def if_rule(else_block=None):
    # si salario <= TOPE_AUXILIO { devengado = devengado + AUXILIO }
    return IfStatement(
        condition=Comparison(operator="<=", left=Identifier(name="salario"), right=Identifier(name="TOPE_AUXILIO")),
        then_block=Block(statements=[
            Assignment(
                name="devengado",
                value=BinaryOperation(operator="+", left=Identifier(name="devengado"), right=Identifier(name="AUXILIO")),
            )
        ]),
        else_block=else_block,
    )


def simulate(lines, memory):
    """Ejecuta el ensamblador en línea recta (sin saltos) para comprobar que los spills no pierden valores."""
    registers = {}

    def read(operand):
        name = operand.strip("[]")
        if name in registers:
            return registers[name]
        if name in memory:
            return memory[name]
        return float(name)

    for line in lines:
        if line.endswith(":") or line in ("HALT",):
            continue
        op, rest = line.split(" ", 1)
        target, source = [part.strip() for part in rest.split(",")] if "," in rest else (rest.strip(), None)
        dest = target.strip("[]")
        if op == "MOV" or op == "LOAD":
            value = read(source)
            if dest.startswith("R"):
                registers[dest] = value
            else:
                memory[dest] = value
        elif op == "STORE":
            memory[source.strip("[]")] = registers[dest]
        elif op in ("ADD", "SUB", "MUL", "DIV"):
            a, b = registers[dest], read(source)
            registers[dest] = {"ADD": a + b, "SUB": a - b, "MUL": a * b, "DIV": a / b}[op]
    return memory


class IRGeneratorTest(unittest.TestCase):
    def test_if_statement_produces_jump_and_label(self):
        program = Program(employee_block=EmployeeBlock(body=Block(statements=[if_rule()])))
        text = [i.to_text() for i in IRGenerator().generate(program)]
        self.assertIn("t1 = salario <= TOPE_AUXILIO", text)
        self.assertIn("ifFalse t1 goto L1", text)
        self.assertIn("L1:", text)

    def test_if_statement_matches_section_3_exactly(self):
        # El TAC del documento (sección 3, fase 4), entre begin_employee y end_employee
        program = Program(employee_block=EmployeeBlock(body=Block(statements=[if_rule()])))
        text = [i.to_text() for i in IRGenerator().generate(program)]
        self.assertEqual(text[1:-1], [
            "t1 = salario <= TOPE_AUXILIO",
            "ifFalse t1 goto L1",
            "t2 = devengado + AUXILIO",
            "devengado = t2",
            "L1:",
        ])

    def test_else_jumps_over_the_else_block(self):
        else_block = Block(statements=[Assignment(name="devengado", value=Identifier(name="salario"))])
        program = Program(employee_block=EmployeeBlock(body=Block(statements=[if_rule(else_block)])))
        text = [i.to_text() for i in IRGenerator().generate(program)]
        self.assertEqual(text[1:-1], [
            "t1 = salario <= TOPE_AUXILIO",
            "ifFalse t1 goto L1",
            "t2 = devengado + AUXILIO",
            "devengado = t2",
            "goto L2",
            "L1:",
            "devengado = salario",
            "L2:",
        ])

    def test_function_call_uses_param_and_call(self):
        tac, _ = tac_of(read_example("bakery.nc"))
        text = [i.to_text() for i in tac]
        self.assertIn("begin_func horas_extra", text)
        self.assertIn("param extras", text)
        self.assertIn("param valor_hora", text)
        self.assertTrue(any(line.endswith("= call horas_extra, 2") for line in text))
        self.assertIn("return t3", text)
        begin = next(i for i in tac if i.op == TacOp.BEGIN_FUNCTION)
        self.assertEqual(begin.arg2, "horas,valor_hora")

    def test_every_instruction_keeps_its_source_line(self):
        tac, _ = tac_of(read_example("bakery.nc"))
        self.assertTrue(all(isinstance(i.line, int) and i.line > 0 for i in tac))
        comparison = next(i for i in tac if i.op == "<=")
        self.assertEqual(comparison.line, 14)

    def test_money_literal_is_written_in_pesos(self):
        program = Program(employee_block=EmployeeBlock(body=Block(statements=[PayStatement(value=MoneyLiteral(value=1750905))])))
        text = [i.to_text() for i in IRGenerator().generate(program)]
        self.assertIn("pay 1750905", text)

    def test_unoptimized_tac_runs_in_the_virtual_machine(self):
        tac, params = tac_of(read_example("bakery.nc"))
        payroll = run_vm(tac, params)
        self.assertEqual(payroll[0]["pay"], 1914643)


class OptimizerTest(unittest.TestCase):
    def test_constant_folding(self):
        tac = [TacInstruction(TacOp.MUL, "2", "1750905", "t1"), TacInstruction(TacOp.ASSIGN, "t1", None, "TOPE_AUXILIO")]
        result = Optimizer().optimize(tac)
        self.assertIn("TOPE_AUXILIO = 3501810", [i.to_text() for i in result.instructions])
        self.assertLess(len(result.instructions), len(tac))

    def test_bakery_matches_section_3(self):
        tac, _ = tac_of(read_example("bakery.nc"))
        text = [i.to_text() for i in Optimizer().optimize(tac).instructions]
        self.assertIn("TOPE_AUXILIO = 3501810", text)
        self.assertIn("devengado = devengado + 249095", text)
        self.assertTrue(any(line.endswith("= salario <= 3501810") for line in text))

    def test_original_tac_is_not_modified(self):
        tac, _ = tac_of(read_example("bakery.nc"))
        before = [i.to_text() for i in tac]
        Optimizer().optimize(tac)
        self.assertEqual([i.to_text() for i in tac], before)

    def test_every_change_is_reported(self):
        tac, _ = tac_of(read_example("bakery.nc"))
        result = Optimizer().optimize(tac)
        kinds = " ".join(result.steps)
        self.assertIn("Plegado de constantes", kinds)
        self.assertIn("Propagación de constantes", kinds)
        self.assertIn("Eliminación de copias", kinds)
        self.assertEqual(result.to_dict()["removed"], len(tac) - len(result.instructions))

    def test_local_variables_are_not_propagated(self):
        # devengado se reasigna dentro del si: no es constante
        tac, _ = tac_of(read_example("bakery.nc"))
        text = [i.to_text() for i in Optimizer().optimize(tac).instructions]
        self.assertTrue(any("devengado - salud" in line for line in text))

    def test_payroll_is_the_same_before_and_after(self):
        for example in ("bakery.nc", "spill.nc", "bonus_valid.nc"):
            with self.subTest(example=example):
                tac, params = tac_of(read_example(example))
                optimized = Optimizer().optimize(tac).instructions
                self.assertEqual(run_vm(tac, params), run_vm(optimized, params))


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

    def test_if_from_section_3(self):
        tac = [
            TacInstruction("<=", "salario", "3501810", "t1"),
            TacInstruction(TacOp.IF_FALSE, "t1", None, "L1"),
            TacInstruction("+", "devengado", "249095", "devengado"),
            TacInstruction(TacOp.LABEL, None, None, "L1"),
        ]
        result = TargetCodeGenerator().translate(tac)
        self.assertEqual(result.lines, [
            "MOV [R0], [salario]",
            "CMP [R0], [3501810]",
            "JG L1",
            "MOV [R0], [devengado]",
            "ADD [R0], [249095]",
            "MOV [devengado], [R0]",
            "L1:",
        ])
        self.assertEqual(result.unsupported, [])

    def test_division_and_jumps_are_translated(self):
        tac = [
            TacInstruction("/", "salario", "240", "t1"),
            TacInstruction(TacOp.GOTO, None, None, "L2"),
            TacInstruction(">", "a", "b", "t2"),
            TacInstruction(TacOp.IF_FALSE, "t2", None, "L3"),
        ]
        lines = TargetCodeGenerator().translate(tac).lines
        self.assertIn("DIV [R0], [240]", lines)
        self.assertIn("JMP L2", lines)
        self.assertIn("JLE L3", lines)

    def test_whole_bakery_has_nothing_unsupported(self):
        response = compile_source(read_example("bakery.nc"), EMPLOYEES)
        self.assertTrue(response["ok"])
        self.assertEqual(response["phases"]["assembly"]["unsupported"], [])

    def test_spill_example_keeps_the_right_value(self):
        # prueba = (salario - salud) * 2 + (pension + salud) * 3
        tac, _ = tac_of(read_example("spill.nc"))
        optimized = Optimizer().optimize(tac).instructions
        employee = [i for i in optimized if i.op not in (TacOp.BEGIN_EMPLOYEE, TacOp.END_EMPLOYEE, TacOp.PAY)]
        result = TargetCodeGenerator().translate(employee)
        self.assertTrue(any(line.startswith("STORE") for line in result.lines))
        self.assertEqual(result.spills[0]["address"], "0x2000")

        memory = simulate(result.lines, {"salario": 1750905.0})
        salud = 1750905 * 0.04
        expected = (1750905 - salud) * 2 + (salud + salud) * 3
        self.assertAlmostEqual(memory["prueba"], expected)

    def test_freeing_dead_temps_reduces_spills(self):
        tac, _ = tac_of(read_example("spill.nc"))
        result = TargetCodeGenerator().translate(Optimizer().optimize(tac).instructions)
        comparison = result.comparison
        self.assertGreater(comparison["professorSpills"], 0)
        self.assertLess(comparison["freeingSpills"], comparison["professorSpills"])

        employee = [line for line in comparison["freeingLines"] if line not in ("PAY [prueba]",)]
        memory = simulate(employee[employee.index("EMPLOYEE:"):], {"salario": 1750905.0})
        salud = 1750905 * 0.04
        self.assertAlmostEqual(memory["prueba"], (1750905 - salud) * 2 + (salud + salud) * 3)


if __name__ == "__main__":
    unittest.main()
