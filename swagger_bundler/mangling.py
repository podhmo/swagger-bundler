# -*- coding:utf-8 -*-
from . import loading
from .ordering import ordering, make_dict


def transform(ctx, data, namespace=None):
    if namespace is None:
        return data
    return _transform(data, namespace, toplevel=True)


def _transform(data, namespace, toplevel=False):
    if hasattr(data, "keys"):
        d = make_dict()
        for k, v in data.items():
            v = data[k]
            if k == "definitions":
                v = _transform_definitions(v, namespace)
            if k == "responses" and toplevel:
                v = _transform_responses(v, namespace)
            elif k == "$ref":
                v = _transform_ref(v, namespace)
            else:
                v = _transform(v, namespace)
            d[k] = v
        return d
    elif isinstance(data, (list, tuple)):
        return [_transform(v, namespace) for v in data]
    else:  # atom
        return data


def _transform_ref(v, namespace):
    if namespace in v:
        return v
    elif "/" not in v:
        return "{}{}".format(namespace, _titleize(v))
    else:
        head, tail = v.rsplit("/", 1)
        return "/".join([head, "{}{}".format(namespace, _titleize(tail))])


def _titleize(s):
    return "{}{}".format(s[0].title(), s[1:])


def _transform_definitions(data, namespace):
    d = make_dict()
    for k, v in data.items():
        d[_transform_ref(k, namespace)] = _transform(v, namespace)
    return d


def _transform_responses(data, namespace):
    return _transform_definitions(data, namespace)


def mangle(ctx, inp, outp, namespace=None):
    subcontext = ctx.make_subcontext_from_port(inp)
    namespace = namespace or subcontext.detector.detect_name()
    result = transform(subcontext, subcontext.data, namespace=namespace)
    ordered = ordering(result)
    loading.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
