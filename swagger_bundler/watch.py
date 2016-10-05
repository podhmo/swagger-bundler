import sys
import time
import logging
import os.path
from . import highlight
logger = logging.getLogger(__name__)


def do_watch(fn, path, pattern, ignore_pattern=None, outfile=None):
    outfile = outfile and os.path.normpath(outfile)
    try:
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
        from watchdog.events import LoggingEventHandler
    except ImportError:
        msg = """\
watch dog is not found.
please run `pip install "swagger_bundler[watch]`
        """
        highlight.show_on_warning(msg)
        sys.exit(1)

    class _CallbackHandler(PatternMatchingEventHandler):
        def process(self, event):
            sys.stderr.write("event detect: event_type={}, src={}\n".format(event.event_type, event.src_path))
            try:
                return fn()
            except:
                logger.warn("exception", exc_info=True)

        def on_any_event(self, event):
            if outfile is None or outfile != os.path.normpath(event.src_path):
                self.process(event)

    observer = Observer()
    patterns = [pattern]
    ignore_patterns = []
    if ignore_pattern is not None:
        ignore_patterns.append(ignore_pattern)
    sys.stderr.write("watch starting patterns={}, ignore_patterns={}\n".format(patterns, ignore_patterns))
    callback_handler = _CallbackHandler(patterns=patterns, ignore_patterns=ignore_patterns)

    observer.schedule(LoggingEventHandler(), path=path, recursive=True)
    observer.schedule(callback_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    try:
        while observer.is_alive():
            observer.join(1)
    except Exception as e:
        sys.stderr.write(str(e))
