# -*- coding:utf-8 -*-
import yaml
from .ordering import ordering, make_dict
from . import bundling
from . import mangling


def generate(inp, outp):
    data = yaml.load(inp)
    if "bundle" in data:
        files = data.pop("bundle")
        additional = bundling.transform(make_dict(), files)
        additional.pop("bundle", None)
        additional.pop("namespace", None)
        data = bundling.merge(additional, data)

    namespace = data.pop("namespace", None)
    result = mangling.transform(data, namespace=namespace)
    ordered = ordering(result)
    yaml.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
