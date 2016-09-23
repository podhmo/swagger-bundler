import yaml
from .ordering import ordering
from collections import Mapping


def merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], Mapping)):
            merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def bundle(files, outp, namespace=None):
    result = {}
    for src in files:
        with open(src) as inp:
            data = yaml.load(inp)
            result = merge(result, data)
    ordered = ordering(result)
    yaml.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
