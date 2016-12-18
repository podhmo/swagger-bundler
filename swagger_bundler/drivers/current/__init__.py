# -*- coding:utf-8 -*-
import sys  # NOQA
from ... import loading
from ...modifiers.ordering import ordering
from ...modifiers import orphancheck
from .linker import RefResolveLinker
from .concat import Concat
from .merger import CommonDefinitionMerger
from .squasher import NamespaceSquasher


class RefResolveDriver(object):
    def __init__(self):
        self.linker = RefResolveLinker(self)
        self.concat = Concat(self)
        self.merger = CommonDefinitionMerger()
        self.squasher = NamespaceSquasher()

    def run(self, basectx, inp, outp, namespace=None):
        ctx = basectx.make_subcontext_from_port(inp)
        result = self.transform(ctx, ctx.data, namespace=namespace, last=True)
        ordered = ordering(result)
        loading.dump(ordered, outp)

    def transform(self, ctx, data, namespace=None, last=False):
        self.linker.transform(ctx, data)
        self.concat.transform(ctx, data)
        if last:
            self.merger.transform(ctx, data)
            self.squasher.transform(ctx, data)
            orphancheck.check_orphan_reference(ctx, data, exception_on_fail=False)
        #     # todo: ref-fixer

        # TODO: handling code
        postscript = ctx.options["postscript_hook"].get("bundle")
        if postscript and callable(postscript):
            postscript_result = postscript(ctx, data, namespace=namespace, last=last)
            if postscript_result is not None:
                data = postscript_result
        return data
