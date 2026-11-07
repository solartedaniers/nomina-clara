import unittest

from compiler.errors import LexicalError
from compiler.lexer import Lexer
from compiler.tokens import TokenType
from tests.helpers import pending_phase, read_example


class LexerTest(unittest.TestCase):
    @pending_phase
    def test_recognizes_money_keywords_and_operators(self):
        tokens = Lexer("si salario <= $1.750.905 {").tokenize()
        kinds = [(t.type, t.value) for t in tokens[:-1]]
        self.assertEqual(
            kinds,
            [
                (TokenType.KEYWORD, "si"),
                (TokenType.IDENTIFIER, "salario"),
                (TokenType.REL_OP, "<="),
                (TokenType.MONEY, "$1.750.905"),
                (TokenType.LBRACE, "{"),
            ],
        )
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    @pending_phase
    def test_tracks_line_and_column(self):
        tokens = Lexer("# comentario\npagar salario").tokenize()
        self.assertEqual((tokens[1].line, tokens[1].col), (2, 7))

    @pending_phase
    def test_reports_invalid_character(self):
        with self.assertRaises(LexicalError) as context:
            Lexer(read_example("lexical_error.nc")).tokenize()
        self.assertEqual(context.exception.line, 5)

    @pending_phase
    def test_error_message_has_character_line_and_column(self):
        with self.assertRaises(LexicalError) as context:
            Lexer(read_example("lexical_error.nc")).tokenize()
        error = context.exception
        self.assertEqual((error.line, error.col), (5, 29))
        self.assertIn("'@'", error.message)
        self.assertIn("línea 5", error.message)
        self.assertIn("columna 29", error.message)

    @pending_phase
    def test_ignores_comments(self):
        tokens = Lexer("# todo esto se ignora\nsalud # y esto también").tokenize()
        self.assertEqual([(t.type, t.value) for t in tokens], [
            (TokenType.IDENTIFIER, "salud"),
            (TokenType.EOF, ""),
        ])

    @pending_phase
    def test_money_decimal_and_integer(self):
        tokens = Lexer("$1.750.905 $500 1.25 240").tokenize()
        self.assertEqual([(t.type, t.value) for t in tokens[:-1]], [
            (TokenType.MONEY, "$1.750.905"),
            (TokenType.MONEY, "$500"),
            (TokenType.DECIMAL, "1.25"),
            (TokenType.INTEGER, "240"),
        ])

    @pending_phase
    def test_money_with_or_without_thousands_separators(self):
        tokens = Lexer("$1.750.905 $1750905").tokenize()
        self.assertEqual([(t.type, t.value) for t in tokens[:-1]], [
            (TokenType.MONEY, "$1.750.905"),
            (TokenType.MONEY, "$1750905"),
        ])

    @pending_phase
    def test_malformed_money_is_a_lexical_error(self):
        for source in ["$1.7509", "$1750.905", "$1.75", "$12."]:
            with self.subTest(source=source):
                with self.assertRaises(LexicalError) as context:
                    Lexer(f"pagar {source}").tokenize()
                self.assertEqual((context.exception.line, context.exception.col), (1, 7))
                self.assertIn(f"'{source}'", context.exception.message)

    @pending_phase
    def test_two_character_operators_before_one_character(self):
        tokens = Lexer("<= >= == != < > =").tokenize()
        self.assertEqual([(t.type, t.value) for t in tokens[:-1]], [
            (TokenType.REL_OP, "<="),
            (TokenType.REL_OP, ">="),
            (TokenType.REL_OP, "=="),
            (TokenType.REL_OP, "!="),
            (TokenType.REL_OP, "<"),
            (TokenType.REL_OP, ">"),
            (TokenType.ASSIGN, "="),
        ])


if __name__ == "__main__":
    unittest.main()
