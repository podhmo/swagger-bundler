import traceback
import sys
import pprint
from collections import deque


def echo(ctx, data, *args, **kwargs):
    sys.stderr.write("echo: ctx={}, data={}, args={}, kwargs={}\n".format(
        pprint.pformat(ctx, indent=2),
        pprint.pformat(data, indent=2),
        pprint.pformat(args, indent=2),
        pprint.pformat(kwargs, indent=2))
    )
    traceback.print_stack(limit=1, file=sys.stderr)


def fix_data_in_target_section(paths, d, fn):
    if hasattr(d, "keys"):
        for k in list(d.keys()):
            if len(paths) > 0 and paths[0] == k:
                name = paths.popleft()
                if len(paths) == 0:
                    fn(d[k])
                fix_data_in_target_section(paths, d[k], fn)
                paths.appendleft(name)
            else:
                fix_data_in_target_section(paths, d[k], fn)
        return d
    elif isinstance(d, (list, tuple)):
        for e in d:
            fix_data_in_target_section(paths, e, fn)
        return d
    else:
        return d


def add_responses_default(ctx, data, *args, **kwargs):
    if not kwargs.get("last"):
        return data

    def add_default(response):
        if not any(x in response for x in ["default", "$ref"]):
            response["default"] = {"$ref": "::default::"}
    fix_data_in_target_section(deque(["paths", "responses"]), data, add_default)
    return data
