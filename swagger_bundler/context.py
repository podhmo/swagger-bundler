# -*- coding:utf-8 -*-
import re
import os.path
import sys
import logging
import magicalimport
import importlib
from . import loading
from . import highlight
logger = logging.getLogger(__name__)


class Env:
    def __init__(self, option_scanner, driver, pool=None, preprocessor=None):
        self.option_scanner = option_scanner
        self.preprocessor = preprocessor or DEFAULT_PREPROCESSOR
        self.pool = pool or {}  # Dict[path, context]

        self.driver = driver
        self.root_context = None

    def register_driver(self, driver):
        self.driver = driver

    def __contains__(self, path):
        return path in self.pool

    def __getitem__(self, path):
        return self.pool[path]

    def get(self, path, default=None):
        return self.pool.get(path) or default

    def register_context(self, context):
        self.pool[context.identifier] = context


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


class Preprocessor:
    def __call__(self, detector, data):
        return self.preprocess_concat(detector, data)

    def preprocess_concat(self, detector, data):
        concat_members = detector.detect_concat()
        if concat_members:
            ignore_members = detector.init_exposed()
            compose_members = detector.init_compose()
            for fname in concat_members:
                ignore_members.append(fname)
                compose_members.append(fname)
        return data


class Detector:
    def __init__(self, config):
        self.config = config

    def detect_concat(self):
        return self.config.get("concat") or []

    def detect_compose(self):
        return self.config.get("compose") or []

    def detect_exposed(self):
        return self.config.get("exposed") or []

    def detect_namespace(self):
        return self.config.get("namespace")

    def update_compose(self, newval):
        self.config["compose"] = newval

    def init_compose(self):
        v = self.config.get("compose")
        if not v:
            v = self.config["compose"] = []
        return v

    def init_exposed(self):
        v = self.config.get("exposed")
        if not v:
            v = self.config["exposed"] = []
        return v


class PathResolver:
    IDENTIFIER_RX = re.compile("^(\S+)\s+as\s+(\S+)$")  # e.g. "foo.yaml as F"

    def __init__(self, path, ns=None):
        self.path = path
        self.ns = ns
        self.identifier = (path, ns)

    def make_subresolver(self, src):
        abspath, ns = self.resolve_identifier(src)
        return self.__class__(abspath, ns=ns)

    def resolve_identifier(self, src):
        # identifier = path + ns
        # "foo.yaml as F" is path="foo.yaml", ns="F"
        m = self.IDENTIFIER_RX.search(src)
        if m is not None:
            return self.resolve_path(m.group(1)), m.group(2)
        elif self.ns is not None:
            return self.resolve_path(src), self.ns
        else:
            return self.resolve_path(src), None

    def resolve_path(self, src):
        if os.path.isabs(src):
            return src
        else:
            return os.path.normpath(os.path.join(os.path.dirname(self.path), src))


class Context:
    def __init__(self, env, detector, resolver, data):
        self.env = env
        self.detector = detector
        self.resolver = resolver
        self.data = data
        self.marked = False

    def exact_tagname(self, name):
        return self.env.option_scanner.scan_map[name]

    def is_marked(self):
        return self.marked

    def mark(self):
        self.marked = True

    @property
    def driver(self):
        return self.env.driver

    @property
    def path(self):
        return self.resolver.path

    @property
    def options(self):
        return self.env.option_scanner.options

    @property
    def identifier(self):
        return self.resolver.identifier

    @property
    def ns(self):
        return self.resolver.ns

    def _on_load_failure(self, src, e=None):
        if e is not None:
            sys.stderr.write("{}: {}\n".format(type(e), e))
        msg = "  on where={!r}, open={!r}\n".format(self.path, src)
        highlight.show_on_warning(msg)
        sys.stderr.flush()

    def make_subcontext(self, src, data=None):
        subresolver = self.resolver.make_subresolver(src)
        if subresolver.identifier in self.env:
            return self.env[subresolver.identifier]
        if data is None:
            try:
                with open(subresolver.path) as rf:
                    data = loading.load(rf)
            except (FileNotFoundError, IsADirectoryError) as e:
                self._on_load_failure(src, e=e)
                sys.stderr.write("give up..\n")
                sys.exit(-1)
            except Exception as e:
                self._on_load_failure(src, e=e)
                raise

        subconfig = self.env.option_scanner.scan(data)
        subdetector = self.detector.__class__(subconfig)

        self.env.preprocessor(subdetector, data)
        logger.debug("make context: file=%s", subresolver.path)
        logger.debug("make context: config=%s", subdetector.config)
        subcontext = self.__class__(self.env, subdetector, subresolver, data)
        self.env.register_context(subcontext)

        # TODO: handling code
        postscript = subcontext.options["postscript_hook"].get("load")
        if postscript and callable(postscript):
            postscript_result = postscript(subcontext, subcontext.data, last=False)
            if postscript_result is not None:
                subcontext.data = postscript_result

        # on qualified import
        ns = subcontext.resolver.ns
        if ns is not None and self.resolver.ns != ns:
            subcontext.data = subcontext.driver.transform(subcontext, subcontext.data, namespace=ns)
            # update compose targets list.
            exposed_list = subcontext.detector.detect_exposed()
            new_compose_target_list = [c for c in subcontext.detector.detect_compose() if c in exposed_list]
            subcontext.detector.update_compose(new_compose_target_list)
        return subcontext

    def make_subcontext_from_port(self, port):
        data = loading.load(port)
        if port is sys.stdin:
            return self.make_subcontext(".", data=data)
        else:
            return self.make_subcontext(port.name, data=data)


def make_rootcontext(option_scanner, driver_class=None):
    config = {"root": True}
    driver_class = driver_class or option_scanner.options["driver_class"]
    driver = driver_class()  # xxx
    env = Env(option_scanner, driver)
    detector = Detector(config)
    resolver = PathResolver(".")
    data = {}
    ctx = Context(env, detector, resolver, data)
    return ctx

DEFAULT_PREPROCESSOR = Preprocessor()
