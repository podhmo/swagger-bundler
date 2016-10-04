import traceback
import sys


def echo(*args, **kwargs):
    sys.stderr.write("echo: args={}, kwargs={}\n".format(args, kwargs))
    traceback.print_stack(limit=1, file=sys.stderr)
