# -*- coding:utf-8 -*-
import sys  # NOQA
import json
from dictknife import Accessor, deepequal, deepmerge, LooseDictWalker
from dictknife.operators import Or
from dictknife.chain import chain, ChainedContext
from collections import namedtuple
from ... import highlight
from ... import loading
from ...modifiers.ordering import make_dict
from ...modifiers.ordering import ordering


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


"""
step

- detect namespace
- resolve current space
- concatnation
"""

StoreFrame = namedtuple("StoreFrame", "path store")


class RefSpec(object):
    def __init__(self, ref, file_path, ref_path):
        self.ref = ref
        self.file_path = file_path
        self.ref_path = ref_path

    def is_external(self):
        return self.file_path is not None

    def is_broken(self):
        return self.ref_path is None

    @classmethod
    def broken(cls, ref):
        return cls(ref, None, None)

    @classmethod
    def internal(cls, ref, ref_path):
        return cls(ref, None, ref_path)

    @classmethod
    def external(cls, ref, file_path, ref_path):
        return cls(ref, file_path, ref_path)


class Handler(ChainedContext):  # Renamed. Because it is confusing that swagger_bundler has also context.
    def __init__(self, *args, store_stack=None, ctx=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_stack = store_stack or []
        self.ctx = ctx

    def new_child(self, *args, ctx=None, store_stack=None, **kwargs):
        new = super().new_child(*args, **kwargs)
        new.store_stack = store_stack or self.store_stack[:]  # xxx
        new.ctx = ctx or self.ctx
        return new

    @property
    def current_store(self):
        return self.store_stack[-1].store

    @property
    def current_path(self):
        return self.store_stack[-1].path

    def detect_refspec(self, ref):
        left_and_right = ref.split("#", 1)
        if len(left_and_right) == 0:
            return RefSpec.broken(ref)
        elif left_and_right[0] == "":
            return RefSpec.internal(ref, left_and_right[1].strip("/").split("/"))
        else:
            left, right = left_and_right
            return RefSpec.external(ref, left, right.strip("/").split("/"))


class RefResolveDriver(object):
    def __init__(self):
        self.linker = RefResolveLinker(self)
        self.concat = Concat(self)

    def run(self, basectx, inp, outp, namespace=None):
        ctx = basectx.make_subcontext_from_port(inp)
        result = self.transform(ctx, ctx.data, namespace=namespace, last=True)
        ordered = ordering(result)
        loading.dump(ordered, outp)

    def transform(self, ctx, data, namespace=None, last=False):
        self.linker.transform(ctx, data)
        self.concat.transform(ctx, data)
        return data


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
                highlight.show_on_warning(msg)
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
                    highlight.show_on_warning(msg)
                    msg = "    {!r}: {!r}".format(ctx.path, json.dumps(container[k]))
                    highlight.show_on_warning(msg)
                    msg = "    {!r}: {!r}".format(subctx.path, json.dumps(d[k]))
                    highlight.show_on_warning(msg)
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
                highlight.show_on_warning(msg)
                return refspec.ref
            elif refspec.is_external():
                d["$ref"] = on_external(h.ctx, h, walker, refspec)
            else:
                d["$ref"] = on_internal(h.ctx, h, walker, refspec)

        markers = list(ctx.options["prefixing_targets"]) + ["$ref"]  # definitions,response, .. etc

        walker = (chain(context_factory=Handler)
                  .chain([Or(markers)], on_container=found_namespace)
                  .chain(["$ref"]))
        walker.walk(data, on_container=found_ref, store_stack=[StoreFrame(path=[], store=data)], ctx=ctx)
        return data


class Concat(object):
    accessor = Accessor(make_dict=make_dict)

    def __init__(self, driver):
        self.driver = driver

    def transform(self, ctx, data):
        concat_marker = ctx.exact_tagname("concat")

        def found_concat(path, d):
            subfiles = d.pop(concat_marker)
            additional = make_dict()
            for src in subfiles:
                # todo: cache
                subctx = ctx.make_subcontext(src)
                additional = deepmerge(additional, self.driver.transform(subctx, subctx.data))
            d.update(deepmerge(d, additional))

        walker = LooseDictWalker(on_container=found_concat)
        walker.walk([concat_marker], data)
        return data
