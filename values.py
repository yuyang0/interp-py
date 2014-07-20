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

    def __nonzero__(self):      # suppoert bool primary function
        return bool(self.value)

    def __str__(self):
        return str(self.value)

class NoneValue(Value):
    def __init__(self):
        self.value = None

######################################################################
#          numerical value
######################################################################
class NumValue(Value):
    """
    this is a base class of all the numerial values. it is mainly used to
    implement arithmetical operations, we can use the special method to
    simplify the code, but in order to make the interpreter to be implemented
    easily in other languages(like java etc), we avoid using these method

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
    in python True is identical to 1, False is identical to 0
    """
    def __init__(self, val):
        self.value = val

###################################################################
#               sequence values (list tuple)
##################################################################

class SeqValue(Value):
    def len(self):
        return len(self.value)

    def getitem(self, idx):
        return self.value[idx]

    def setitem(self, idx, val):
        self.value[idx] = val

    def getslice(self, lower=0, upper=None, step=1):
        if upper is None:
            upper = len(self.value)+1
        ret = []
        for i in range(lower, upper, step):
            ret.append(self.value[i])
        return ret

    def setslice(self, lower, upper, val):
        if not IS(self, ListValue):
            fatal("only list value support set slice")

class StrValue(SeqValue):
    def __init__(self, val):
        self.value = val

    def add(self, obj):
        if not IS(obj, StrValue):
            fatal("TypeError: can't add string to no-string type")
        return StrValue(self.value + obj.value)

    def mul(self, obj):
        if not IS(obj, IntValue):
            fatal("TypeError: can't multiply string with no-int value")
        return StrValue(self.value * obj.value)

class ListValue(SeqValue):
    def __init__(self, elts):
        self.value = list(elts)

    def add(self, obj):
        if not IS(obj, ListValue):
            fatal("TypeError: can only concatenate list to list")
        return ListValue(self.value + obj.value)

    def mul(self, obj):
        if not (IS(obj, IntValue) or IS(obj, BoolValue)):
            fatal("TypeError: can't multiply list with no-int value")
        return ListValue(self.value * obj.value)

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
        if not (IS(obj, IntValue) or IS(obj, BoolValue)):
            fatal("TypeError: can't multiply list with no-int value")
        return TupleValue(self.value * obj.value)

    def __str__(self):
        ss = ' '.join(map(str, self.value))
        return "(%s)" % ss

class DictValue(Value):
    def __init__(self, elts):
        self.value = dict(elts)

    def getitem(self, n):
        return self.value[n]

    def setitem(self, k, v):
        self.value[k] = v

    def __str__(self):
        return "dict=>:" + str(self.value)

class SetValue(Value):
    def __init__(self, elts):
        self.value = set(elts)

    def __str__(self):
        return str(self.value)

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

    def __nonzero__(self):
        return True
    # def apply(self, posargs, keywords, starargs, kwargs):
    #     new_env = Env(self.env)
    #     for var, val in zip(self.posargs, posargs):
    #         new_env.put(var, val)
    #     for var, val in keywords.items():
    #         new_env.put(var, val)
    #     new_env.put(self.vararg, starargs)
    #     new_env.put(self.kwarg, kwargs)
    #     # TODO: maybe need to creat a new enviroment
    #     return value_of_stmts(self.body, new_env)

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
    def __init__(self, fname, name, p_env):
        self.fname = name
        self.name = name
        self.env = ModuleEnv(p_env)

        # TODO: specify the correct value of these special attributes
        self.env.put("__name__", self.name)
        self.env.put("__file__", self.fname)
        self.env.put("__doc__", None)

    def as_pyval(self):
        fatal("can't call as_pyval on module value")

    def get_attr(self, name):
        return self.env.lookup(name)

    def __str__(self):
        return "<Module:%s>" % self.name

    def __nonzero__(self):
        return True

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

    def __nonzero__(self):
        return True

    def as_pyval(self):
        fatal("can't call as_pyval on class value")

    def get_attr(self, name):
        try:
            val = self.env.lookup(name)
            return val
        except EnvLookupError:
            if self.bases is None:
                return None
            for base in self.bases:
                val = base.get_attr(name)
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

    def __nonzero__(self):
        nonzero = self.get_attr("__nonzero__")
        if nonzero is None:
            return True
        else:
            return False        # TODO: invoke the nonzero method

    def as_pyval(self):
        fatal("can't call as_pyval on instance value")

    def get_attr(self, name):
        try:
            val = self.env.lookup(name)
            return val
        except EnvLookupError:
            return self.cls.get_attr(name)

######################################################################
#          file value
######################################################################
class FileValue(Value):
    def __init__(self, fname, flag):
        pass
