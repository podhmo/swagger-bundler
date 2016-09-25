# -*- coding:utf-8 -*-
from swagger_bundler import context


def make_rootcontext_from_configparser(parser):
    option_scanner = context.OptionScanner.from_configparser(parser)
    return context.make_rootcontext(option_scanner)
