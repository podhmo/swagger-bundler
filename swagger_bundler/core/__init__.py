from .optionscanner import OptionScanner  # NOQA
from .context import Context
from .env import Env
from .detector import Detector
from .pathresolver import PathResolver


def make_rootcontext(option_scanner, driver_class=None):
    config = {"root": True}
    driver_class = driver_class or option_scanner.options["driver_class"]
    driver = driver_class()  # xxx
    env = Env(option_scanner, driver)
    detector = Detector(config)
    resolver = PathResolver(".")
    data = {}
    ctx = Context(env, detector, resolver, data)
    return ctx
