#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Simple test
"""

print 1, 2
print 1+2
print 1*2
print 3-2
print 1 == 2
print 1 <= 2
print 1 <= 2 and 2 <= 3
print 1 <= 2 and 2 >= 3 or 4 >= 3

print 3 * [1, 2, 3]
print '-----------keywords--------------'
print True
print False
print None

print '-----------test built-in function----------'
print int('11')

print '-----------list, tuple---------------------'
print list((1, 2, 3))
print tuple([1, 2, 3, 4])
# print dict([(1,'a'), (2, 'b'), (3, 'c')])
aa = [1, 2, 3]
print aa
print aa[2]
print aa[1:3]
for i in aa:
    print "in for loop"
    print i
x, y, z = aa
# return x
print x
print y
print z

x += 10
print x
