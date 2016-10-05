# -*- coding:utf-8 -*-
import re
from . import highlight


def check_orphan_reference(ctx, data, exception_on_fail=False):
    # TODO: remove prefixing_targets
    prefixing_targets = ctx.options["prefixing_targets"]

    refs = set()
    orphans = []
    rx = re.compile("^#/({})/(.+)".format("|".join(prefixing_targets)))

    def collect_refs(d):
        if hasattr(d, "keys"):
            if "$ref" in d:
                refs.add(d["$ref"])
            for v in d.values():
                collect_refs(v)
        elif isinstance(d, (tuple, list)):
            for e in d:
                collect_refs(e)

    def has_ref(ref):
        m = rx.search(ref)
        if m is None:
            return on_error(ref)
        target, name = m.groups()
        subsection = data.get(target) or {}
        if name not in subsection:
            return on_error(ref)

    def on_error(ref):
        msg = "{} is not found.".format(ref)
        orphans.append(ref)
        if not exception_on_fail:
            highlight.show_on_warning(msg)

    collect_refs(data)
    for ref in refs:
        has_ref(ref)

    if exception_on_fail and orphans:
        raise OrphanReferenceError("these references are not found: {}".format("\n".join(orphans)), orphans)
    return orphans


class OrphanReferenceError(ValueError):
    def __init__(self, msg, orphans, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.orphans = orphans
