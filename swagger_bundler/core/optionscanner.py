# -*- coding:utf-8 -*-
import os.path
import sys
import logging
import magicalimport
import importlib
logger = logging.getLogger(__name__)


class OptionScanner:
    def __init__(self, scan_items, driver_class=None):
        # usually {"compose": "x-bundler-compose", ...}
        # so in yaml file: x-bundler-compose: <compose sourcefile>
        # in program: "compose" as keyword.
        self.scan_items = scan_items
        self.scan_map = dict(scan_items)
        # TODO:: support options
        self.options = {
            "prefixing_targets": set(["definitions", "responses", "parameters"]),
            "postscript_hook": {},
            "driver_class": driver_class,
        }

    def scan(self, data):
        return {sysname: data.pop(getname)
                for sysname, getname in self.scan_items
                if getname in data}

    def load_functions(self, items, here=None):
        d = {}
        for k, postscript in items:
            postscript = postscript.strip()
            if postscript and ":" in postscript:
                d[k] = self.load_function(postscript, here=here)
        return d

    def load_function(self, sym, here=None):
        module_path, fn_name = sym.rsplit(":", 2)
        try:
            _, ext = os.path.splitext(module_path)
            if ext == ".py":
                module = magicalimport.import_from_physical_path(module_path, here=here)
            else:
                module = importlib.import_module(module_path)
            return getattr(module, fn_name)
        except (ImportError, AttributeError) as e:
            sys.stderr.write("could not import {!r}\n{}\n".format(sym, e))
            raise

    @classmethod
    def from_configparser(cls, parser):
        scanner = cls(tuple(parser.items("special_marker")))
        if parser.has_section("postscript_hook"):
            here = parser["config"]["config_dir"]
            hooks = scanner.load_functions(parser.items("postscript_hook"), here=here)
            scanner.options["postscript_hook"] = hooks
        scanner.options["driver_class"] = scanner.load_function(parser["DEFAULT"]["driver"], here=here)
        return scanner
