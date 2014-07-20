#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
interpreter for python
"""
from util import *
from environment import *
from values import *
from buildin import built_in_env

class Cont(object):
    pass
cont = Cont()

def bind(target, val, env):
    if IS(target, ast.Name) or IS(target, str):
        return env.put_or_update(get_id(target), val)
    # for assign statement.
    elif IS(target, ast.Tuple) or IS(target, ast.Tuple):
        if IS(val, ListValue) or IS(val, TupleValue):
            if len(target.elts) == len(val):
                for i in xrange(len(val)):
                    bind(target.elts[i], val[i], env)
            elif len(target.elts) > len(val):
                msg = "too few values to unpack."
                raise EnvBindError(msg)
            else:
                msg = "too many values to unpack"
                raise EnvBindError(msg)
    elif IS(target, ast.Subscript):
        tgt = value_of_exp(target.value, env)
        if IS(tgt, ListValue):
            pass
        elif IS(tgt, DictValue):
            if IS(target.slice, ast.Index):
                idx = pyval_of_exp(target.slice.value)
                tgt.setitem(idx, val)
            else:
                fatal("assigning to dict only supports index keys")
        elif IS(tgt, InstanceValue):
            pass
        else:
            fatal("TypeError: assign to a subscript exp")
    elif IS(target, ast.Attribute):
        tgt = value_of_exp(target.value, env)
        if IS(tgt, InstanceValue):
            pass
        elif IS(tgt, ClassValue):
            pass
        else:
            fatal("TypeError: assign to an attribute exp")
    else:
        raise EnvBindError("error type arguments.")

def apply_closure(clo, posargs, keywords=None,):
    new_env = Env(clo.env)
    if len(posargs) > len(clo.posargs) and clo.vararg is None:
        fatal("too many arguments")

    # TODO: better implemention
    if (clo.kwarg is None) and (dict_sub(keywords, dict.fromkeys(clo.posargs))):
        fatal("too many keyword arguments")

    for var, val in zip(clo.posargs, posargs[:len(clo.posargs)]):
        new_env.put(get_id(var), val)
    for var, val in keywords.items():
        if var in clo.posargs:
            if new_env.lookup_local(var) is None:
                new_env.put(var, val)
            else:
                fatal("already bind in env")
    if clo.vararg is not None:
        new_env.put(clo.vararg, ListValue(posargs[len(clo.posargs):]))
    if clo.kwarg is not None:
        new_env.put(clo.kwarg, kwargs)

    # TODO: maybe need to creat a new enviroment
    # new_env = Env(new_env)
    return value_of_stmts(clo.body, new_env)

# and, or
def apply_boolop_exp(exp, env):
    def value_and(*exps):
        ret = True
        for exp in exps:
            val = value_of_exp(exp, env)
            if bool(val) is False:
                ret = False
                break
        return BoolValue(ret)
    def value_or(*exps):
        ret = False
        for exp in exps:
            val = value_of_exp(exp, env)
            if bool(val) is True:
                ret = True
                break
        return BoolValue(ret)

    op = exp.op
    if IS(op, ast.And):
        return value_and(*exp.values)
    elif IS(op, ast.Or):
        return value_or(*exp.values)
    else:
        print "unkown bool operator"

# binary operator: +, -, *, /
#TODO: support list add and class operators
def apply_binop_exp(exp, env):
    l_val = value_of_exp(exp.left, env)
    r_val = value_of_exp(exp.right, env)
    op = exp.op
    if IS(op, ast.Add):
        return l_val.add(r_val)
    elif IS(op, ast.Sub):
        return l_val.sub(r_val)
    elif IS(op, ast.Mult):
        return l_val.mul(r_val)
    elif IS(op, ast.Div):
        return l_val.div(r_val)
    else:
        fatal('unkown binary operator.')


# unary operator: not
def apply_unaryop_exp(exp, env):
    op = exp.op
    rand = pyval_of_exp(exp.operand, env)
    if IS(op, ast.Not):
        return BoolValue(not rand)
    elif IS(op, ast.Invert):
        pass
    elif IS(op, ast.UAdd):
        pass
    elif IS(op, ast.USub):
        pass
    else:
        print "unkown UnaryOp type(%s)" % op
        raise


# compare Operator: ==, !=, <, <=, >, >=,is, is not, in, not in
def apply_comop_exp(exp, env):
    def apply_a_comop(rand1, op, rand2):
        if IS(op, ast.Eq):
            return rand1 == rand2
        elif IS(op, ast.NotEq):
            return rand1 != rand2
        elif IS(op, ast.Lt):
            return rand1 < rand2
        elif IS(op, ast.LtE):
            return rand1 <= rand2
        elif IS(op, ast.Gt):
            return rand1 > rand2
        elif IS(op, ast.GtE):
            return rand1 >= rand2
        elif IS(op, ast.Is):
            return rand1 is rand2
        elif IS(op, ast.IsNot):
            return rand1 is not rand2
        elif IS(op, ast.In):
            return rand1 in rand2
        elif IS(op, ast.NotIn):
            return rand1 not in rand2
    left = pyval_of_exp(exp.left, env)
    ops = exp.ops
    rest_rands = map(lambda e: pyval_of_exp(e, env), exp.comparators)
    ret = foldl(apply_a_comop, left, ops, rest_rands)
    return BoolValue(ret)


def pyval_of_exp(exp, env):
    if exp is None:
        return None
    val = value_of_exp(exp, env)
    return val.as_pyval()

def value_of_exp(exp, env):
    if IS(exp, ast.BoolOp):
        return apply_boolop_exp(exp, env)
    elif IS(exp, ast.BinOp):
        return apply_binop_exp(exp, env)
    elif IS(exp, ast.UnaryOp):
        return apply_unaryop_exp(exp, env)
    elif IS(exp, ast.Lambda):
        return LambdaValue(exp, env)
    elif IS(exp, ast.IfExp):
        t_val = pyval_of_exp(exp.test, env)
        if t_val:
            return value_of_exp(exp.body, env)
        else:
            return value_of_exp(exp.orelse, env)
    elif IS(exp, ast.Dict):
        # keys need be python value
        keys = map(lambda e: pyval_of_exp(e, env), exp.keys)
        values = map(lambda e: value_of_exp(e, env), exp.values)
        return DictValue(zip(keys, values))
    elif IS(exp, ast.Set):
        elts = map(lambda e: pyval_of_exp(e, env), exp.elts)
        return SetValue(elts)
    elif IS(exp, ast.ListComp):
        pass
    elif IS(exp, ast.SetComp):
        pass
    elif IS(exp, ast.DictComp):
        pass
    elif IS(exp, ast.GeneratorExp):
        pass
    elif IS(exp, ast.Yield):
        pass
    elif IS(exp, ast.Compare):
        return apply_comop_exp(exp, env)
    elif IS(exp, ast.Call):
        func = value_of_exp(exp.func, env)
        args = map(lambda e: value_of_exp(e, env), exp.args)
        keywords = {}
        for var, val in exp.keywords:
            keywords[var] = value_of_exp(val, env)
        starargs = None
        if exp.starargs is not None:
            starargs = value_of_exp(exp.starargs, env)
        kwargs = None
        if exp.kwargs is not None:
            kwargs = value_of_exp(exp.kwargs, env)

        # merger positional arguments
        if IS(starargs, ListValue) or IS(starargs, TupleValue) or\
           IS(starargs, SetValue):
            args += list(starargs.value)
        # merger keyword arguments
        if IS(kwargs, DictValue):
            for var, val in kwargs.as_pyval():
                if var in keywords:
                    fatal("keywords have same keys")
                keywords[var] = val

        if IS(func, ClassValue):
            constructor = func.get_attr("__init__")
            # bind self
            inst = InstanceValue(func, func.env)
            args = [inst] + args
            return apply_closure(constructor, args, keywords)
        elif IS(func, LambdaValue):
            return apply_closure(func, args, keywords)
        elif IS(func, FunValue):
            return apply_closure(func, args, keywords)
        elif IS(func, MethodValue):
            # get the instance, exp.func must be a Attribute Node
            inst = value_of_exp(exp.func.value, env)
            args = [inst] + args
            return apply_closure(func, args, keywords)
        elif IS(func, InstanceValue):  # a instance has __call__ method
            call = func.get_attr("__call__")
            if call is None:
                fatal("this instance don't support call")
            else:
                args = [func] + args
                return apply_closure(call, args, keywords)
        elif IS(func, PrimFunValue):
            return func.fun(*args)
        else:
            fatal("unkown function type")

    elif IS(exp, ast.Repr):
        pass
    elif IS(exp, ast.Num):
        if type(exp.n) == int:
            return IntValue(exp.n)
        elif type(exp.n) == float:
            return floatValue(exp.n)
        else:
            fatal("unkown number value")
    elif IS(exp, ast.Str):
        return StrValue(exp.s)
    elif IS(exp, ast.Attribute):
        val = value_of_exp(exp.value, env)
        if IS(val, ClassValue):
            return val.get_attr(exp.attr)
        elif IS(val, InstanceValue):
            return val.get_attr(exp.attr)
        else:
            print "unkown attribute value."
        # TODO:
    elif IS(exp, ast.Subscript):
        val = value_of_exp(exp.value, env)
        if IS(exp.slice, ast.Index):
            idx = pyval_of_exp(exp.slice.value, env)
            if IS(val, ListValue) or IS(val, TupleValue):
                return val.getitem(idx)
            elif IS(val, InstanceValue):
                getitem = val.get_attr("__getitem__")
                if getitem is None:
                    fatal("this class don't support get slice")
                else:
                    args = [val] + args
                    return apply_closure(getitem, args)
        elif IS(exp.slice, ast.Slice):
            lower = pyval_of_exp(exp.slice.lower, env)
            upper = pyval_of_exp(exp.slice.upper, env)
            step = pyval_of_exp(exp.slice.step, env)
            if IS(val, ListValue) or IS(val, TupleValue):
                val.getslice(lower, upper, step)
            elif IS(val, InstanceValue):
                getslice = val.get_attr("__getslice__")
                if getslice is None:
                    fatal("this class don't support get slice")
                else:
                    args = [val] + args
                    return apply_closure(getslice, args)

        elif IS(exp.slice, ast.Ellipsis):
            pass
        else:
            pass
        if IS(val, ListValue) or IS(val, TupleValue):
            return val[idx]
        else:
            print "only list and tuple support subscript expression."
            raise

    elif IS(exp, ast.Name):
        if exp.id in global_names:  # a global name
            env1 = module_env
        else:
            env1 = env
        try:
            val = env1.lookup(exp.id)
            return val
        except EnvLookupError, e:
            fatal("value_of_exp", e.msg)

    elif IS(exp, ast.List):
        vals = map(lambda e: value_of_exp(e, env), exp.elts)
        return ListValue(vals)
    elif IS(exp, ast.Tuple):
        vals = map(lambda e: value_of_exp(e, env), exp.elts)
        return TupleValue(vals)
    else:
        print "unkown exp type(%s)." % str(exp)
        raise


def value_of_stmts(stmts, env):
    if stmts == []:
        return cont  # return without find a return statement
    stmt = stmts[0]
    rest_stmts = stmts[1:]
    if IS(stmt, ast.FunctionDef):
        if IS(env, ClassEnv):   # a class method
            clo = MethodValue(stmt, env)
        else:                   # a normal function
            clo = FunValue(stmt, env)
        env.put(stmt.name, clo)
        return value_of_stmts(rest_stmts, env)
    elif IS(stmt, ast.ClassDef):  # OOP
        cls_name = stmt.name
        cls_bases = map(lambda e: value_of_exp(e, env), stmt.bases)
        body = stmt.body
        cls_val = ClassValue(cls_name, cls_bases)
        # evalute the body of class
        # first bind the class name

        new_env = ClassEnv(env)
        new_env.put(cls_name, cls_val)
        val = value_of_stmts(body, new_env)
        cls_val.env.set_table(new_env.table)

        env.put(cls_name, cls_val)
        return value_of_stmts(rest_stmts, env)
    elif IS(stmt, ast.Return):
        if stmt.value is None:
            return None
        else:
            return value_of_exp(stmt.value, env)
    elif IS(stmt, ast.Assign):
        for e in stmt.targets:
            val = value_of_exp(stmt.value, env)
            bind(e, val, env)
        return value_of_stmts(rest_stmts, env)
    elif IS(stmt, ast.AugAssign):   # a = a op b
        pass

    elif IS(stmt, ast.Print):
        val_lst = map(lambda e: value_of_exp(e, env), stmt.values)
        if stmt.dest:
            dest = value_of_exp(stmt.dest, env)
            print dest % tuple(val_lst)
            return value_of_stmts(rest_stmts, env)
        else:
            for val in val_lst:
                print val,
            print               # newline
            return value_of_stmts(rest_stmts, env)
    elif IS(stmt, ast.For):
        pass
    elif IS(stmt, ast.While):
        test = pyval_of_exp(stmt.test, env)
        while test:
            val = value_of_stmts(stmt.body, env)
            if val == "break":
                return value_of_stmts(rest_stmts, env)
            elif val == "continue" or val == cont:
                test = pyval_of_exp(stmt.test, env)
            else:               # find a return statement.
                return val
        # when the loop exits normally, we need run the else block
        if stmt.orelse is None:
            return value_of_stmts(rest_stmts, env)
        else:
            val = value_of_stmts(stmt.orelse, env)
            if val == cont:
                return value_of_stmts(rest_stmts, env)
            else:                   # find a return statement
                return val

    elif IS(stmt, ast.If):
        test_val = pyval_of_exp(stmt.test, env)
        if test_val:
            val = value_of_stmts(stmt.body, env)
        else:
            val = value_of_stmts(stmt.orelse, env)
        if val == cont:  # without return statement
            return value_of_stmts(rest_stmts, env)
        else:            # find a return statement, just return the value
            return val   # and ignore the rest statements
    elif IS(stmt, ast.With):
        pass
    elif IS(stmt, ast.Raise):
        pass
    elif IS(stmt, ast.TryExcept):
        pass
    elif IS(stmt, ast.TryFinally):
        pass
    elif IS(stmt, ast.Assert):
        pass
    elif IS(stmt, ast.Import):
        pass
    elif IS(stmt, ast.ImportFrom):
        pass
    elif IS(stmt, ast.Exec):
        pass
    elif IS(stmt, ast.Global):
        for name in stmt.names:
            global_names.add(name)
    elif IS(stmt, ast.Expr):
        val = value_of_exp(stmt.value, env)
        return value_of_stmts(rest_stmts, env)
    elif IS(stmt, ast.Break):
        return "break"
    elif IS(stmt, ast.Continue):
        return "continue"
    elif IS(stmt, ast.Pass):
        return value_of_stmts(rest_stmts, env)
    else:
        print "unkown statement type."

module_env = None
global_names = None

def value_of_mod(fname, mod):
    global module_env, global_names
    val = ModuleValue(fname, fname, built_in_env)
    module_env = val.env
    global_names = set()
    if IS(mod, ast.Module):
        value_of_stmts(mod.body, module_env)
        return val
    elif IS(mod, ast.Interactive):
        pass
    elif IS(mod, ast.Expression):
        pass
    else:
        print "error: unkown MOD type."


def eval_file(fname):
    node = parse_file(fname)
    val = value_of_mod(fname, node)
    print "-------------final value----------------------"
    print val
    print "----------------------------------------------"


def eval_string(s):
    node = parse_str(s)
    return value_of_mod(node, init_env())


if __name__ == '__main__':
    # eval_file("test/1.py")
    eval_file("test/2.py")
