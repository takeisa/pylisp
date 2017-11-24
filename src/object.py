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
