# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


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
