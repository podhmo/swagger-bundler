# -*- coding:utf-8 -*-
import logging
from swagger_bundler import context
logger = logging.getLogger(__name__)


def make_rootcontext(parser):
    detector_factory = context.DetectorFactoryFromConfigParser(parser)
    return context.make_rootcontext(detector_factory)
