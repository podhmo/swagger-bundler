# -*- coding:utf-8 -*-
from . import loading
from .ordering import ordering, make_dict
from . import bundling
from . import prefixing


def transform(ctx, data):
    subfiles = ctx.detector.detect_bundle()
    if subfiles:
        additional = bundling.transform(ctx, make_dict(), subfiles)
        data = bundling.merge(additional, data)

    namespace = ctx.detector.detect_namespace()
    if namespace:
        data = prefixing.transform(ctx, data, namespace=namespace)
    return data


def generate(ctx, inp, outp):
    subcontext = ctx.make_subcontext_from_port(inp)
    result = transform(subcontext, subcontext.data)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
