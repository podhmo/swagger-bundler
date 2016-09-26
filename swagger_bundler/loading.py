# -*- coding:utf-8 -*-
import json
import yaml
import enum
import os.path
from collections import OrderedDict


class Format(enum.Enum):
    yaml = 1
    json = 2
    unknown = -1


def dispatch_by_format(filename, fn_map):
    _, ext = os.path.splitext(filename)
    if ext in (".yaml", ".yml"):
        return fn_map[Format.yaml]
    elif ext in (".json", ".js"):
        return fn_map[Format.json]
    else:
        return fn_map[Format.unknown]


def _json_load(fp):
    return json.load(fp, object_pairs_hook=OrderedDict)


def load(fp, fn_map={Format.yaml: yaml.load, Format.json: _json_load, Format.unknown: yaml.load}):
    fname = getattr(fp, "name", "(unknown)")
    loader = dispatch_by_format(fname, fn_map)
    return loader(fp)


def dump(d, fp, format=Format.yaml, default_flow_style=None, allow_unicode=None, fn_map=None):
    if fn_map is None:
        def yaml_dump(d, fp):
            return yaml.dump(d, fp, default_flow_style=default_flow_style, allow_unicode=allow_unicode)
        fn_map = {Format.yaml: yaml_dump, Format.json: json.dump, Format.unknown: yaml_dump}
    fname = getattr(fp, "name", "(unknown)")
    dumper = dispatch_by_format(fname, fn_map)
    return dumper(d, fp)
