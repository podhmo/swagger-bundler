from dictknife import Accessor, deepmerge
from dictknife import LooseDictWalker
from ...modifiers.ordering import make_dict


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
