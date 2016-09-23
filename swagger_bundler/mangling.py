# -*- coding:utf-8 -*-
import yaml
import sys
from .ordering import ordering


def ordered_items(d):
    return ((int(k), v) if k.isdigit() else (k, v) for k, v in sorted((str(k), v) for k, v in d.items()))


def transform(data, ns_key="namespace", namespace=None):
    if namespace is None:
        if ns_key not in data:
            sys.stderr.write("{} is not found. skipping...\n".format(ns_key))
            return data
        namespace = data[ns_key]
    return _transform(data, namespace)


def _transform(data, namespace):
    if hasattr(data, "keys"):
        d = {}
        for k, v in ordered_items(data):
            v = data[k]
            if k == "definitions":
                v = _transform_definitions(v, namespace)
            if k == "responses":
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
        return "{}{}".format(namespace, v.title())
    else:
        head, tail = v.rsplit("/", 1)
        return "/".join([head, "{}{}".format(namespace, tail.title())])


def _transform_definitions(data, namespace):
    d = {}
    for k, v in ordered_items(data):
        d[_transform_ref(k, namespace)] = _transform(v, namespace)
    return d


def _transform_responses(data, namespace):
    return _transform_definitions(data, namespace)


def mangle(inp, outp, namespace=None):
    data = yaml.load(inp)
    result = transform(data, namespace=namespace)
    ordered = ordering(result)
    yaml.dump(ordered, outp, allow_unicode=True, default_flow_style=False)
