# -*- coding:utf-8 -*-
import logging
from collections import defaultdict
from . import loading
from .ordering import ordering, make_dict


logger = logging.getLogger(__name__)


def _titleize(s):
    return "{}{}".format(s[0].title(), s[1:])


class Prefixer:
    def __init__(self, namespace, exposed_predicate):
        self.namespace = namespace
        self.exposed_predicate = exposed_predicate

    def add_prefix(self, data):
        return self.transform(data, toplevel=True)

    def transform(self, data, toplevel=False):
        if hasattr(data, "keys"):
            d = make_dict()
            for k, v in data.items():
                if k == "definitions":
                    d[k] = self._transform_definitions(v)
                elif k == "responses" and toplevel:
                    d[k] = self._transform_responses(v)
                elif k == "$ref":
                    d[k] = self._transform_ref(v)
                else:
                    d[k] = self.transform(v)
            return d
        elif isinstance(data, (list, tuple)):
            return [self.transform(v) for v in data]
        else:  # atom
            return data

    def _transform_ref(self, v):
        if self.namespace in v:
            return v
        head, tail = v.rsplit("/", 1)

        # exposed
        for k in ["definitions", "responses"]:
            if "/{}".format(k) in head and tail in self.exposed_predicate[k]:
                return v
        return "/".join([head, "{}{}".format(self.namespace, _titleize(tail))])

    def _transform_name(self, v):
        if self.namespace in v:
            return v
        return "{}{}".format(self.namespace, _titleize(v))

    def _transform_definitions(self, data):
        d = make_dict()
        exposeds = self.exposed_predicate["definitions"]
        for k, v in data.items():
            if k in exposeds:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d

    def _transform_responses(self, data):
        d = make_dict()
        exposeds = self.exposed_predicate["responses"]
        for k, v in data.items():
            if k in exposeds:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d


def _get_exposed_detail(ctx):
    # Dict[path, {"responses", "definitions"}]
    detail = defaultdict(dict)
    detail[ctx.identifier] = {
        "responses": set(ctx.data.get("responses", {}).keys()),
        "definitions": set(ctx.data.get("definitions", {}).keys())
    }
    ignore_path_set = {ctx.resolver.resolve_identifier(fname) for fname in ctx.detector.detect_exposed()}
    compose_path_set = {ctx.resolver.resolve_identifier(fname) for fname in ctx.detector.detect_compose()}

    # sub relation
    for fname in ctx.detector.detect_compose():
        subcontext = ctx.make_subcontext(fname)
        subdetail = _get_exposed_detail(subcontext)
        for subpath, subpair in subdetail.items():
            if subpath in ignore_path_set:
                detail[subpath].update(subpair)
            elif subpath in compose_path_set:
                continue
            else:
                detail[subpath].update(subpair)
    logger.debug("exposed detail: %s", detail)
    return detail


def get_exposed_predicate(ctx):
    predicate = {"responses": set(), "definitions": set()}
    detail = _get_exposed_detail(ctx)
    detail.pop(ctx.identifier)
    for pair in detail.values():
        predicate["responses"].update(pair["responses"])
        predicate["definitions"].update(pair["definitions"])
    return predicate


def transform(ctx, data, namespace=None):
    if namespace is None:
        return data

    exposed_predicate = get_exposed_predicate(ctx)
    logger.debug("transform: identifier=%s, namespace=%s, ignore=%s", ctx.identifier, namespace, exposed_predicate)
    prefixer = Prefixer(namespace, exposed_predicate)
    return prefixer.add_prefix(data)


def run(ctx, inp, outp, namespace=None):
    subcontext = ctx.make_subcontext_from_port(inp)
    namespace = namespace or subcontext.detector.detect_name()
    result = transform(subcontext, subcontext.data, namespace=namespace)
    ordered = ordering(result)
    loading.dump(ordered, outp)
