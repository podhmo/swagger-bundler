# -*- coding:utf-8 -*-
import os.path
import sys
from . import loading


class Env:
    def __init__(self, detector_factory, pool=None):
        self.detector_factory = detector_factory
        self.pool = pool or {}  # Dict[path, context]

    def __contains__(self, path):
        return path in self.pool

    def __getitem__(self, path):
        return self.pool[path]

    def register_context(self, context):
        self.pool[context.path] = context


class Detector:
    def __init__(self, config, scan_items):
        self.config = config

        # usually {"bundle": "@bundle", ...}
        # so in yaml file: @bundle: <bundle value>
        # in program: "bundle" as keyword.
        self.scan_items = scan_items

    def scan(self, data):
        return {sysname: data.pop(getname)
                for sysname, getname in self.scan_items
                if getname in data}

    def detect_bundle(self):
        return self.config.get("bundle") or []

    def detect_namespace(self):
        return self.config.get("namespace")

    def detect_disable_mangle(self):
        return self.config.get("disable_mangle") or []


class DetectorFactoryFromConfigParser:
    def __init__(self, parser, cls=Detector):
        self.cls = cls
        self.parser = parser
        self.scan_items = tuple(self.parser.items("reserved_word"))

    def __call__(self, config):
        return self.cls(config, self.scan_items)


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
        subconfig = self.detector.scan(data)
        subdetector = self.env.detector_factory(subconfig)
        subcontext = self.__class__(self.env, subdetector, subresolver, data)
        self.env.register_context(subcontext)
        return subcontext

    def make_subcontext_from_port(self, port):
        data = loading.load(port)
        if port is sys.stdin:
            return self.make_subcontext(".", data=data)
        else:
            return self.make_subcontext(port.name, data=data)


def make_rootcontext(detector_factory):
    config = {"root": True}
    env = Env(detector_factory)
    detector = detector_factory(config)
    resolver = PathResolver(".")
    data = {}
    return Context(env, detector, resolver, data)
