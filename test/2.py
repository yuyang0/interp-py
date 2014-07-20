#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""

"""

# simple fucntion definition ane call (1)
def my_add(x, y):
    return x + y

print my_add(1, 3)

# def my_sub(x, y):
#     return x-y

# simple function definition and call  (2)
def my_sub(x, y):
    if y == 0:
        return x
    else:
        return my_sub(x-1, y-1)

print my_sub(4, 1)
print my_sub(4, 2)
print my_sub(4, 0)

# def test_lambda():
#     return map(lambda x: x+1, [1,2,3])
# print test_lambda()
print "-------test recursive function--------------"
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
print factorial(5)
print factorial(6)

print "---------test Assignment --------------------"
def test_assign():
    if False:
        a = 2
    else:
        a = 3
        b = 4
        b = 5
    print a, b
test_assign()
print "-----------argument pass style -----------------"
def test_var_args(a, b, *args):
    print a, b
    print args
def test_default(a, b, c=3):
    return a + b + c
test_var_args('a', 'b', 'c', 'd')
# print test_default(1, 2)
# print "-----------test if return ----------------------"
# def test_if_return():
#     a = 1
#     if a:
#         b = 1
#         return
#         b = 2
#         print b
#     else:
#         b = 10
#         return b
#         b = 11
#     print b

# print test_if_return()
# print '---------------test while-------------------------'
# def test_while():
#     i = 0
#     while i < 10:
#         print i
#         i = i + 1
#         if i > 5:
#             continue
#         print "after continue."
#     else:
#         print "in else block."
# test_while()
