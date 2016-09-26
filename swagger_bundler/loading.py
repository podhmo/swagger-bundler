# -*- coding:utf-8 -*-
import json
import yaml
import os.path
import logging
from collections import OrderedDict
logger = logging.getLogger(__name__)


class Format:
    yaml = "yaml"
    json = "json"
    unknown = "(unknown)"


def dispatch_by_format(filename, fn_map, default=Format.unknown):
    _, ext = os.path.splitext(filename)
    if ext in (".yaml", ".yml"):
        return fn_map[Format.yaml]
    elif ext in (".json", ".js"):
        return fn_map[Format.json]
    else:
        return fn_map[default]


def _json_load(fp):
    return json.load(fp, object_pairs_hook=OrderedDict)


def _json_dump(d, fp):
    return json.dump(d, fp, ensure_ascii=False, indent=2)


def load(fp, format=None, fn_map={Format.yaml: yaml.load, Format.json: _json_load, Format.unknown: yaml.load}):
    if format is not None:
        loader = fn_map[format]
    else:
        fname = getattr(fp, "name", "(unknown)")
        loader = dispatch_by_format(fname, fn_map, default=loading_config.input_format)
    return loader(fp)


def dump(d, fp, format=None, default_flow_style=None, allow_unicode=None, fn_map=None):
    if fn_map is None:
        def yaml_dump(d, fp):
            return yaml.dump(d, fp, default_flow_style=default_flow_style, allow_unicode=allow_unicode)
        fn_map = {Format.yaml: yaml_dump, Format.json: _json_dump, Format.unknown: yaml_dump}

    if format is not None:
        dumper = fn_map[format]
    else:
        fname = getattr(fp, "name", "(unknown)")
        dumper = dispatch_by_format(fname, fn_map, default=loading_config.output_format)
    return dumper(d, fp)


class loading_config:
    input_format = Format.yaml
    output_format = Format.yaml


def setup(input=None, output=None):
    global loading_config
    if input is not None:
        logger.debug("setup input format: %s", input)
        loading_config.input_format = input
    if output is not None:
        logger.debug("setup output format: %s", output)
        loading_config.output_format = output
