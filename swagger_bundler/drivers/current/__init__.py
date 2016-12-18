# -*- coding:utf-8 -*-
import sys  # NOQA
from ... import loading
from ...modifiers.ordering import ordering
from .modifierreflink import RefResolveLinker
from .modifierconcat import Concat

"""
json reference examples

# extra ref :: <path>#/<namespace>*<section>/<name>
# path :: (<name>/)*<name>
# namespace :: (<name>/)*
# section :: 'definitions' | 'parameters' | 'responses'

examples

- "#/foo/bar"
- "./#foo/bar"
- "/foo/bar/#foo/bar"
"""


"""
step

- detect namespace
- resolve current space
- concatnation
"""


class RefResolveDriver(object):
    def __init__(self):
        self.linker = RefResolveLinker(self)
        self.concat = Concat(self)

    def run(self, basectx, inp, outp, namespace=None):
        ctx = basectx.make_subcontext_from_port(inp)
        result = self.transform(ctx, ctx.data, namespace=namespace, last=True)
        ordered = ordering(result)
        loading.dump(ordered, outp)

    def transform(self, ctx, data, namespace=None, last=False):
        self.linker.transform(ctx, data)
        self.concat.transform(ctx, data)
        return data
