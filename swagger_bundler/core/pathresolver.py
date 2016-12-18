# -*- coding:utf-8 -*-
import logging
import re
import os.path
logger = logging.getLogger(__name__)


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
