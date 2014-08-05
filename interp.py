#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
interpreter for python
"""
import os
import os.path

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
            constructor = func.getattr("__init__")
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
            call = func.getattr("__call__")
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
            return val.getattr(exp.attr)
        elif IS(val, InstanceValue):
            return val.getattr(exp.attr)
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
                getitem = val.getattr("__getitem__")
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
                getslice = val.getattr("__getslice__")
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
        # if exp.id in global_names:  # a global name
        #     env1 = module_env
        if interp.cur_mod.is_global(exp.id):
            env1 = interp.cur_mod.env
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
        for a in stmt.names:
            mod = interp.load_module(a.name)
            if a.asname is not None:
                env.put_or_update(a.asname, mod)
            else:
                # get the first segement of module name
                local_name = a.name.partition(".")[0]
                env.put_or_update(local_name, mod)
    # level: 0 is absolute import, 1 is current directory,
    # 2 is parent directory
    elif IS(stmt, ast.ImportFrom):
        mod = interp.load_module(stmt.module, stmt.level)
        if IS(mod, PackageValue):     # a package
            for a in stmt.names:
                val = mod.getattr(a.name)
                if val is None:
                    pass

                if a.asname is None:
                    env.put_or_update(a.name, val)
                else:
                    env.put_or_update(a.asname, val)
        else:                   # a regular moudle
            for a in stmt.names:
                val = mod.getattr(a.name)
                if val is None:
                    fatal("this module don't have the attribute")
                if a.asname is None:
                    env.put_or_update(a.name, val)
                else:
                    env.put_or_update(a.asname, val)
    elif IS(stmt, ast.Exec):
        pass
    elif IS(stmt, ast.Global):
        for name in stmt.names:
            # global_names.add(name)
            interp.cur_mod.add_global(name)
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

def value_of_mod(fname, node):
    global module_env, global_names
    val = ModuleValue(fname, fname, built_in_env)
    module_env = val.env
    global_names = set()
    if IS(node, ast.Module):
        value_of_stmts(node.body, module_env)
        return val
    elif IS(node, ast.Interactive):
        pass
    elif IS(node, ast.Expression):
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


class Interpreter(object):
    def __init__(self):
        self.main_mod = None
        self.cur_mod = None
        self.import_stk = []                # detect the import cycle
        self.mod_cache = {}
        self.root_dir = None    # main directory of the software

    def start(self, fname):
        """
        the entry point of the interpreter
        """
        node = parse_file(fname)
        val = ModuleValue(fname, "__main__", built_in_env)
        self.cur_mod = val
        self.main_mod = val
        self.import_stk.append(fname)
        self.mod_cache[fname] = val
        self.root_dir = os.path.dirname(fname)

        if IS(node, ast.Module):
            value_of_stmts(node.body, self.cur_mod.env)
            return val
        else:
            fatal("error: unkown MOD type.")

        print "-------------final value----------------------"
        print val
        print "----------------------------------------------"

    def load_file(self, fname):
        relpath = os.path.relpath(fname, self.root_dir)
        mod_name = relpath.replace(os.sep, ".")
        if os.path.isdir(fname):   # package
            fname = os.path.join(fname, "__init__.py")

        if fname in self.import_stk:    # import cycle
            fatal("error: import cycle.")
        self.import_stk.append(fname)

        if fname in self.mod_cache:    # already in cache
            return self.mod_cache[fname]

        node = parse_file(fname)
        if os.path.basename(fname) == "__init__.py":  # a package
            val = PackageValue(fname, mod_name, built_in_env)
        else:                   # a module
            val = ModuleValue(fname, mod_name, built_in_env)

        prev = self.cur_mod
        self.cur_mod = val

        if IS(node, ast.Module):
            value_of_stmts(node.body, val.env)
        else:
            fatal("error: unkown MOD type.")
        self.cur_mod = prev     # restore the current module
        return val

    def load_module(self, name, level=0):
        '''
        load a module and return the module value
        '''
        if levle == 0:
            start_dir = self.root_dir
        elif level > 0:
            start_dir = self.cur_mod.fname
            for i in range(level):
                start_dir = os.path.dirname(start_dir)
        else:
            fatal("level must be a positive integer")
        name_segs = name.split(".")
        prev = None
        fname = start_dir
        for n in name_segs:
            fname = os.path.join(fname, n)
            mod_val = self.load_file(fname)
            if prev is not None:
                prev.env.put(n, mod_val)
            prev = mod_val
        return prev


if __name__ == '__main__':
    # eval_file("test/1.py")
    # eval_file("test/2.py")
    interp = Interpreter()
    interp.start("test/2.py")
