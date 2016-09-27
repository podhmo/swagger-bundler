# -*- coding:utf-8 -*-
import re
import os.path
import sys
import click
import logging
from . import loading
from . import bundling
logger = logging.getLogger(__name__)


class Env:
    def __init__(self, option_scanner, pool=None, preprocessor=None):
        self.option_scanner = option_scanner
        self.preprocessor = preprocessor or DEFAULT_PREPROCESSOR
        self.pool = pool or {}  # Dict[path, context]

    def __contains__(self, path):
        return path in self.pool

    def __getitem__(self, path):
        return self.pool[path]

    def get(self, path, default=None):
        return self.pool.get(path) or default

    def register_context(self, context):
        self.pool[context.path] = context


class OptionScanner:
    def __init__(self, scan_items):
        # usually {"compose": "x-bundler-compose", ...}
        # so in yaml file: x-bundler-compose: <compose sourcefile>
        # in program: "compose" as keyword.
        self.scan_items = scan_items

    def scan(self, data):
        return {sysname: data.pop(getname)
                for sysname, getname in self.scan_items
                if getname in data}

    @classmethod
    def from_configparser(cls, parser):
        return cls(tuple(parser.items("special_marker")))

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d.items()))


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

    def is_marked(self):
        return self.marked

    def mark(self):
        self.marked = True

    @property
    def path(self):
        return self.resolver.path

    @property
    def identifier(self):
        return self.resolver.identifier

    def _on_load_failure(self, src, e=None):
        if e is not None:
            sys.stderr.write("{}: {}\n".format(type(e), e))
        msg = "  on where={!r}, open={!r}\n".format(self.path, src)
        sys.stderr.write(click.style(msg, bold=True, fg="yellow"))
        logger.info(msg)
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

        # on qualified import
        ns = subcontext.resolver.ns
        if ns is not None:
            subcontext.data = bundling.transform(subcontext, subcontext.data, namespace=ns)
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


def make_rootcontext(option_scanner):
    config = {"root": True}
    env = Env(option_scanner)
    detector = Detector(config)
    resolver = PathResolver(".")
    data = {}
    return Context(env, detector, resolver, data)

DEFAULT_PREPROCESSOR = Preprocessor()
