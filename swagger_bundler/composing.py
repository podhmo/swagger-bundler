# -*- coding:utf-8 -*-
import logging
from . import loading
from .ordering import ordering, make_dict
logger = logging.getLogger(__name__)


def _merged(left, right):
    if isinstance(left, list):
        r = left[:]
        if isinstance(right, (list, tuple)):
            for e in right:
                if e not in r:
                    r.append(e)
        else:
            if right not in r:
                r.append(right)
        return r
    elif hasattr(left, "get"):
        if hasattr(right, "get"):
            r = left.copy()
            for k in right.keys():
                if k in left:
                    r[k] = _merged(r[k], right[k])
                else:
                    r[k] = right[k]
            return r
        else:
            raise ValueError("cannot merge dict and non-dict: left=%s, right=%s", left, right)
    else:
        return right


def merged(left, right):
    # import json
    # logger.debug("**merge: %s @@@@ %s**", json.dumps(left, indent=2), json.dumps(right, indent=2))
    result = _merged(left, right)
    # logger.debug("****merge result: %s****", json.dumps(result, indent=2))
    return result


def transform(ctx, fulldata, files, last=False):
    logger.debug("transform: files=%s", files)
    additional = make_dict()
    for src in files:
        subcontext = ctx.make_subcontext(src)
        if subcontext.is_marked():
            continue
        additional = merged(additional, subcontext.data)
        subcontext.mark()
        subfiles = subcontext.detector.detect_compose()
        if subfiles:
            additional = transform(subcontext, additional, subfiles)
    result = merged(additional, fulldata)

    # TODO: handling code
    postscript = ctx.options["postscript_hook"].get("compose")
    if postscript and callable(postscript):
        postscript_result = postscript(ctx, result, last=last)
        if postscript_result is not None:
            result = postscript_result
    return result


def run(ctx, files, outp):
    result = transform(ctx, make_dict(), files, last=True)
    ordered = ordering(result)
    loading.dump(ordered, outp)
