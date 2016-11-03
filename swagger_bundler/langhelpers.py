# -*- coding:utf-8 -*-
def titleize(s):
    """fooBar -> FooBar"""
    if not s:
        return s
    else:
        return "{}{}".format(s[0].title(), s[1:])
