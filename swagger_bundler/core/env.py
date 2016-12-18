# -*- coding:utf-8 -*-
import logging
from .preprocessor import DEFAULT_PREPROCESSOR
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
