import json
from dictknife import Accessor, deepequal
from dictknife.operators import Or
from dictknife.chain import chain
from collections import namedtuple
from .chainedhandler import ChainedHandler
from ...langhelpers import highlight
from ...modifiers.ordering import make_dict


StoreFrame = namedtuple("StoreFrame", "path store")


"""
json reference examples

# extra ref :: <path>#/<namespace>*<section>/<name>
# path :: (<name>/)*<name>
# namespace :: (<name>/)*
# section :: 'definitions' | 'parameters' | 'responses'

examples

- "#/foo/bar"
- "./#foo/bar"
- "/foo/bar/#foo/bar"
"""


class RefResolveLinker(object):
    accessor = Accessor(make_dict=make_dict)

    def __init__(self, driver):
        self.driver = driver

    def transform(self, ctx, data):
        def found_namespace(h, walker, d):
            if "$ref" in d:
                found_ref(h, walker, d)
            else:
                path = h.path[:-1]
                h.store_stack.append(StoreFrame(path=path, store=self.accessor.access(data, path)))  # todo: pop stack

        def on_internal(subctx, h, walker, refspec):
            # print("@@@ internal", ctx.path, ":", refspec.ref, file=sys.stderr)
            d = self.accessor.maybe_access_container(subctx.data, refspec.ref_path)
            if d is None:
                msg = "  on where={!r}, ref {!r} is not found\n".format(subctx.path, refspec.ref)
                highlight(msg)
                return refspec.ref
            k = refspec.ref_path[-1]

            if "$ref" in d[k]:
                d[k]["$ref"] = found_ref(h, walker, d[k]["$ref"])
            else:
                store = h.current_store
                container = self.accessor.maybe_access_container(store, refspec.ref_path)
                if container is None:
                    # print("@@@@@ assign", refspec.ref, "from ", subctx.path, "value", json.dumps(d[k]), file=sys.stderr)
                    self.accessor.assign(store, refspec.ref_path, d[k].copy())
                    # print(json.dumps(store, indent=2), file=sys.stderr)
                elif "$ref" in container[k]:
                    # print("@@@@@ override", subctx.path, d[k], container)
                    container[k] = d[k].copy()
                elif not deepequal(container[k], d[k]):
                    # print("@@@@@ merge", subctx.path)
                    msg = "  on where={!r}, ref {!r} is conflicted with {!r}\n".format(subctx.path, refspec.ref, ctx.path)
                    highlight(msg)
                    msg = "    {!r}: {!r}".format(ctx.path, json.dumps(container[k]))
                    highlight(msg)
                    msg = "    {!r}: {!r}".format(subctx.path, json.dumps(d[k]))
                    highlight(msg)
                walker.walk(["$ref"], d[k], ctx=h.new_child(ctx=subctx))  # xxx
            return "/".join(["#", *refspec.ref_path])

        def on_external(ctx, h, walker, refspec):
            subctx = ctx.make_subcontext(refspec.file_path)
            # print("@@ external", ctx.path, "->", subctx.path, file=sys.stderr)
            # todo: cache
            self.driver.transform(subctx, subctx.data)
            internal_ref = "/".join(["#", *refspec.ref_path])
            on_internal(subctx, h, walker, refspec)
            return internal_ref

        def found_ref(h, walker, d):
            refspec = h.detect_refspec(d["$ref"])
            if refspec.is_broken():
                msg = "  on where={!r}, invalid ref {!r}\n".format(ctx.path, refspec.ref)
                highlight(msg)
                return refspec.ref
            elif refspec.is_external():
                d["$ref"] = on_external(h.ctx, h, walker, refspec)
            else:
                d["$ref"] = on_internal(h.ctx, h, walker, refspec)

        markers = list(ctx.options["prefixing_targets"]) + ["$ref"]  # definitions,response, .. etc

        walker = (chain(context_factory=ChainedHandler)
                  .chain([Or(markers)], on_container=found_namespace)
                  .chain(["$ref"]))
        walker.walk(data, on_container=found_ref, store_stack=[StoreFrame(path=[], store=data)], ctx=ctx)
        return data
