#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
test OOP
"""

class AA(object):
    print "in AA class"
    aa_1 = 1
    aa_2 = 2

    def __init__(self):
        print "in __init__"
        print "aa_1 = ", self.aa_1
        print "aa_2 = ", self.aa_2
        print "exit __init__"

    def aa_method(self):
        print "aa_1 = ", self.aa_1
        print "in aa_method"

a = AA()
a.aa_method()

