# -*- coding:utf-8 -*-
import click
import sys
import logging
logger = logging.getLogger(__name__)


def show_on_warning(msg):
    sys.stderr.write(click.style(msg.rstrip("\n"), bold=True, fg="yellow"))
    sys.stderr.write("\n")
    logger.info(msg)
