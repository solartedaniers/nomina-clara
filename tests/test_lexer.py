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


if __name__ == "__main__":
    unittest.main()
