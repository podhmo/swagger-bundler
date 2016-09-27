# -*- coding:utf-8 -*-
import logging
from . import loading
from .ordering import ordering
from . import composing
from . import prefixing

logger = logging.getLogger(__name__)


def transform(ctx, data, namespace=None):
    subfiles = ctx.detector.detect_compose()
    if subfiles:
        data = composing.transform(ctx, data, subfiles)

    namespace = namespace or ctx.detector.detect_namespace()
    if namespace:
        data = prefixing.transform(ctx, data, namespace=namespace)
    return data


def run(ctx, inp, outp, namespace=None):
    subcontext = ctx.make_subcontext_from_port(inp)
    result = transform(subcontext, subcontext.data, namespace=namespace)
    ordered = ordering(result)
    loading.dump(ordered, outp)
