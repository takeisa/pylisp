class TString:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "\"" + self.value + "\""


class TNumber:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class TSymbol:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self._name == other._name


class TPair:
    def __init__(self, car, cdr):
        self._car = car
        self._cdr = cdr

    @property
    def car(self):
        return self._car

    @property
    def cdr(self):
        return self._cdr

    def __str__(self):
        ss = []
        ss.append("(")
        ss.append(str(self.car))

        obj = self.cdr
        while isinstance(obj, TPair):
            ss.append(" ")
            ss.append(str(obj.car))
            obj = obj.cdr

        if not isinstance(obj, TNull):
            ss.append(" . ")
            ss.append(str(obj))

        ss.append(")")

        return "".join(ss)


class TNull:
    def __str__(self):
        return "()"


class TClosure:
    def __init__(self, body, env, vars):
        self.body = body
        self.enf = env
        self.vars = vars
