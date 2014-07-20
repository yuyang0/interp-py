#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
enviroments
"""
import copy

class EnvError(Exception):
    pass


class EnvLookupError(EnvError):
    def __init__(self, msg):
        self.msg = msg


class EnvBindError(EnvError):
    def __init__(self, msg):
        self.msg = msg


class EnvAssignError(EnvError):
    def __init__(self, msg):
        self.msg = msg


class Env(object):
    def __init__(self, parent=None, table={}):
        self.parent = parent
        self.table = copy.deepcopy(table)  # deepcopy is very important

    def lookup(self, var):
        val = self.table.get(var, None)
        if val is None:
            if self.parent is None:
                raise EnvLookupError("%s is not bound" % var)
            else:
                return self.parent.lookup(var)
        else:
            return val

    def lookup_local(self, var):
        return self.table.get(var, None)

    def put(self, var, val):
        if var in self.table:
            print "%s is already bind in this env" % var
            raise EnvBindError("%s is already bind in this env" % var)
        self.table[var] = val

    def update(self, var, val):
        e = self.find_defined_env(var)
        if e is None:
            raise EnvAssignError("%s is not bound in environment, so we can't assign")
        e.table[var] = val

    def put_or_update(self, var, val):
        self.table[var] = val

    def find_defined_env(self, var):
        if self.lookup_local(var) is None:
            if self.parent is None:
                return None
            else:
                return self.parent.find_defined_env(var)
        else:
            return self

    def merger_env(self, other):
        for var, val in other.table.items():
            self.table[var] = val

    def set_table(self, tbl):
        self.table = tbl

    def __str__(self):
        return str(self.table) + "~-> " + str(self.parent)

class ModuleEnv(Env):
    def __init__(self, parent=None, table={}):
        super(ModuleEnv, self).__init__(parent, table)


class ClassEnv(Env):
    def __init__(self, parent=None, table={}):
        super(ClassEnv, self).__init__(parent, table)


class InstanceEnv(Env):
    def __init__(self, parent=None, table={}):
        super(InstanceEnv, self).__init__(parent, table)


