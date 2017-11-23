import sys
import re
from object import *


class Reader:
    def __init__(self, stream):
        self.stream = stream
        self.c = None

    def read_char(self):
        ret_c = self.c
        if ret_c == "":
            return ret_c

        self.c = None
        if ret_c is None:
            ret_c = self.stream.read(1)

        return ret_c

    def unread_char(self, c):
        self.c = c


class Lexer:
    def __init__(self, reader):
        self.reader = reader
        self.token = None

    @staticmethod
    def is_space(c):
        return c in " \t\r\n"

    def skip_spaces(self):
        c = self.reader.read_char()
        while c != "" and Lexer.is_space(c):
            c = self.reader.read_char()

        self.reader.unread_char(c)

    def read_string(self):
        cs = []
        c = self.reader.read_char()
        while c != "\"":
            cs.append(c)
            c = self.reader.read_char()

        return "".join(cs)

    def read_ident(self):
        cs = []
        c = self.reader.read_char()
        while not (Lexer.is_space(c) or c in "()"):
            cs.append(c)
            c = self.reader.read_char()
        self.reader.unread_char(c)

        return "".join(cs)

    @staticmethod
    def is_number(s):
        return re.fullmatch(r"\d+", s)

    def get_token(self):
        if self.token:
            ret_token = self.token
            self.token = None
            return ret_token

        self.skip_spaces()

        token = None

        c = self.reader.read_char()
        if c == "":
            pass
        elif c == "(":
            token = ("LPAR", c)
        elif c == ")":
            token = ("RPAR", c)
        elif c == ".":
            token = ("DOT", c)
        elif c == "\"":
            s = self.read_string()
            token = ("STRING", s)
        else:
            self.reader.unread_char(c)
            ident = self.read_ident()
            if Lexer.is_number(ident):
                token = ("NUMBER", ident)
            else:
                token = ("IDENT", ident)

        return token

    def unget_token(self, token):
        self.token = token


class TSyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SexpReader:
    def __init__(self, stream=sys.stdin):
        self.lexer = Lexer(Reader(stream))

    def read_pair(self):
        token = self.lexer.get_token()
        token_type, token_value = token

        if token_type == "RPAR":
            return TNull()

        if token_type == "DOT":
            raise TSyntaxError("bad dot syntax")
        self.lexer.unget_token(token)

        car = self.read()

        token = self.lexer.get_token()
        token_type, _ = token
        if token_type == "DOT":
            cdr = self.read()
            token_type, _ = self.lexer.get_token()
            if token_type != "RPAR":
                raise TSyntaxError("bad dot syntax")
        else:
            self.lexer.unget_token(token)
            cdr = self.read_pair()

        return TPair(car, cdr)

    def read(self):
        token_type, token_value = self.lexer.get_token()
        obj = None
        if token_type == "STRING":
            obj = TString(token_value)
        elif token_type == "NUMBER":
            obj = TNumber(int(token_value))
        elif token_type == "IDENT":
            obj = TSymbol(token_value)
        elif token_type == "LPAR":
            obj = self.read_pair()

        return obj

# (a b c . d)
# -> (pair a (pair b (pair c . d)))
# (a b c d)
# -> (pair a (pair b (pair c (pair d nil))))

# (
# ) -> null ()
# . -> error
# _ -> (cons car (read


def repl():
    reader = SexpReader(sys.stdin)
    while True:
        print(">> ", end="")
        sys.stdout.flush()
        obj = reader.read()
        print(obj)
        sys.stdout.flush()


def main():
    repl()


if __name__ == '__main__':
    main()