# -*- coding:utf-8 -*-
import logging
from ...modifiers import composing
from ...modifiers.ordering import ordering
from ...modifiers import orphancheck
from . import prefixing
from ... import loading
logger = logging.getLogger(__name__)


class FileConcatDriver:
    def run(self, ctx, inp, outp, namespace=None):
        subcontext = ctx.make_subcontext_from_port(inp)
        result = self.transform(subcontext, subcontext.data, namespace=namespace, last=True)

        orphancheck.check_orphan_reference(ctx, result, exception_on_fail=False)

        ordered = ordering(result)
        loading.dump(ordered, outp)

    def transform(self, ctx, data, namespace=None, last=False):
        subfiles = ctx.detector.detect_compose()
        if subfiles:
            data = composing.transform(ctx, data, subfiles, last=last)

        namespace = namespace or ctx.detector.detect_namespace()
        if namespace:
            data = prefixing.transform(ctx, data, namespace=namespace, last=last)

        # TODO: handling code
        postscript = ctx.options["postscript_hook"].get("bundle")
        if postscript and callable(postscript):
            postscript_result = postscript(ctx, data, namespace=namespace, last=last)
            if postscript_result is not None:
                data = postscript_result
        return data
