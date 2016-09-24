# -*- coding:utf-8 -*-
from . import loading
from .ordering import ordering, make_dict


def transform(ctx, data, namespace=None):
    if namespace is None:
        return data

    disable_mangle_predicate = {"responses": set(), "definitions": set()}
    for fname in ctx.detector.detect_disable_mangle():
        path = ctx.resolver.resolve_path(fname)
        if path in ctx.env:
            subdata = ctx.env[path].data
            disable_mangle_predicate["responses"].update(subdata.get("responses", []).keys())
            disable_mangle_predicate["definitions"].update(subdata.get("definitions", []).keys())
    transformer = Transformer(namespace, disable_mangle_predicate)
    return transformer.transform(data, toplevel=True)


class Transformer:
    def __init__(self, namespace, disable_mangle_predicate):
        self.namespace = namespace
        self.disable_mangle_predicate = disable_mangle_predicate

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

        # disable_mangle
        for k in ["definitions", "responses"]:
            if "/{}".format(k) in head and tail in self.disable_mangle_predicate[k]:
                return v
        return "/".join([head, "{}{}".format(self.namespace, _titleize(tail))])

    def _transform_name(self, v):
        if self.namespace in v:
            return v
        return "{}{}".format(self.namespace, _titleize(v))

    def _transform_definitions(self, data):
        d = make_dict()
        disable_mangles = self.disable_mangle_predicate["definitions"]
        for k, v in data.items():
            if k in disable_mangles:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d

    def _transform_responses(self, data):
        d = make_dict()
        disable_mangles = self.disable_mangle_predicate["responses"]
        for k, v in data.items():
            if k in disable_mangles:
                d[k] = self.transform(v)
            else:
                d[self._transform_name(k)] = self.transform(v)
        return d


def _titleize(s):
    return "{}{}".format(s[0].title(), s[1:])


def mangle(ctx, inp, outp, namespace=None):
    subcontext = ctx.make_subcontext_from_port(inp)
    namespace = namespace or subcontext.detector.detect_name()
    result = transform(subcontext, subcontext.data, namespace=namespace)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
