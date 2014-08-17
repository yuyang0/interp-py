#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
utilities
"""
import sys
import ast
from unparse import Unparser

__all__ = ["parse_file", "parse_str", "IS", "fatal", "get_id", "dict_sub",
           "partial_zip", "call_stk"]

def parse_file(name):
    try:
        with open(name, 'rb') as f:
            return ast.parse(f.read())
    except IOError:
        print "can't open file %s" % name

parse_str = ast.parse
IS = isinstance

DEBUG = True

# these two global variables used to record the call stack, when encounter a
# error, we must print the call stack

class CallStack(object):
    def __init__(self):
        self.stk = []
        self.unparser = Unparser()
        self.cur_node = None
        self.contianer = None

    def set_cur_node(self, node, fname, container="<Module>"):
        self.cur_node = (node, fname, container)

    def set_container(self, node):
        self.container = node

    def append(self, node, fname, container="<Module>"):
        self.stk.append((node, fname, container))

    def append_cur_node(self):
        self.stk.append(self.cur_node)

    def pop(self):
        self.stk.pop()

    def print_stk(self):
        self.stk.append(self.cur_node)

        for ele in self.stk:
            node, fname, container = ele
            print 'File " %s", line %d' % (fname, node.lineno)
            src = self.unparser.start(node)
            print "    " + src.strip()

call_stk = CallStack()

def fatal(who, *msg):
    print "Traceback (most recent call last):"
    call_stk.print_stk()

    output = who + ": " + ' '.join(map(str, msg))
    print output
    sys.exit(-1)

def foldl(f, x, *lsts):
    lsts = zip(*lsts)
    ret = x
    for args in lsts:
        ret = f(ret, *args)
    return ret

def get_id(x):
    if IS(x, ast.Name):
        return x.id
    else:
        return x

def dict_sub(d1, d2):
    ret = {}
    for k, v in d1.items():
        if k not in d2:
            ret[k] = v
    return ret


def partial_zip(a1, a2):
    """
    return a triple
    """
    rest_a1 = []
    rest_a2 = []
    if len(a1) > len(a2):
        rest_a1 = a1[len(a2):]
    if len(a1) < len(a2):
        rest_a2 = a2[len(a1):]
    return (zip(a1, a2), rest_a1, rest_a2)
