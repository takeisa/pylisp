import unittest
import io
from pylisp import Reader, Lexer, SexpReader, TSyntaxError
from object import TString, TNumber, TSymbol, TPair, TNull


class TestReader(unittest.TestCase):
    @staticmethod
    def create_reader(s):
        return Reader(io.StringIO(s))

    def setUp(self):
        pass

    def test_read_char(self):
        reader = TestReader.create_reader("ab")
        self.assertEqual("a", reader.read_char())
        self.assertEqual("b", reader.read_char())
        self.assertEqual("", reader.read_char())

    def test_unread_char(self):
        reader = TestReader.create_reader("ab")
        c = reader.read_char()
        self.assertEqual("a", c)
        reader.unread_char(c)
        c = reader.read_char()
        self.assertEqual("a", c)
        c = reader.read_char()
        self.assertEqual("b", c)
        reader.unread_char(c)
        c = reader.read_char()
        self.assertEqual("b", c)
        self.assertEqual("", reader.read_char())


class TestLexer(unittest.TestCase):
    @staticmethod
    def create_lexer(s):
        return Lexer(Reader(io.StringIO(s)))

    def test_get_token(self):
        lexer = TestLexer.create_lexer("  (\"abc\" 123 ident .)")
        self.assertEqual(("LPAR", "("), lexer.get_token())
        self.assertEqual(("STRING", "abc"), lexer.get_token())
        self.assertEqual(("NUMBER", "123"), lexer.get_token())
        self.assertEqual(("IDENT", "ident"), lexer.get_token())
        self.assertEqual(("DOT", "."), lexer.get_token())
        self.assertEqual(("RPAR", ")"), lexer.get_token())
        self.assertIsNone(lexer.get_token())

    def test_unget_token(self):
        lexer = TestLexer.create_lexer("(a b)")
        self.assertEqual(("LPAR", "("), lexer.get_token())
        token = lexer.get_token()
        self.assertEqual(("IDENT", "a"), token)
        lexer.unget_token(token)
        self.assertEqual(("IDENT", "a"), lexer.get_token())
        token = lexer.get_token()
        self.assertEqual(("IDENT", "b"), token)
        lexer.unget_token(token)
        self.assertEqual(("IDENT", "b"), lexer.get_token())
        self.assertEqual(("RPAR", ")"), lexer.get_token())






class TestSexpReader(unittest.TestCase):
    @staticmethod
    def create_reader(s):
        return SexpReader(io.StringIO(s))

    def test_read_string_number_symbol(self):
        reader = TestSexpReader.create_reader("\"abc\" 123 symbol")

        obj = reader.read()
        self.assertIsInstance(obj, TString)
        self.assertEqual("abc", obj.value)

        obj = reader.read()
        self.assertIsInstance(obj, TNumber)
        self.assertEqual(123, obj.value)

        obj = reader.read()
        self.assertIsInstance(obj, TSymbol)
        self.assertEqual("symbol", obj.name)

    def test_read_null(self):
        reader = TestSexpReader.create_reader("()")
        obj = reader.read()
        self.assertIsInstance(obj, TNull)

    def test_read_pair_syntax_error(self):
        reader = TestSexpReader.create_reader("(. a)")
        with self.assertRaises(TSyntaxError):
            reader.read()

    def test_read_pair(self):
        reader = TestSexpReader.create_reader("(a . b)")
        pair = reader.read()
        self.assertIsInstance(pair, TPair)
        self.assertIsInstance(pair.car, TSymbol)
        self.assertEqual("a", pair.car.name)
        self.assertIsInstance(pair.cdr, TSymbol)
        self.assertEqual("b", pair.cdr.name)

    def test_read_pair_list(self):
        reader = TestSexpReader.create_reader("(a b)")
        pair1 = reader.read()
        self.assertIsInstance(pair1, TPair)
        self.assertIsInstance(pair1.car, TSymbol)
        self.assertEqual("a", pair1.car.name)
        pair2 = pair1.cdr
        self.assertIsInstance(pair2, TPair)
        self.assertIsInstance(pair2.car, TSymbol)
        self.assertEqual("b", pair2.car.name)
        self.assertIsInstance(pair2.cdr, TNull)



if __name__ == '__main__':
    unittest.main()
