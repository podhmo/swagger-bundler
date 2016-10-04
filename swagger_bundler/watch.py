import click
import sys
import time
import logging
logger = logging.getLogger(__name__)


def do_watch(fn, path, pattern, ignore_pattern=None):
    try:
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
        from watchdog.events import LoggingEventHandler
    except ImportError:
        msg = """\
watch dog is not found.
please run `pip install "swagger_bundler[watch]`
        """
        sys.stderr.write(click.style(msg, bold=True, fg="yellow"))
        sys.exit(1)

    class _CallbackHandler(PatternMatchingEventHandler):
        def process(self, event):
            sys.stderr.write("event detect: event_type={}, src={}\n".format(event.event_type, event.src_path))
            try:
                return fn()
            except Exception as e:
                logger.warn("exception", exc_info=True)

        def on_any_event(self, event):
            self.process(event)

    observer = Observer()
    patterns = [pattern]
    ignore_patterns = [ignore_pattern] if ignore_pattern else []
    sys.stderr.write("watch starting patterns={}, ignore_patterns={}\n".format(patterns, ignore_patterns))
    callback_handler = _CallbackHandler(patterns=patterns, ignore_patterns=ignore_patterns)

    observer.schedule(LoggingEventHandler(), path=path, recursive=True)
    observer.schedule(callback_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    try:
        while observer.is_alive():
            observer.join(1)
    except Exception as e:
        sys.stderr.write(str(e))
