from collections import defaultdict
from dictknife import LooseDictWalker, deepequal, Accessor
from dictknife.operators import Or
from ...modifiers.ordering import make_dict


class CommonDefinitionMerger(object):
    def __init__(self):
        self.accessor = Accessor(make_dict)

    def transform(self, ctx, data):
        tmpstore = defaultdict(lambda: defaultdict(list))  # section -> name -> d

        def found_section(path, d):
            section = path[-1]
            for k in d[section].keys():
                tmpstore[section][k].append(d[section])
        markers = list(ctx.options["prefixing_targets"])  # definitions,response, .. etc
        LooseDictWalker(on_container=found_section).walk([Or(markers)], data)

        for section, items in tmpstore.items():
            for name, vs in items.items():
                if len(vs) <= 1:
                    continue
                ok = True
                left = vs[0]
                for right in vs[1:]:
                    if not deepequal(left[name], right[name]):
                        ok = False
                        break
                if ok:
                    shared = vs[0][name].copy()
                    shared["x-common"] = True
                    self.accessor.assign(data, [section, name], shared)
                    for v in vs:
                        v.pop(name)
