#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
build-in functions, classes and modules, actually we should implement all
the names in __builtin__, you can see these names with the following code:

import __builtin__
dir(__builtin__)
"""
from environment import Env
from values import *
from util import *
# from values import (PrimFunValue, BoolValue, NoneValue,
#                     ClassValue)

def int_fun(x, base=10):
    if isinstance(x, StrValue) or isinstance(x, NumValue):
        return IntValue(int(x.value, base))
    else:
        fatal("TypeError: int() argument must be a string or a number.")

def bool_fun(x=False):
    return BoolValue(bool(x))

def str_fun(obj=""):
    return StrValue(str(obj))

def list_fun(arg):
    if IS(arg, SeqValue) or IS(arg, DictValue) or IS(arg, SetValue):
        return ListValue(arg.value)
    elif IS(arg, InstanceValue):
        pass
    else:
        pass
    raise

def tuple_fun(arg):
    if IS(arg, SeqValue) or IS(arg, DictValue) or IS(arg, SetValue):
        return TupleValue(arg.value)
    elif IS(arg, InstanceValue):
        pass
    else:
        pass
    raise

def dict_fun(iterable=None, **kwarg):
    if iterable is None:
        return DictValue(dict(**kwarg))
    else:
        return DictValue(dict(iterable, **kwarg))

built_in_env = Env(None, {
    "abs"              : PrimFunValue(abs),
    "all"              : PrimFunValue(all),
    "any"              : PrimFunValue(any),
    "apply"            : PrimFunValue(apply),
    "basestring"       : PrimFunValue(basestring),
    "bin"              : PrimFunValue(bin),
    "bool"             : PrimFunValue(bool_fun),
    "buffer"           : PrimFunValue(buffer),
    "bytearray"        : PrimFunValue(bytearray),
    "bytes"            : PrimFunValue(bytes),
    "callable"         : PrimFunValue(callable),
    "chr"              : PrimFunValue(chr),
    "classmethod"      : PrimFunValue(classmethod),
    "cmp"              : PrimFunValue(cmp),
    "coerce"           : PrimFunValue(coerce),
    "compile"          : PrimFunValue(compile),
    "complex"          : PrimFunValue(complex),
    "delattr"          : PrimFunValue(delattr),
    "dict"             : PrimFunValue(dict),
    "dir"              : PrimFunValue(dir),
    "divmod"           : PrimFunValue(divmod),
    "enumerate"        : PrimFunValue(enumerate),
    "eval"             : PrimFunValue(eval),
    "execfile"         : PrimFunValue(execfile),
    "file"             : PrimFunValue(file),
    "filter"           : PrimFunValue(filter),
    "float"            : PrimFunValue(float),
    "format"           : PrimFunValue(format),
    "frozenset"        : PrimFunValue(frozenset),
    "getattr"          : PrimFunValue(getattr),
    "globals"          : PrimFunValue(globals),
    "hasattr"          : PrimFunValue(hasattr),
    "hash"             : PrimFunValue(hash),
    "help"             : PrimFunValue(help),
    "hex"              : PrimFunValue(hex),
    "id"               : PrimFunValue(id),
    "input"            : PrimFunValue(input),
    "int"              : PrimFunValue(int_fun),
    "intern"           : PrimFunValue(intern),
    "isinstance"       : PrimFunValue(isinstance),
    "issubclass"       : PrimFunValue(issubclass),
    "iter"             : PrimFunValue(iter),
    "len"              : PrimFunValue(len),
    "list"             : PrimFunValue(list_fun),
    "locals"           : PrimFunValue(locals),
    "long"             : PrimFunValue(long),
    "map"              : PrimFunValue(map),
    "max"              : PrimFunValue(max),
    "memoryview"       : PrimFunValue(memoryview),
    "min"              : PrimFunValue(min),
    "next"             : PrimFunValue(next),
    "object"           : PrimFunValue(object),
    "oct"              : PrimFunValue(oct),
    "open"             : PrimFunValue(open),
    "ord"              : PrimFunValue(ord),
    "pow"              : PrimFunValue(pow),
    "property"         : PrimFunValue(property),
    "range"            : PrimFunValue(range),
    "raw_input"        : PrimFunValue(raw_input),
    "reduce"           : PrimFunValue(reduce),
    "reload"           : PrimFunValue(reload),
    "repr"             : PrimFunValue(repr),
    "reversed"         : PrimFunValue(reversed),
    "round"            : PrimFunValue(round),
    "set"              : PrimFunValue(set),
    "setattr"          : PrimFunValue(setattr),
    "slice"            : PrimFunValue(slice),
    "sorted"           : PrimFunValue(sorted),
    "staticmethod"     : PrimFunValue(staticmethod),
    "str"              : PrimFunValue(str_fun),
    "sum"              : PrimFunValue(sum),
    "super"            : PrimFunValue(super),
    "tuple"            : PrimFunValue(tuple_fun),
    "type"             : PrimFunValue(type),
    "unichr"           : PrimFunValue(unichr),
    "unicode"          : PrimFunValue(unicode),
    "vars"             : PrimFunValue(vars),
    "xrange"           : PrimFunValue(xrange),
    "zip"              : PrimFunValue(zip),

    # keywords
    "True"             : BoolValue(True),
    "False"            : BoolValue(False),
    "None"             : NoneValue(),
    # classes
    "object"           : ClassValue("object")
})
