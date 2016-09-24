from . import loading
from .ordering import ordering, make_dict
from collections import Mapping


def merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], Mapping)):
            merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def transform(result, files):
    for src in files:
        with open(src) as inp:
            data = loading.load(inp)
            result = merge(result, data)
    return result


def bundle(files, outp):
    result = transform(make_dict(), files)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
