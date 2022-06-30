# -*- coding: utf-8 -*-
from copy import copy
from pprint import pprint


def TestFunction(num):
    global a
    a = 2
    return num

if __name__ == '__main__':

    from sys import _getframe

    print _getframe().f_lineno

    print 'end'