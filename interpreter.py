#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
interpreter for python
"""
import ast
import os
import os.path

from util import *
from environment import *
from values import *
from builtin import built_in_env


def bind(target, val, env):
    if IS(target, ast.Name) or IS(target, str):
        name = get_id(target)
        local_val = env.lookup_local(name)
        if local_val is None:
            env.put(name, val)
        elif local_val == "global":
            g_env = env.find_global_env()
            if g_env is None:
                fatal("can't find global scope.")
            else:
                g_env.put_or_update(name, val)
        else:
            env.update(name, val)
    elif IS(target, ast.Tuple) or IS(target, ast.Tuple):
        if IS(val, ListValue) or IS(val, TupleValue):
            if len(target.elts) == val.pylen():
                for i in xrange(val.pylen()):
                    bind(target.elts[i], val.value[i], env)
            elif len(target.elts) > len(val):
                fatal("too few values to unpack.")
            else:
                fatal("too many values to unpack")
    elif IS(target, ast.Subscript):
        tgt = value_of_exp(target.value, env)
        if IS(tgt, ListValue):
            if IS(target.slice, ast.Index):
                idx = value_of_exp(target.slice.value)
                tgt.setitem(idx, val)
            elif IS(target.slice, ast.Slice):
                pass
        elif IS(tgt, DictValue):
            if IS(target.slice, ast.Index):
                idx = value_of_exp(target.slice.value)
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
            tgt.env.put_or_update(target.attr, val)
        elif IS(tgt, ClassValue):
            tgt.env.put_or_update(target.attr, val)
        else:
            fatal("TypeError: assign to an attribute exp")
    else:
        raise EnvBindError("error type arguments.")

def apply_closure(clo, posargs, keywords=None):
    new_env = clo.bind_args(posargs, keywords)
    # TODO: maybe need to creat a new enviroment
    # new_env = Env(new_env)
    ret = value_of_stmts(clo.body, new_env)
    if ret == "no-return":
        return none
    else:
        return ret


class ExpEvaluator(object):
    """
    evaluator of expression
    """
    def __init__(self):
        pass

    def dispatch(self, exp, env):
        "Dispatcher function, dispatching exp type T to method _T."
        if not IS(exp, ast.expr):
            fatal("%s not a expression node" % exp)
        meth = getattr(self, "_"+exp.__class__.__name__)
        return meth(exp, env)

    def _BoolOp(self, exp, env):
        """boolean expression"""
        def value_and(*exps):
            for exp in exps:
                val = self.dispatch(exp, env)
                if val.pybool() is False:
                    return false
            return true

        def value_or(*exps):
            for exp in exps:
                val = self.dispatch(exp, env)
                if val.pybool() is True:
                    return false
            return true

        op = exp.op
        if IS(op, ast.And):
            return value_and(*exp.values)
        elif IS(op, ast.Or):
            return value_or(*exp.values)
        else:
            fatal("unkown bool operator")

    def _BinOp(self, exp, env):
        l_val = self.dispatch(exp.left, env)
        r_val = self.dispatch(exp.right, env)
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
            fatal('unkown binary operator %s' % op)

    def _UnaryOp(self, exp, env):
        op = exp.op
        rand = self.dispatch(exp.operand, env)
        if IS(op, ast.Not):
            return BoolValue(not rand.pybool())
        elif IS(op, ast.Invert):
            pass
        elif IS(op, ast.UAdd):
            pass
        elif IS(op, ast.USub):
            pass
        else:
            fatal("unkown UnaryOp type(%s)" % op)

    def _Compare(self, exp, env):
        def apply_a_comop(left, op, right):
            rand1 = self.dispatch(left, env)
            rand2 = self.dispatch(right, env)

            if IS(op, ast.Eq):
                return rand1.eq(rand2)
            elif IS(op, ast.NotEq):
                return rand1.neq(rand2)
            elif IS(op, ast.Lt):
                return rand1.lt(rand2)
            elif IS(op, ast.LtE):
                return rand1.lte(rand2)
            elif IS(op, ast.Gt):
                return rand1.gt(rand2)
            elif IS(op, ast.GtE):
                return rand1.gte(rand2)
            # Not Implemented
            elif IS(op, ast.Is):
                return rand2.contains(rand1)
            elif IS(op, ast.IsNot):
                return rand1 is not rand2
            elif IS(op, ast.In):
                return rand1.contains(rand2)
            elif IS(op, ast.NotIn):
                ret = rand1.contains(rand2)
                return BoolValue(not ret.pybool())
        left = exp.left
        ops = exp.ops
        rest_rands = exp.comparators
        for op, right in zip(ops, rest_rands):
            ret = apply_a_comop(left, op, right)
            if ret.pybool() is False:
                return BoolValue(False)
            left = right
        return BoolValue(True)

    def _Lambda(self, exp, env):
        return LambdaValue(exp, env)

    def _IfExp(self, exp, env):
        t_val = self.dispatch(exp.test, env)
        if t_val.pybool():
            return self.dispatch(exp.body, env)
        else:
            return self.dispatch(exp.orelse, env)

    def _Dict(self, exp, env):
        keys = map(lambda e: self.dispatch(e, env), exp.keys)
        values = map(lambda e: self.dispatch(e, env), exp.values)
        return DictValue(zip(keys, values))

    def _Set(self, exp, env):
        elts = map(lambda e: self.dispatch(e, env), exp.elts)
        return SetValue(elts)

    def _List(self, exp, env):
        vals = map(lambda e: self.dispatch(e, env), exp.elts)
        return ListValue(vals)

    def _Tuple(self, exp, env):
        vals = map(lambda e: self.dispatch(e, env), exp.elts)
        return TupleValue(vals)

    def _Call(self, exp, env):
        call_stk.append_cur_node()

        func = self.dispatch(exp.func, env)
        args = map(lambda e: self.dispatch(e, env), exp.args)
        keywords = {}
        for var, val in exp.keywords:
            keywords[var] = self.dispatch(val, env)
        starargs = ListValue([])
        if exp.starargs is not None:
            starargs = self.dispatch(exp.starargs, env)
        kwargs = DictValue({})
        if exp.kwargs is not None:
            kwargs = self.dispatch(exp.kwargs, env)

        # merger positional arguments
        if IS(starargs, ListValue) or IS(starargs, TupleValue) or\
           IS(starargs, SetValue):
            args += list(starargs.value)
        else:
            fatal("argument after * must be a sequence.")
        # merger keyword arguments
        if IS(kwargs, DictValue):
            for var, val in kwargs.as_pyval():
                if not IS(var, StrValue):
                    fatal("not a name.")
                var = var.value
                if var in keywords:
                    fatal("keywords have same keys")
                keywords[var] = val
        else:
            fatal("argument after ** must be a dict.")

        if IS(func, ClassValue):
            constructor = func.getattr("__init__")
            # bind self
            inst = InstanceValue(func)
            args = [inst] + args
            constructor.apply(args, keywords)
            ret = inst         # we should return the instance
        elif IS(func, LambdaValue):
            ret = func.apply(args, keywords)
        elif IS(func, FunValue):
            ret = func.apply(args, keywords)
        elif IS(func, MethodValue):
            # get the instance, exp.func must be a Attribute Node
            if not IS(exp.func, ast.Attribute):
                fatal("Not a attribute node.")
            inst = self.dispatch(exp.func.value, env)
            args = [inst] + args
            ret = func.apply(args, keywords)
        elif IS(func, InstanceValue):  # a instance has __call__ method
            call = func.getattr("__call__")
            if call is None:
                fatal("this instance don't support call")
            else:
                args = [func] + args
                ret = call.apply(args, keywords)
        elif IS(func, PrimFunValue):
            ret = func.apply(args, keywords)
        else:
            fatal("unkown function type")
        call_stk.pop()
        return ret

    def _Num(self, exp, env):
        if type(exp.n) == int:
            return IntValue(exp.n)
        elif type(exp.n) == float:
            return floatValue(exp.n)
        else:
            fatal("unkown number value")

    def _Str(self, exp, env):
        return StrValue(exp.s)

    def _Attribute(self, exp, env):
        val = self.dispatch(exp.value, env)
        if IS(val, ClassValue) or IS(val, InstanceValue) or \
           IS(val, ModuleValue):
            return val.getattr(exp.attr)
        else:
            fatal("unkown attribute value.")

    def _Subscript(self, exp, env):
        # TODO: better implemention
        val = self.dispatch(exp.value, env)
        if IS(exp.slice, ast.Index):
            idx = self.dispatch(exp.slice.value, env)
            if IS(val, SeqValue) or IS(val, DictValue):
                return val.getitem(idx)
            elif IS(val, InstanceValue):
                getitem = val.getattr("__getitem__")
                if getitem is None:
                    fatal("this instance don't support get item.")
                else:
                    args = [val, idx]
                    return getitem.apply(args)
        elif IS(exp.slice, ast.Slice):
            if exp.slice.lower is None:
                lower = none
            else:
                lower = self.dispatch(exp.slice.lower, env)
            if exp.slice.upper is None:
                upper = none
            else:
                upper = self.dispatch(exp.slice.upper, env)
            if exp.slice.step is None:
                step = none
            else:
                step = self.dispatch(exp.slice.step, env)
            if IS(val, ListValue) or IS(val, TupleValue):
                return val.getslice(lower, upper, step)
            elif IS(val, InstanceValue):
                getslice = val.getattr("__getslice__")
                if getslice is None:
                    fatal("this class don't support get slice")
                else:
                    args = [val, upper, lower, step]
                    return getslice.apply(args)

        elif IS(exp.slice, ast.Ellipsis):
            pass
        else:
            pass

    def _Name(self, exp, env):
        try:
            val = env.lookup(exp.id)
            if val == "global":    # a global value
                env1 = env.find_global_env()
                return env1.lookup(exp.id)
            else:
                return val
        except EnvLookupError, e:
            fatal(e.msg)


    def _ListComp(self, exp, env):
        pass

    def _SetComp(self, exp, env):
        pass

    def _DictComp(self, exp, env):
        pass

    def _GeneratorExp(self, exp, env):
        pass

    def _Yield(self, exp, env):
        pass


class BlockEvaluator(object):
    """
    evaluator of statements:
    self.eval evaluates all the statements in a block, it will rerurn the
              following values:
              1. no-return: this block doesn't contain return statement
              2. break: find a break statement
              3. continue: find a continue statement
              4. a Value instance: find a return statement
    self.dispatch evaluates only one statement, it will return following
              values:
              1. cont: continue evaluate the rest statements
              2. a Value instance: means current statement is a return
                 tatement
    """
    def __init__(self):
        pass

    def eval(self, stmts, env):
        for stmt in stmts:
            # print interp.cur_mod
            # print interp
            call_stk.set_cur_node(stmt, interp.cur_mod.fname)

            ret = self.dispatch(stmt, env)
            if ret == "cont":
                continue
            elif IS(ret, Value):
                return ret
            else:
                return ret

        return "no-return"

    def dispatch(self, stmt, env):
        "Dispatcher function, dispatching statement type T to method _T."
        if not IS(stmt, ast.stmt):
            fatal("not a statement node")
        meth = getattr(self, "_"+stmt.__class__.__name__)
        return meth(stmt, env)

    def _FunctionDef(self, stmt, env):
        if IS(env, ClassEnv):   # a class method
            clo = MethodValue(stmt, env)
        else:                   # a normal function
            clo = FunValue(stmt, env)
        env.put(stmt.name, clo)
        return "cont"

    def _ClassDef(self, stmt, env):
        cls_name = stmt.name
        cls_bases = map(lambda e: value_of_exp(e, env), stmt.bases)
        body = stmt.body
        cls_val = ClassValue(cls_name, cls_bases)
        # create new enviroment and evaluate the class body.
        new_env = ClassEnv(env)
        # set the __doc__ attribute
        doc_val = ast.get_docstring(stmt)
        if doc_val is None:
            doc_val = none
        else:
            doc_val = StrValue(doc_val)
        cls_val.set_doc(doc_val)

        self.eval(body, new_env)
        cls_val.set_env(new_env)

        env.put(cls_name, cls_val)
        return "cont"

    def _Return(self, stmt, env):
        if not IS(env, LocalEnv):
            fatal("SyntaxError: return is not in a function")

        if stmt.value is None:
            return none
        else:
            return value_of_exp(stmt.value, env)

    def _Assign(self, stmt, env):
        for e in stmt.targets:
            val = value_of_exp(stmt.value, env)
            bind(e, val, env)
        return "cont"

    def _AugAssign(self, stmt, env):   # a = a op b
        # first create a BinOp node for 'a op b'
        node = ast.BinOp(stmt.target, stmt.op, stmt.value)
        val = value_of_exp(node, env)
        bind(stmt.target, val, env)
        return "cont"

    def _Print(self, stmt, env):
        val_lst = map(lambda e: value_of_exp(e, env), stmt.values)
        if stmt.dest:
            dest = value_of_exp(stmt.dest, env)
            print dest % tuple(val_lst)
        else:
            for val in val_lst:
                print val,
            print               # newline
        return "cont"

    def _For(self, stmt, env):
        #TODO: navie implemention
        obj = value_of_exp(stmt.iter, env)
        if IS(obj, SeqValue) or IS(obj, DictValue) or IS(obj, SetValue):
            for val in obj.value:
                bind(stmt.target, val, env)
                ret = self.eval(stmt.body, env)
                if ret == "break":
                    return "cont"
                elif ret == "continue" or ret == "no-return":
                    continue
                else:
                    return ret

            if stmt.orelse is None:
                return "cont"
            else:
                val = self.eval(stmt.orelse, env)
                if val == "no-return":
                    return "cont"
                else:                   # find a return statement
                    return val

    def _While(self, stmt, env):
        t_val = value_of_exp(stmt.test, env)
        while t_val.pybool():
            val = self.eval(stmt.body, env)
            if val == "break":
                return "cont"
            elif val == "continue" or val == "no-return":
                t_val = value_of_exp(stmt.test, env)
            else:               # find a return statement.
                return val
        # when the loop exits normally, we need run the else block
        if stmt.orelse is None:
            return "cont"
        else:
            val = self.eval(stmt.orelse, env)
            if val == "no-return":
                return "cont"
            else:                   # find a return statement
                return val

    def _If(self, stmt, env):
        t_val = value_of_exp(stmt.test, env)
        if t_val.pybool():
            val = self.eval(stmt.body, env)
        else:
            val = self.eval(stmt.orelse, env)
        if val == "no-return":  # without return statement
            return "cont"
        else:            # find a return statement, just return the value
            return val   # and ignore the rest statements

    def _Assert(self, stmt, env):
        val = value_of_exp(stmt.test, env)
        if val.pybool() is True:
            return "cont"
        else:
            if stmt.msg is None:
                msg = ""
            else:
                msg = value_of_exp(stmt.msg, env)
            fatal("AssertionError: %s" % msg)

    def _Import(self, stmt, env):
        for a in stmt.names:
            mod = interp.load_module(a.name)
            if a.asname is not None:
                env.put_or_update(a.asname, mod)
            else:
                # get the first segement of module name
                local_name = a.name.partition(".")[0]
                env.put_or_update(local_name, mod)
        return "cont"

    def _ImportFrom(self, stmt, env):
        """
        evaluate the statement like 'from XXX import YYY'

        level: 0 is absolute import, 1 is current directory,
               2 is parent directory
        """
        mod = interp.load_module(stmt.module, stmt.level)
        if IS(mod, PackageValue):     # a package
            for a in stmt.names:      # from XXX import *
                if a == "*":
                    mod.import_all(env)
                    break

                val = mod.getattr(a.name)
                if val is None:
                    fatal("module doesn't have attribute %s." % a.name)

                if a.asname is None:
                    env.put_or_update(a.name, val)
                else:
                    env.put_or_update(a.asname, val)
        else:                   # a regular moudle
            for a in stmt.names:
                if a == "*":
                    mod.import_all(env)
                    break

                val = mod.getattr(a.name)
                if val is None:
                    fatal("this module don't have the attribute")
                if a.asname is None:
                    env.put_or_update(a.name, val)
                else:
                    env.put_or_update(a.asname, val)
        return "cont"

    def _Global(self, stmt, env):
        # every name which is declared as a global name will bind to "global"
        # in local enviroment. so we must change the implemention of the
        # bind function
        for name in stmt.names:
            env.put_or_update(name, "global")
        return "cont"

    def _Expr(self, stmt, env):
        value_of_exp(stmt.value, env)
        return "cont"

    def _Break(self, stmt, env):
        return "break"

    def _Continue(self, stmt, env):
        return "continue"

    def _Pass(self, stmt, env):
        return "cont"

    # need to be implemented
    def _Exec(self, stmt, env):
        pass

    def _With(self, stmt, env):
        pass

    def _Raise(self, stmt, env):
        pass

    def _TryExcept(self, stmt, env):
        pass

    def _TryFinally(self, stmt, env):
        pass


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
        fname = os.path.abspath(fname)
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


###############################################################
# global instances and functions
###############################################################
g_exp = ExpEvaluator()

def value_of_exp(exp, env):
    return g_exp.dispatch(exp, env)

g_stmts = BlockEvaluator()
def value_of_stmts(stmts, env):
    return g_stmts.eval(stmts, env)

interp = Interpreter()

if __name__ == '__main__':
    # interp.start("test/oop.py")
    interp.start("test/2.py")
    # interp.start("test/1.py")
