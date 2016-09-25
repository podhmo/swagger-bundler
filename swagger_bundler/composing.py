import copy
from collections import Mapping
import logging
from . import loading
from .ordering import ordering, make_dict

logger = logging.getLogger(__name__)


# xxx:
def _merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], Mapping)):
            _merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def merge(x, y):
    return _merge(x, copy.deepcopy(y))


def transform(ctx, result, files):
    logger.debug("transform: files=%s", files)
    additional = make_dict()
    for src in files:
        subcontext = ctx.make_subcontext(src)
        if subcontext.is_marked():
            continue
        additional = merge(additional, subcontext.data)
        subcontext.mark()
        subfiles = subcontext.detector.detect_compose()
        if subfiles:
            transform(subcontext, additional, subfiles)
    return merge(additional, result)


def run(ctx, files, outp):
    result = transform(ctx, make_dict(), files)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
