#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
values of python
"""
from util import *
from environment import *


class Value(object):
    def as_pyval(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def pybool(self):
        """
        return True or False (not BoolValue)
        """
        return bool(self.value)

    def bool(self):
        return BoolValue(self.pybool())

    def pycmp(self, obj):
        """
        all other comparison methods such as cmp, lt, lte depends on this
        method, so this mthod need override in the subclass
        """
        if not IS(obj, NumValue):
            return -1              # arbitrary value

        if self.value == obj.value:
            return 0
        elif self.value > obj.value:
            return 1
        else:
            return -1

    def cmp(self, obj):
        return IntValue(self.pycmp(obj))

    def eq(self, obj):
        ret = True if self.pycmp(obj) == 0 else False
        return BoolValue(ret)

    def neq(self, obj):
        ret = True if self.pycmp(obj) != 0 else False
        return BoolValue(ret)

    def lt(self, obj):
        ret = True if self.pycmp(obj) < 0 else False
        return BoolValue(ret)

    def lte(self, obj):
        ret = True if self.pycmp(obj) <= 0 else False
        return BoolValue(ret)

    def gt(self, obj):
        ret = True if self.pycmp(obj) > 0 else False
        return BoolValue(ret)

    def gte(self, obj):
        ret = True if self.pycmp(obj) >= 0 else False
        return BoolValue(ret)

class NoneValue(Value):
    def __init__(self):
        self.value = None

######################################################################
#          numerical value
######################################################################
class NumValue(Value):
    """
    this is the base class of all the numerial values. it is mainly used to
    implement arithmetical operations, we can use the special method to
    simplify the code, but in order to make the interpreter to be implemented
    easily in other languages(like java etc), we avoid using these methods

    + : (number,number), (string,string), (list,list), (tuple,tuple)
        and instance which has __add__ method
    - : (number, number) and instance which has __sub__ method
    * : (int, number), (int, string), (int, list), (int,tuple) and instance
        which has __mul__ method
    / : (number, number) and instance which has __div__ method

    """

    def add(self, obj):
        if not IS(obj, NumValue):
            fatal("+ : unsupport oprand types")
        if IS(self, FloatValue) or IS(obj, FloatValue):
            return FloatValue(self.value + obj.value)
        else:
            return IntValue(self.value + obj.value)

    def sub(self, obj):
        if not IS(obj, NumValue):
            fatal("- : unsupport oprand types")
        if IS(self, FloatValue) or IS(obj, FloatValue):
            return FloatValue(self.value - obj.value)
        else:
            return IntValue(self.value - obj.value)

    def mul(self, obj):
        if not (IS(obj, NumValue) or IS(obj, SeqValue)):
            fatal("* : unsupport oprand types")

        if IS(self, IntValue) and IS(obj, SeqValue):
            return obj.mul(self)
        if IS(self, FloatValue) or IS(obj, FloatValue):
            return FloatValue(self.value + obj.value)
        else:
            return IntValue(self.value * obj.value)

    def div(self, obj):
        if not IS(obj, NumValue):
            fatal("/ : unsupport oprand types")
        if obj.value == 0:
            fatal("ZeroDivisionError(/): integer division or modulo by zero")
        if IS(self, FloatValue) or IS(obj, FloatValue):
            return FloatValue(self.value / obj.value)
        else:
            return IntValue(self.value / obj.value)

class IntValue(NumValue):
    def __init__(self, val):
        self.value = val

class FloatValue(NumValue):
    def __init__(self, val):
        self.value = val

class BoolValue(IntValue):
    """
    in python True is identical to 1, False is identical to 0, so BoolValue
    is subclass of IntValue
    """
    def __init__(self, val):
        self.value = val

###################################################################
#               sequence values (list tuple)
##################################################################

class SeqValue(Value):
    def pylen(self):
        return len(self.value)

    def len(self):
        ret = len(self.value)
        return IntValue(ret)

    def getitem(self, idx):
        """
        need override for string value.
        """
        if not IS(idx, IntValue):
            fatal("TypeError, index of sequence must be a integer.")
        return self.value[idx.value]

    def getslice(self, lower=0, upper=None, step=1):
        if upper is None:
            upper = len(self.value)+1
        ret = self.value[lower:upper:step]
        return self.__class__(ret)

    def contains(self, obj):
        for ele in self.value:
            if obj.pycmp(ele) == 0:
                return BoolValue(True)
        return BoolValue(False)

class StrValue(SeqValue):
    def __init__(self, val):
        self.value = val

    def getitem(self, idx):
        if not IS(idx, IntValue):
            fatal("TypeError, index of sequence must be a integer.")
        ret = self.value[idx.value]
        return StrValue(ret)

    def add(self, obj):
        if not IS(obj, StrValue):
            fatal("TypeError: can't add string to no-string type")
        return StrValue(self.value + obj.value)

    def mul(self, obj):
        if not IS(obj, IntValue):
            fatal("TypeError: can't multiply string with no-int value")
        return StrValue(self.value * obj.value)

    def contains(self, ss):
        if not IS(ss, StrValue):
            fatal("'in <string>' requires string as left operand")

        ret = (ss.value in self.value)
        return BoolValue(ret)


class ListValue(SeqValue):
    def __init__(self, elts):
        self.value = list(elts)

    def add(self, obj):
        if not IS(obj, ListValue):
            fatal("TypeError: can only concatenate list to list")
        return ListValue(self.value + obj.value)

    def mul(self, obj):
        if not IS(obj, IntValue):
            fatal("TypeError: can't multiply list with no-int value")
        return ListValue(self.value * obj.value)

    def setitem(self, idx, val):
        if not IS(idx, IntValue):
            fatal("TypeError: index of list must be an integer.")
        self.value[idx.pyval()] = val

    def setslice(self, lower, upper, val):
        pass

    def __str__(self):
        ss = ' '.join(map(str, self.value))
        return "[%s]" % ss

class TupleValue(SeqValue):
    def __init__(self, elts):
        self.value = tuple(elts)

    def add(self, obj):
        if not IS(obj, TupleValue):
            fatal("TypeError: can only concatenate tuple to tuple")
        return TupleValue(self.value + obj.value)

    def mul(self, obj):
        if not IS(obj, IntValue):
            fatal("TypeError: can't multiply list with no-int value")
        return TupleValue(self.value * obj.value)

    def __str__(self):
        ss = ' '.join(map(str, self.value))
        return "(%s)" % ss

class DictValue(Value):
    """
    key-value mappings:
    1. key must be immutable types, so list, dict and set can't be a key
    """
    def __init__(self, elts):
        self.value = dict(elts)

    def getitem(self, n):
        return self.value[n]

    def setitem(self, k, v):
        self.value[k] = v

    def __str__(self):
        return "dict=>:" + str(self.value)

    def contains(self, obj):
        for k in self.value:
            if obj.pycmp(k) == 0:
                return BoolValue(True)
        return BoolValue(False)

class SetValue(Value):
    def __init__(self, elts):
        self.value = set(elts)

    def __str__(self):
        return str(self.value)

    def contains(self, obj):
        for ele in self.value:
            if obj.pycmp(ele) == 0:
                return BoolValue(True)
        return BoolValue(False)

######################################################################
# callable values include
# 1. built-in function
# 2. user-defined function
# 3. built-in method
# 4. method
# 5. user-defined method
# 6. class
# 7. instance which has __call__ method
# 8. generator functions
######################################################################
class ClosureValue(Value):
    def __init__(self, func, env):   # func is ast node
        self.env = env
        self.posargs = map(get_id, func.args.args)  # positional arguments
        self.vararg = func.args.vararg              # string
        self.kwarg = func.args.kwarg                # string
        self.defaults = func.args.defaults          # exp list

        self.body = func.body

    def as_pyval(self):
        fatal("can't call as_pyval on closure value")

    def pybool(self):
        return True

class LambdaValue(ClosureValue):
    def __init__(self, func, env):
        super(LambdaValue, self).__init__(func, env)
        self.name = None

class FunValue(ClosureValue):
    def __init__(self, func, env):
        super(FunValue, self).__init__(func, env)
        self.name = func.name

class MethodValue(ClosureValue):
    def __init__(self, func, env):
        super(MethodValue, self).__init__(func, env)
        self.name = func.name
        self.cls = None

class PrimFunValue(ClosureValue):
    def __init__(self, fun):
        self.fun = fun

######################################################################
#          module value
######################################################################
class ModuleValue(Value):
    """
    module value has some special attributes:
    1. __name__: full quialitfied name
    2. __file__: file name of this moudle, if it is a package, this attribute
                 must contain __init__.py
    3. __package__: if it is a package, then this attribute is same as the
                    __name__ attribute, otherwise it's the package
    """
    def __init__(self, fname, name, p_env):
        self.fname = name
        self.name = name
        if IS(self, PackageValue):
            self.package = self.name
        else:
            self.package = self.name.rpartition(".")[0]
        self.env = ModuleEnv(p_env)
        self.globals = set()
        # TODO: specify the correct value of these special attributes
        self.env.put("__name__", self.name)
        self.env.put("__file__", self.fname)
        self.env.put("__doc__", None)
        self.env.put("__package__", self.package)

    def as_pyval(self):
        fatal("can't call as_pyval on module value")

    def add_global(self, name):
        self.globals.add(name)

    def is_global(self, name):
        return (name in self.globals)

    def getattr(self, name):
        """
        1. check if the moudle has __all__ attribute
        2. if the moudle has __all__ attribute then check if name is in __all__
        3. if the moudle doesn't has __all__ attribute then check if name starts
           with _
        """
        try:
            all_names = self.env.lookup("__all__")
        except EnvLookupError:
            all_names = None

        if all_names is None:
            if name.startswith("_"):
                fatal("this moudle doesn't export name(%s)" % name)
        else:
            if all_names.contains(StrValue(name)):
                fatal("this moudle doesn't export name(%s)" % name)

        try:
            return self.env.lookup(name)
        except EnvLookupError:
            return None

    def __str__(self):
        return "<Module:%s>" % self.name

    def pybool(self):
        return True

class PackageValue(ModuleValue):
    """
    packages are just a special kind of module, it has some special attribute:
    1. __path__:
    """
    def __init__(self, fname, name, p_env):
        super(PackageValue, self).__init__(fname, name, p_env)
        self.env.put("__path__", None) # TODO
######################################################################
#          class value
######################################################################
class ClassValue(Value):
    def __init__(self, name, bases=None):
        self.name = name
        self.env = ClassEnv()
        self.bases = bases      # super classes

        # TODO: specify the correct value of these special attributes
        self.env.put("__name__", name)
        self.env.put("__module__", None)
        self.env.put("__dict__", self.env.table)
        self.env.put("__bases__", bases)
        self.env.put("__doc__", None)

    def pybool(self):
        return True

    def as_pyval(self):
        fatal("can't call as_pyval on class value")

    def getattr(self, name):
        try:
            val = self.env.lookup(name)
            return val
        except EnvLookupError:
            if self.bases is None:
                return None
            for base in self.bases:
                val = base.getattr(name)
                if val is not None:
                    return val
            return None

######################################################################
#          instance value
######################################################################
class InstanceValue(Value):
    def __init__(self, cls):
        self.cls = cls
        self.env = InstanceEnv()

        # TODO: specify the correct value of these special attributes
        self.env.put("__class__", cls)
        self.env.put("__dict__", self.env.table)

    def pybool(self):
        nonzero = self.getattr("__nonzero__")
        if nonzero is None:
            return True
        else:
            return False        # TODO: invoke the nonzero method

    def as_pyval(self):
        fatal("can't call as_pyval on instance value")

    def getattr(self, name):
        try:
            val = self.env.lookup(name)
            return val
        except EnvLookupError:
            return self.cls.getattr(name)

    def contains(self, obj):    # TODO:
        contain = self.getattr("__contains__")
        # TODO: invoke the contains method

######################################################################
#          file value
######################################################################
class FileValue(Value):
    def __init__(self, fname, flag):
        pass

######################################################################
#          global constants
######################################################################
none = NoneValue()
true = BoolValue(True)
false = BoolValue(False)
