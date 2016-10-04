# -*- coding:utf-8 -*-
import sys
import os.path
import configparser
from collections import OrderedDict


CONFIG_NAME = "swagger-bundler.ini"


def pickup_path(start_path, filename, default=None):
    """pickupping the config file path

    start path = "/foo/bar/boo", filename = "config.ini"
    finding candidates are ["/foo/bar/boo/config.ini", "/foo/bar/config.ini", "/foo/config.ini", "/config.ini"]
    """
    start_point = os.path.normpath(os.path.abspath(start_path))
    current = start_point
    candidates = []
    while True:
        candidates.append(os.path.join(current, filename))
        if current == "/":
            break
        current, dropped = os.path.split(current)

    for path in candidates:
        if os.path.exists(path):
            return path
    return default


def pickup_config(start_path=None, default=None):
    start_path = start_path or os.getcwrd()
    return pickup_path(start_path, CONFIG_NAME, default=default)


def init_config(path):
    template = """\
[DEFAULT]

[special_marker]
# todo: gentle description.
namespace = x-bundler-namespace
compose = x-bundler-compose
concat = x-bundler-concat
exposed = x-bundler-exposed

[postscript_hook]
# lambda ctx, data, *args, **kwargs: do_something()
## examples:
# swagger_bundler.postscript:echo
# or
# a/b/c/d.py:function_name
compose =
bundle =
add_namespace =
validate =
"""
    sys.stderr.write("generate {}.\n".format(path))
    sys.stderr.flush()
    with open(path, "w") as wf:
        wf.write(template)


def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    config.add_section("config")
    config["config"]["config_path"] = path
    config["config"]["config_dir"] = os.path.dirname(path)
    return config


def describe_config(config, outp):
    import json
    d = OrderedDict()
    d["config"] = OrderedDict(config.items("config"))
    d["special_marker"] = OrderedDict(config.items("special_marker"))
    json.dump(d, outp, indent=2)
