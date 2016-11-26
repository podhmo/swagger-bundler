# -*- coding:utf-8 -*-
def titleize(s):
    """fooBar -> FooBar"""
    if not s:
        return s
    else:
        return "{}{}".format(s[0].upper(), s[1:])


def untitlize(s):
    """FooBar -> fooBar"""
    if not s:
        return s
    else:
        return "{}{}".format(s[0].lower(), s[1:])


def guess_name(s, ns):
    yield s
    if ns:
        unprefixed = s[len(ns):]
        yield unprefixed
        yield untitlize(unprefixed)
