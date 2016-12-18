# -*- coding:utf-8 -*-
import logging
from dictknife import deepmerge
from .ordering import make_dict
logger = logging.getLogger(__name__)


def merged(left, right):
    # import json
    # logger.debug("**merge: %s @@@@ %s**", json.dumps(left, indent=2), json.dumps(right, indent=2))
    result = deepmerge(left, right)
    # logger.debug("****merge result: %s****", json.dumps(result, indent=2))
    return result


def transform(ctx, fulldata, files, last=False):
    logger.debug("transform: files=%s", files)
    additional = make_dict()
    for src in files:
        subcontext = ctx.make_subcontext(src)
        if subcontext.is_marked():
            logger.debug("skip: {}\n".format(subcontext.identifier))
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
