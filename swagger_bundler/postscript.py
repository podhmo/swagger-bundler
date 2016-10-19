import traceback
import sys
import pprint
import copy
from collections import deque
from collections import OrderedDict


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


class LooseDictWalker:
    def __init__(self, on_container=None, on_data=None):
        self.on_container = on_container
        self.on_data = on_data

    def on_found(self, d, k):
        if self.on_container is not None:
            self.on_container(d)
        if self.on_data is not None:
            self.on_data(d[k])

    def walk(self, paths, d):
        return self._walk(deque(paths), d)

    def _walk(self, paths, d):
        if hasattr(d, "keys"):
            for k in list(d.keys()):
                if len(paths) > 0 and paths[0] == k:
                    name = paths.popleft()
                    self._walk(paths, d[k])
                    if len(paths) == 0:
                        self.on_found(d, k)
                    paths.appendleft(name)
                else:
                    self._walk(paths, d[k])
            return d
        elif isinstance(d, (list, tuple)):
            for e in d:
                self._walk(paths, e)
            return d
        else:
            return d


def loose_dict_walker(paths, d, fn):
    w = LooseDictWalker(on_data=fn)
    return w.walk(paths, d)


# for backward compatibility
fix_data_in_target_section = loose_dict_walker


class ExtractorContext:
    def __init__(self, path, r=None):
        self.path = path
        self.r = r or OrderedDict()

    def full_name(self):
        return "".join(self.path)

    def add_name(self, name):
        self.path.append(name.title())

    def add_array_item(self):
        self.add_name("item")

    def pop_name(self):
        self.path.pop()

    def save_object(self, name, definition):
        newdef = self.r.__class__()
        newdef["type"] = "object"
        newdef["properties"] = definition
        self.r[name] = newdef
        return newdef

    def save_array(self, name, definition):
        newdef = self.r.__class__()
        newdef["type"] = "array"
        newdef["items"] = definition
        self.r[name] = newdef
        return newdef


class MarkedExtractorContext(ExtractorContext):
    def save_object(self, name, definition):
        newdef = super().save_object(name, definition)
        newdef["x-auto-generated"] = True

    def save_array(self, name, definition):
        newdef = super().save_array(name, definition)
        newdef["x-auto-generated"] = True


class SubDefinitionExtractor:
    def __init__(self, replace=True):
        self.replace = replace

    def extract(self, data, ctx):
        self._extract(data, ctx)
        for k in list(ctx.r.keys()):
            ctx.r[k] = copy.deepcopy(ctx.r[k])
        return ctx.r

    def _extract(self, data, ctx):
        typ = data.get("type")
        if typ == "array" and "items" in data:
            return self.on_array_has_items(data, ctx)
        elif (typ is None or typ == "object") and "properties" in data:
            return self.on_object_has_properties(data, ctx)
        else:
            return data

    def return_definition(self, definition, fullname, typ="object"):
        if self.replace:
            return {"$ref": "#/definitions/{}".format(fullname)}
        else:
            return definition

    def on_object_has_properties(self, data, ctx):
        for name in data["properties"]:
            ctx.add_name(name)
            data["properties"][name] = self._extract(data["properties"][name], ctx)
            ctx.pop_name()

        if "$ref" in data:
            return data
        fullname = ctx.full_name()
        ctx.save_object(fullname, data["properties"])
        return self.return_definition(data, fullname, typ="object")

    def on_array_has_items(self, data, ctx):
        if "$ref" in data["items"]:
            return data
        fullname = ctx.full_name()
        ctx.add_array_item()
        data["items"] = self._extract(data["items"], ctx)
        ctx.save_array(fullname, data["items"])
        ctx.pop_name()
        return self.return_definition(data, fullname, typ="array")
