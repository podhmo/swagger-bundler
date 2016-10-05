# -*- coding: utf-8 -*-

# almost stolen from: https://github.com/ccpgames/jsonschema-errorprinter

import json
import os.path
from io import StringIO

from jsonschema import validate
from jsonschema import FormatChecker, ValidationError
from . import loading
from . import orphancheck


def generate_validation_error_report(e, json_object, lines_before=7, lines_after=7):
    """
    Generate a detailed report of a schema validation error.

    'e' is a jsonschema.ValidationError exception that errored on
    'json_object'.

    Steps to discover the location of the validation error:
    1. Traverse the json object using the 'path' in the validation exception
       and replace the offending value with a special marker.
    2. Pretty-print the json object indendented json text.
    3. Search for the special marker in the json text to find the actual
       line number of the error.
    4. Make a report by showing the error line with a context of
      'lines_before' and 'lines_after' number of lines on each side.
    """

    if json_object is None:
        return "'json_object' cannot be None."

    if not e.path:
        if e.schema_path and e.validator_value:
            return "Toplevel:\n\t{}".format(e.message)
        else:
            return str(e)

    marker = "3fb539deef7c4e2991f265c0a982f5ea"

    # Find the object that is erroring, and replace it with the marker.
    ob_tmp = json_object
    for entry in list(e.path)[:-1]:
        ob_tmp = ob_tmp[entry]

    orig, ob_tmp[e.path[-1]] = ob_tmp[e.path[-1]], marker

    # Pretty print the object and search for the marker.
    json_error = json.dumps(json_object, indent=4)
    io = StringIO(json_error)
    errline = None

    for lineno, text in enumerate(io):
        if marker in text:
            errline = lineno
            break

    if errline is not None:
        # Re-create report.
        report = []
        ob_tmp[e.path[-1]] = orig
        json_error = json.dumps(json_object, indent=4)
        io = StringIO(json_error)

        for lineno, text in enumerate(io):
            if lineno == errline:
                line_text = "{:4}: >>>".format(lineno + 1)
            else:
                line_text = "{:4}:    ".format(lineno + 1)
            report.append(line_text + text.rstrip("\n"))

        report = report[max(0, errline - lines_before):errline + 1 + lines_after]

        s = "Error in line {}:\n".format(errline + 1)
        s += "\n".join(report)
        s += "\n\n" + str(e).replace("u'", "'")
    else:
        s = str(e)
    return s


def check_json(json_object, schema, context=None):
    try:
        validate(json_object, schema, format_checker=FormatChecker())
    except ValidationError as e:
        report = generate_validation_error_report(e, json_object)
        if context:
            return "Schema check failed for '{}'\n{}".format(context, report)
        else:
            return "Schema check failed.\n{}".format(report)


def run(ctx, inp, out):
    here = os.path.abspath(os.path.dirname(__file__))
    schema_path = os.path.join(here, "schema/swagger-2.0.json")

    with open(schema_path) as rf:
        schema = json.load(rf)
    data = loading.load(inp)

    def fix(d, after_responses=False):
        if hasattr(d, "keys"):
            for k in list(d.keys()):
                if k == "responses":
                    d[fix(k, after_responses=True)] = fix(d.pop(k), after_responses=True)
                else:
                    d[fix(k, after_responses=after_responses)] = fix(d.pop(k), after_responses=after_responses)
            return d
        elif isinstance(d, (list, tuple)):
            for e in d:
                fix(e, after_responses=after_responses)
            return d
        elif after_responses and isinstance(d, int):
            return str(d)
        else:
            return d
    out.write(str(check_json(fix(data), schema)))

    # TODO: handling code
    postscript = ctx.options["postscript_hook"].get("validate")
    if postscript and callable(postscript):
        postscript(ctx, data, last=True)

    orphancheck.check_orphan_reference(ctx, data, exception_on_fail=True)
