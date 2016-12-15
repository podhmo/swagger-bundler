import sys
from functools import partial
from . import LooseDictWalker
from .. import highlight

"""
json reference examples

- "#/foo/bar"
- "./#foo/bar"
- "/foo/bar/#foo/bar"
"""


# e.g. ref="./foo#/foo/bar", path="./foo", nodes=["foo", "bar"]
def on_external(walker, ctx, ref, path, nodes):
    return ref


class JSONRefWalker(object):
    def __init__(self, on_container=None, on_data=None, on_external=None):
        self.on_container = on_container
        self.on_data = on_data
        self.on_external = on_external

    def at_update_ref(self, d, ref):
        d["$ref"] = ref

    def at_ref(self, ctx, d):
        ref = d["$ref"]
        print("@ ref", ctx.path, ":", d["$ref"], file=sys.stderr)
        left_and_right = [x.strip("/") for x in ref.split("#", 1)]
        if len(left_and_right) == 0:
            msg = "  on where={!r}, invalid ref {!r}\n".format(ctx.path, ref)
            highlight.show_on_warning(msg)
            return ref
        elif left_and_right[0] == "":
            internal_ref = self.at_current(ctx, ref, left_and_right[1].split("/"))
            self.at_update_ref(d, internal_ref)
        else:
            src, name_path = left_and_right
            names = name_path.split("/")
            internal_ref = self.on_external(self, ctx, ref, src, names)
            self.at_update_ref(d, internal_ref)

    def at_current(self, ctx, ref, names):
        print("@@@ current", ctx.path, ":", ref, file=sys.stderr)
        # using
        pt = self.at_container_by_names(ctx.data, names)
        if pt is None:
            msg = "  on where={!r}, ref {!r} is not found\n".format(ctx.path, ref)
            highlight.show_on_warning(msg)
            return ref

        if self.on_container is not None:
            self.on_container(self, ctx, ref, pt, names[-1])
        if self.on_data is not None:
            self.on_data(self, ctx, ref, pt[names[-1]])
        return ref

    def walk(self, ctx, data):
        walker = LooseDictWalker(on_container=partial(self.at_ref, ctx))
        return walker.walk(["$ref"], data)

    # todo: rename

    def at_container_by_names(self, data, names):
        pt = data
        for name in names[:-1]:
            if name not in pt:
                return None
            pt = pt[name]
        if names[-1] not in pt:
            return None
        return pt
