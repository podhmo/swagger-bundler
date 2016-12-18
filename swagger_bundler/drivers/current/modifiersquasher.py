from dictknife import Accessor
from dictknife.operators import Or
from dictknife.chain import chain
from collections import namedtuple
from .chainedhandler import ChainedHandler
from ...langhelpers import highlight, titleize
from ...modifiers.ordering import make_dict
NamespaceFrame = namedtuple("NamespaceFrame", "ns, store")


class NamespaceSquasher(object):
    def __init__(self):
        self.accessor = Accessor(make_dict)

    def transform(self, ctx, data):
        will_removed_items = []

        def found_section(h, walker, d):
            ns = "#{}".format("/".join(h.path[:2]))
            h.store_stack.append(NamespaceFrame(ns=ns, store=d))  # todo: pop stack
            prefix = "".join(h.path[:-1])
            section = h.path[-1]
            sd = d[section]
            for name in list(sd.keys()):
                data[section][prefix + titleize(name)] = sd.pop(name)
            will_removed_items.append(h.path[0])

        def found_ref(h, walker, d):
            ref = d["$ref"]
            if not ref.startswith("#/"):
                highlight("squash: invalid ref {}\n".format(ref))
            section = h.path[0]
            name = h.path[-1]
            new_ref = h.store_stack[-1].ns + titleize(name)
            if new_ref not in d[section]:
                highlight("squash: not found ref {}\n".format(new_ref))
            d["$ref"] = new_ref

        markers = list(ctx.options["prefixing_targets"])  # definitions,response, .. etc
        walker = (chain(context_factory=ChainedHandler)
                  .chain([Or(markers)], on_container=found_section)
                  .chain(["$ref"]))

        for section in markers:
            if section not in data:
                data[section] = make_dict()
            stack = [NamespaceFrame(ns="#/{}".format(section), store=data[section] or {})]
            walker.walk(data, on_container=found_ref, store_stack=stack, ctx=ctx)
            if not data[section]:
                data.pop(section)

        for path in will_removed_items:
            data.pop(path, None)
        return data
