#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
utilities
"""
import sys
import ast

__all__ = ["parse_file", "parse_str", "IS", "fatal", "get_id", "dict_sub", "partial_zip"]

def parse_file(name):
    try:
        with open(name, 'rb') as f:
            return ast.parse(f.read())
    except IOError:
        print "can't open file %s" % name

parse_str = ast.parse
IS = isinstance

DEBUG = True

def fatal(who, *msg):
    output = who + ": " + ' '.join(map(str, msg))
    print output
    if DEBUG:
        raise
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
