#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
modules
"""
main_mod = None

def import_module(name):
    pass

def eval_file(fname):
    global main_mod
    node = parse_file(fname)
    main_mod = ModuleValue("__main__", fname, built_in_env)
    module_env = main_mod.env
    if IS(mod, ast.Module):
        value_of_stmts(mod.body, module_env)
        return main_mod
    else:
        print "error: unkown MOD type."
    print "-------------final value----------------------"
    print main_mod
    print "----------------------------------------------"

class Module(object):
    pass

if __name__ == '__main__':
    eval_file("test/2.py")
