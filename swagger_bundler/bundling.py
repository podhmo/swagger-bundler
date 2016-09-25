# -*- coding:utf-8 -*-
from . import loading
from .ordering import ordering, make_dict
from . import composing
from . import prefixing


def transform(ctx, data):
    subfiles = ctx.detector.detect_compose()
    if subfiles:
        additional = composing.transform(ctx, make_dict(), subfiles)
        data = composing.merge(additional, data)

    namespace = ctx.detector.detect_namespace()
    if namespace:
        data = prefixing.transform(ctx, data, namespace=namespace)
    return data


def run(ctx, inp, outp):
    subcontext = ctx.make_subcontext_from_port(inp)
    result = transform(subcontext, subcontext.data)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
