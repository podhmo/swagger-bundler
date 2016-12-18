import re
import traceback
import sys
import pprint
from collections import deque
from collections import OrderedDict
from dictknife import LooseDictWalker as NewerLooseDictWalker
from dictknife.contexts import SimpleContext
from swagger_bundler.langhelpers import guess_name, highlight
from swagger_bundler.modifiers.lifting import SubDefinitionExtractor, ExtractorContext


# backward compatibility
class LooseDictWalker(NewerLooseDictWalker):
    context_factory = SimpleContext


def loose_dict_walker(paths, d, fn):
    w = LooseDictWalker(on_data=fn)
    return w.walk(paths, d)


def echo(ctx, data, *args, **kwargs):
    sys.stderr.write("echo: ctx={}, data={}, args={}, kwargs={}\n".format(
        pprint.pformat(ctx, indent=2),
        pprint.pformat(data, indent=2),
        pprint.pformat(args, indent=2),
        pprint.pformat(kwargs, indent=2))
    )
    traceback.print_stack(limit=1, file=sys.stderr)


def add_responses_default(ctx, data, *args, **kwargs):
    if not kwargs.get("last"):
        return data

    def add_default(response):
        if not any(x in response for x in ["default", "$ref"]):
            response["default"] = {"$ref": "::default::"}
    loose_dict_walker(deque(["paths", "responses"]), data, add_default)
    return data


def lifting_definition(ctx, data, *args, **kwargs):
    w = SubDefinitionExtractor(replace=True)
    for name in list(data["definitions"].keys()):
        prop = data["definitions"].pop(name)
        extracted = w.extract(prop, MarkedExtractorContext([name]))
        extracted[name] = prop
        data["definitions"].update(reversed(extracted.items()))


class MarkedExtractorContext(ExtractorContext):
    def save_object(self, name, definition):
        newdef = super().save_object(name, definition)
        newdef["x-auto-generated"] = True

    def save_array(self, name, definition):
        newdef = super().save_array(name, definition)
        newdef["x-auto-generated"] = True


# for backward compatibility
fix_data_in_target_section = loose_dict_walker


_rx_cache = {}


# todo remove
def deref_support_for_extra_file(ctx, rootdata, *args, targets=tuple(["definitions", "responses", "parameters", "paths"]), **kwargs):
    cache_k = tuple(targets)
    if cache_k not in _rx_cache:
        _rx_cache[cache_k] = re.compile("#/({})/".format("|".join(targets)))
    separator_rx = _rx_cache[cache_k]

    # plain ref :: #/<section>/<name>
    # extra ref :: <path>#/<section>/<name>
    # path :: (<name>/)*<name>
    # section :: 'definitions' | 'parameters' | 'responses'

    def deref(d, ctx, hist):
        if "$ref" not in d:
            return d, hist
        try:
            m = separator_rx.search(d["$ref"])
            if m is None:
                highlight("invalid ref: {}\n".format(d["$ref"]))
                return d, hist

            # plain ref
            if m.start() == 0:
                return d, hist

            # with extra path
            path = d["$ref"][:m.start()]
            section = m.group(1)
            name = d["$ref"][m.end():]
            subctx = ctx.make_subcontext(path)

            # gueesing key (this is heuristic)
            section_store = subctx.data[section]
            for guessed in guess_name(name, subctx.ns):
                if guessed in section_store:
                    hist.append((section, name, subctx))
                    return deref(section_store[guessed], ctx=subctx, hist=hist)
            highlight("not found ref: {}\n".format(d["$ref"]))
            return d, hist
        except (IndexError, ValueError) as e:
            highlight(str(e))

    def on_ref_found(d):
        data, hist = deref(d, ctx, [])
        if hist:
            original_ref = d.pop("$ref")
            section, name, subctx = hist[-1]

            d["$ref"] = "#/{}/{}".format(section, name)
            if section not in rootdata:
                rootdata[section] = OrderedDict()

            if name not in rootdata[section]:
                rootdata[section][name] = data
            elif d == rootdata[section][name]:
                d.pop("$ref")
                d.update(data)
            else:
                refpath = "#/{}/{}".format(section, name)
                if rootdata[section][name] != data:
                    d["x-conflicted"] = original_ref
                    msg = "{} is conflicted. (where file={!r} ref={!r})".format(refpath, ctx.path, original_ref)
                    highlight(msg)
                    d.pop("$ref")
                    d.update(data)

            def merge_properties(d, ctx=None, section=None, name=None):
                if name and section:
                    if section in rootdata and name in rootdata[section]:
                        return
                if name and "$ref" not in d:
                    if section not in rootdata:
                        rootdata[section] = OrderedDict()
                    rootdata[section][name] = d
                    LooseDictWalker(on_container=lambda d: merge_properties(d, ctx=ctx)).walk(["$ref"], d)
                    return

                m = separator_rx.search(d["$ref"])
                if m is None:
                    highlight("invalid ref(merge_properties): {}\n".format(d["$ref"]))
                    return d, hist

                section = m.group(1)
                name = d["$ref"][m.end():]
                if m.start() != 0:
                    # with extra path
                    path = d["$ref"][:m.start()]
                    subctx = ctx.make_subcontext(path)
                    section_store = subctx.data[section]
                    for guessed in guess_name(name, subctx.ns):
                        if guessed in section_store:
                            merge_properties(section_store[guessed], ctx=subctx, section=section, name=guessed)
                elif section in rootdata and name in rootdata[section]:
                    return
                else:
                    # plain ref
                    section_store = ctx.data[section]
                    for guessed in guess_name(name, ctx.ns):
                        if guessed in section_store:
                            return merge_properties(section_store[guessed], ctx=ctx, section=section, name=guessed)

                    subfiles = ctx.detector.detect_compose()
                    for subpath in subfiles:
                        subctx = ctx.make_subcontext(subpath)
                        if section in subctx.data:
                            section_store = subctx.data[section]
                            for guessed in guess_name(name, ctx.ns):
                                if guessed in section_store:
                                    return merge_properties(section_store[guessed], ctx=ctx, section=section, name=guessed)
                    highlight("xinvalid ref(merge_properties): {}\n".format(d["$ref"]))
                    return

            # todo: cache
            LooseDictWalker(on_container=lambda d: merge_properties(d, ctx=subctx)).walk(["$ref"], data)

    w = LooseDictWalker(on_container=on_ref_found)
    q = ["$ref"]
    for section in targets:
        if section in rootdata:
            w.walk(q, rootdata[section])
