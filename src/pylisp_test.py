import unittest
import io
from pylisp import Reader, Lexer, SexpReader, TSyntaxError, Eval
from object import TString, TNumber, TSymbol, TPair, TNull, TClosure
from vm import VM, Env, Halt, Refer, Constant, Assign, Closure


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


class TestObjectPrint(unittest.TestCase):
    def test_string(self):
        sut = TString("abc")
        self.assertEqual("\"abc\"", str(sut))

    def test_symbol(self):
        sut = TSymbol("abc")
        self.assertEqual("abc", str(sut))

    def test_number(self):
        sut = TNumber(123)
        self.assertEqual("123", str(sut))

    def test_null(self):
        sut = TNull()
        self.assertEqual("()", str(sut))

    def test_pair(self):
        sut = TPair(TSymbol("a"), TSymbol("b"))
        self.assertEqual("(a . b)", str(sut))

    def test_pair_list_1(self):
        sut = TPair(TSymbol("a"), TNull())
        self.assertEqual("(a)", str(sut))

    def test_pair_list_2(self):
        sut = TPair(TSymbol("a"), TPair(TSymbol("b"), TNull()))
        self.assertEqual("(a b)", str(sut))

    def test_pair_list_2_dot(self):
        sut = TPair(TSymbol("a"), TPair(TSymbol("b"), TSymbol("c")))
        self.assertEqual("(a b . c)", str(sut))

    def test_pair_list_in_list(self):
        sut = TPair(TSymbol("a"), TPair(TPair(TSymbol("b"), TPair(TSymbol("c"), TNull())), TPair(TSymbol("d"), TNull())))
        self.assertEqual("(a (b c) d)", str(sut))


class TestEval(unittest.TestCase):
    @staticmethod
    def read(s):
        return SexpReader(io.StringIO(s)).read()

    @staticmethod
    def eval(s):
        return Eval().eval(TestEval.read(s))

    def test_number(self):
        obj = TestEval.eval("123")
        self.assertEqual(123, obj.value)


class TestVM(unittest.TestCase):
    def setUp(self):
        self.vm = VM()

    def test_halt(self):
        self.vm.reg.a = TString("halt")
        self.vm.reg.x = Halt()
        self.vm.run()
        a = self.vm.reg.a
        self.assertIsInstance(a, TString)
        self.assertEqual("halt", a.value)

    def test_constant(self):
        self.vm.reg.x = Constant(TString("constant"), Halt())
        self.vm.run()
        a = self.vm.reg.a
        self.assertIsInstance(a, TString)
        self.assertEqual("constant", a.value)

    def test_refer(self):
        self.vm.reg.e = Env([TSymbol("foo")], [TString("foo_val")], None)
        self.vm.reg.x = Refer(TSymbol("foo"), Halt())
        self.vm.run()
        a = self.vm.reg.a
        self.assertIsInstance(a, TString)
        self.assertEqual("foo_val", a.value)

    def test_assign(self):
        self.vm.reg.e = Env(["foo"], [TString("foo_val")], None)
        self.vm.reg.a = TString("foo_val_2")
        self.vm.reg.x = Assign("foo", Halt())
        self.vm.run()
        val = self.vm.reg.e.look_up("foo")
        self.assertIsInstance(val, TString)
        self.assertEqual("foo_val_2", val.value)

    def test_closure(self):
        self.vm.reg.e = Env(["foo"], [TNumber(10)], None)
        self.vm.reg.x = Closure([TSymbol("a"), TSymbol("b")], None, Halt())
        self.vm.run()
        a = self.vm.reg.a
        self.assertIsInstance(a, TClosure)


if __name__ == '__main__':
    unittest.main()
