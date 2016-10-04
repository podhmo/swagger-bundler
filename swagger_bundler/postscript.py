import traceback
import sys
import pprint


def echo(ctx, data, *args, **kwargs):
    sys.stderr.write("echo: ctx={}, data={}, args={}, kwargs={}\n".format(
        pprint.pformat(ctx, indent=2),
        pprint.pformat(data, indent=2),
        pprint.pformat(args, indent=2),
        pprint.pformat(kwargs, indent=2))
    )
    traceback.print_stack(limit=1, file=sys.stderr)
