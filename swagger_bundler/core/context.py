# -*- coding:utf-8 -*-
import sys
import logging
from .. import loading
from .. import highlight
logger = logging.getLogger(__name__)


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
