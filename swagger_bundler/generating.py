# -*- coding:utf-8 -*-
from . import loading
from .ordering import ordering, make_dict
from . import bundling
from . import mangling


def transform(data):
    if "bundle" in data:
        files = data.pop("bundle")
        additional = bundling.transform(make_dict(), files)
        additional.pop("bundle", None)
        additional.pop("namespace", None)
        data = bundling.merge(additional, data)

    namespace = data.pop("namespace", None)
    return mangling.transform(data, namespace=namespace)


def generate(inp, outp):
    data = loading.load(inp)
    result = transform(data)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
