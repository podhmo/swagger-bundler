from dictknife import Accessor, deepmerge
from dictknife import LooseDictWalker
from dictknife.contexts import SimpleContext
from ...modifiers.ordering import make_dict


class Concat(object):
    accessor = Accessor(make_dict=make_dict)

    def __init__(self, driver):
        self.driver = driver
        self.reffixer = RefFixer()

    def transform(self, ctx, data):
        concat_marker = ctx.exact_tagname("concat")

        def found_concat(path, d):
            subfiles = d.pop(concat_marker)
            additional = make_dict()
            for src in subfiles:
                # todo: cache
                subctx = ctx.make_subcontext(src)
                additional = deepmerge(additional, self.driver.transform(subctx, subctx.data))

            self.reffixer.fix(path[:-1], additional)
            d.update(deepmerge(d, additional))

        walker = LooseDictWalker(on_container=found_concat)
        walker.walk([concat_marker], data)
        return data


class RefFixer(object):
    def __init__(self):
        self.walker = LooseDictWalker(on_container=self.found_ref)

    def fix(self, path, d):
        prefix = "#/{}/".format("/".join(path))
        self.walker.walk(["$ref"], d, ctx=FixRefHandler(prefix))

    def found_ref(self, h, d):
        d["$ref"] = d["$ref"].replace("#/", h.prefix)


class FixRefHandler(SimpleContext):
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, walker, fn, value):
        return fn(self, value)
