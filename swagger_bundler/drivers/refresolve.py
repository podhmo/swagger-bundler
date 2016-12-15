# -*- coding:utf-8 -*-
import sys  # NOQA
import json
from ..walkers import JSONRefWalker
from .. import highlight
from ..modifiers.ordering import make_dict
from ..modifiers.ordering import ordering
from .. import loading


def assign_by_names(pt, ref, value):
    names = ref[2:].split("/")
    for name in names[:-1]:
        if name not in pt:
            pt[name] = make_dict()
        pt = pt[name]
    pt[names[-1]] = value


def deep_equal_check(ctx0, ctx1, d0, d1):
    def check(left, right):
        if hasattr(left, "keys"):
            for k in left.keys():
                if k not in right:
                    return False
                return check(left[k], right[k])
        elif isinstance(left, (list, tuple)):
            if len(left) != len(right):
                return False
            for x, y in zip(left, right):
                if not check(x, y):
                    return False
        else:
            return left == right
    return check(d0, d1) and check(d1, d0)


class RefResolveDriver(object):
    def transform(self, ctx, store, namespace=None, last=False):
        def on_has_ref(walker, subctx, ref, d, k):
            if "$ref" in d[k]:
                d[k]["$ref"] = walker.at_ref(subctx, d[k]["$ref"])
            else:
                walker.walk(subctx, d[k])
                if not ref.startswith("#/"):
                    msg = "  on where={!r}, not startswith #/ {!r}\n".format(subctx.path, ref)
                    highlight.show_on_warning(msg)
                    return ref

                container = walker.at_container_by_names(store, ref[2:].split("/"))
                if container is None:
                    print("@@@@@ assign", ref, "from ", subctx.path, "value", json.dumps(d[k]), file=sys.stderr)
                    assign_by_names(store, ref, d[k])
                    print(json.dumps(store, indent=2), file=sys.stderr)
                elif "$ref" in container:
                    container[k] = d[k]
                elif not deep_equal_check(ctx, subctx, container[k], d[k]):
                    msg = "  on where={!r}, ref {!r} is conflicted with {!r}\n".format(subctx.path, ref, ctx.path)
                    highlight.show_on_warning(msg)
                    msg = "    {!r}: {!r}".format(ctx.path, json.dumps(container[k]))
                    highlight.show_on_warning(msg)
                    msg = "    {!r}: {!r}".format(subctx.path, json.dumps(d[k]))
                    highlight.show_on_warning(msg)
                walker.walk(subctx, d[k])

        def on_external_resource(walker, ctx, ref, src, names):
            subctx = ctx.make_subcontext(src)
            print("@@ external", ctx.path, "->", subctx.path, file=sys.stderr)
            internal_ref = ref.replace(src, "")
            container = walker.at_container_by_names(store, names)
            if not container:
                walker.at_current(subctx, internal_ref, names)
            return internal_ref

        walker = JSONRefWalker(on_container=on_has_ref, on_external=on_external_resource)
        walker.walk(ctx, store)

        # TODO: handling code
        postscript = ctx.options["postscript_hook"].get("bundle")
        if postscript and callable(postscript):
            postscript_result = postscript(ctx, store, namespace=namespace, last=last)
            if postscript_result is not None:
                store = postscript_result
        return store

    def run(self, basectx, inp, outp, namespace=None):
        ctx = basectx.make_subcontext_from_port(inp)
        result = self.transform(ctx, ctx.data, namespace=namespace, last=True)
        ordered = ordering(result)
        loading.dump(ordered, outp)
