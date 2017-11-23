class TString:
    def __init__(self, value):
        self.value = value


class TNumber:
    def __init__(self, value):
        self.value = value


class TSymbol:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


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


class TNull:
    pass
