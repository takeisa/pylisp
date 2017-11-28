class VM:
    def __init__(self):
        self.reg = Register()

    def run(self):
        x = self.reg.x
        while x:
            print(x)
            self.reg.x.exec(self.reg)
            x = self.reg.x

        return self.reg.a


class Register:
    def __init__(self):
        self.a = None
        self.x = None
        self.e = None


class Env:
    def __init__(self, vars, vals, parent):
        self.parent = parent
        self.map = dict(zip(vars, vals))

    def look_up(self, var):
        val = self.map.get(var)
        if val:
            return val
        else:
            if self.parent:
                return self.parent.look_up(var)
            else:
                return None

    def set(self, var, val):
        if not self.map.get(var):
            raise Exception(f"undefined: {var}")
        self.map[var] = val

    def extend(self, vars, vals):
        return Env(vars, vals, self)


class Halt:
    def exec(self, reg):
        reg.x = None


class Refer:
    def __init__(self, var, x):
        self.var = var
        self.x = x

    def exec(self, reg):
        reg.a = reg.e.look_up(self.var)
        reg.x = self.x


class Constant:
    def __init__(self, obj, x):
        self.obj = obj
        self.x = x

    def exec(self, reg):
        reg.a = self.obj
        reg.x = self.x


class Assign:
    def __init__(self, var, x):
        self.var = var
        self.x = x

    def exec(self, reg):
        reg.e.set(self.var, reg.a)
        reg.x = self.x
