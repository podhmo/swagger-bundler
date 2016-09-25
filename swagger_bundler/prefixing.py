# -*- coding:utf-8 -*-
import logging
from . import loading
from .ordering import ordering, make_dict


logger = logging.getLogger(__name__)


def _titleize(s):
    return "{}{}".format(s[0].title(), s[1:])


class Prefixer:
    def __init__(self, namespace, ignore_prefixer_predicate):
        self.namespace = namespace
        self.ignore_prefixer_predicate = ignore_prefixer_predicate

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

        # ignore_prefixer
        for k in ["definitions", "responses"]:
            if "/{}".format(k) in head and tail in self.ignore_prefixer_predicate[k]:
                return v
        return "/".join([head, "{}{}".format(self.namespace, _titleize(tail))])

    def _transform_name(self, v):
        if self.namespace in v:
            return v
        return "{}{}".format(self.namespace, _titleize(v))

    def _transform_definitions(self, data):
        d = make_dict()
        ignore_prefixers = self.ignore_prefixer_predicate["definitions"]
        for k, v in data.items():
            if k in ignore_prefixers:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d

    def _transform_responses(self, data):
        d = make_dict()
        ignore_prefixers = self.ignore_prefixer_predicate["responses"]
        for k, v in data.items():
            if k in ignore_prefixers:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d


def get_ignore_prefixer_predicate(ctx):
    predicate = {"responses": set(), "definitions": set()}
    for fname in ctx.detector.detect_ignore_prefixer():
        path = ctx.resolver.resolve_path(fname)
        subcontext = ctx.env.get(path)
        if subcontext is not None:
            subdata = subcontext.data
            predicate["responses"].update(subdata.get("responses", []).keys())
            predicate["definitions"].update(subdata.get("definitions", []).keys())
    for fname in ctx.detector.detect_compose():
        path = ctx.resolver.resolve_path(fname)
        subcontext = ctx.env.get(path)
        subpredicate = get_ignore_prefixer_predicate(subcontext)
        predicate["responses"].update(subpredicate["responses"])
        predicate["definitions"].update(subpredicate["definitions"])
    return predicate


def transform(ctx, data, namespace=None):
    if namespace is None:
        return data

    ignore_prefixer_predicate = get_ignore_prefixer_predicate(ctx)
    logger.debug("transform: namespace=%s, ignore=%s", namespace, ignore_prefixer_predicate)
    prefixer = Prefixer(namespace, ignore_prefixer_predicate)
    return prefixer.add_prefix(data)


def run(ctx, inp, outp, namespace=None):
    subcontext = ctx.make_subcontext_from_port(inp)
    namespace = namespace or subcontext.detector.detect_name()
    result = transform(subcontext, subcontext.data, namespace=namespace)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
