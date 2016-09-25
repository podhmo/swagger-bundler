# -*- coding:utf-8 -*-
import os.path
import sys
from . import loading


class Env:
    def __init__(self, option_scanner, pool=None, preprocessor=None):
        self.option_scanner = option_scanner
        self.preprocessor = preprocessor or DEFAULT_PREPROCESSOR
        self.pool = pool or {}  # Dict[path, context]

    def __contains__(self, path):
        return path in self.pool

    def __getitem__(self, path):
        return self.pool[path]

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
        return cls(tuple(parser.items("reserved_word")))

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d.items()))


class Preprocessor:
    def __call__(self, detector, data):
        return self.preprocess_concat(detector, data)

    def preprocess_concat(self, detector, data):
        concat_members = detector.detect_concat()
        if concat_members:
            ignore_members = detector.init_ignore_prefixer()
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

    def detect_ignore_prefixer(self):
        return self.config.get("ignore_prefixer") or []

    def detect_namespace(self):
        return self.config.get("namespace")

    def init_compose(self):
        v = self.config.get("compose")
        if not v:
            v = self.config["compose"] = []
        return v

    def init_ignore_prefixer(self):
        v = self.config.get("ignore_prefixer")
        if not v:
            v = self.config["ignore_prefixer"] = []
        return v


class PathResolver:
    def __init__(self, path):
        self.path = path

    def make_subresolver(self, src):
        abspath = self.resolve_path(src)
        return self.__class__(abspath)

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

    def make_subcontext(self, src, data=None):
        subresolver = self.resolver.make_subresolver(src)
        if subresolver.path in self.env:
            return self.env[subresolver.path]

        if data is None:
            with open(subresolver.path) as rf:
                data = loading.load(rf)

        subconfig = self.env.option_scanner.scan(data)
        subdetector = self.detector.__class__(subconfig)

        self.env.preprocessor(subdetector, data)

        subcontext = self.__class__(self.env, subdetector, subresolver, data)
        self.env.register_context(subcontext)
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
