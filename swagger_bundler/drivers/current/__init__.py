# -*- coding:utf-8 -*-
import sys  # NOQA
from ... import loading
from ...modifiers.ordering import ordering
from .modifierreflink import RefResolveLinker
from .modifierconcat import Concat


class RefResolveDriver(object):
    def __init__(self):
        self.linker = RefResolveLinker(self)
        self.concat = Concat(self)
        self.extractor = CommonDefinitionExtractor(self)

    def run(self, basectx, inp, outp, namespace=None):
        ctx = basectx.make_subcontext_from_port(inp)
        result = self.transform(ctx, ctx.data, namespace=namespace, last=True)
        ordered = ordering(result)
        loading.dump(ordered, outp)

    def transform(self, ctx, data, namespace=None, last=False):
        self.linker.transform(ctx, data)
        self.concat.transform(ctx, data)
        if last:
            self.extractor.transform(ctx, data)
            # todo: ref-fixer

        # TODO: handling code
        postscript = ctx.options["postscript_hook"].get("bundle")
        if postscript and callable(postscript):
            postscript_result = postscript(ctx, data, namespace=namespace, last=last)
            if postscript_result is not None:
                data = postscript_result
        return data

from collections import defaultdict
from dictknife import LooseDictWalker, deepequal, Accessor
from dictknife.operators import Or
from ...modifiers.ordering import make_dict


class CommonDefinitionExtractor(object):
    def __init__(self, driver):
        self.driver = driver
        self.accessor = Accessor(make_dict)

    def transform(self, ctx, data):
        tmpstore = defaultdict(lambda: defaultdict(list))  # section -> name -> d

        def found_section(path, d):
            section = path[-1]
            for k in d.keys():
                tmpstore[section][k].append((path[:-1], d))
        markers = list(ctx.options["prefixing_targets"])  # definitions,response, .. etc
        LooseDictWalker(on_data=found_section).walk([Or(markers)], data)

        for section, items in tmpstore.items():
            for name, vs in items.items():
                if len(vs) <= 1:
                    continue
                ok = True
                left = vs[0]
                for _, right in vs[1:]:
                    if not deepequal(left[name], right[name]):
                        ok = False
                        break
                if ok:
                    shared = vs[0][name].copy()
                    shared["x-common"] = True
                    self.accessor.assign(data, [section, name], shared)
                    for ns_path, v in vs:
                        v.pop(name)
