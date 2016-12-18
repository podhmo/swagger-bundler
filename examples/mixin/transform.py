from swagger_bundler.langhelpers import highlight
from swagger_bundler.postscript import LooseDictWalker


def activate_mixin(ctx, data, marker="x-bundler-mixin", pop_path_list=["x-bundler-types"], *args, **kwargs):
    if not kwargs.get("last"):
        return data

    def emit_mixin(subdata):
        path_list = subdata.pop(marker, None)
        if isinstance(path_list, (str, bytes)):
            path_list = [path_list]
        for path in path_list:
            if not path.startswith("#"):
                highlight("mixin: path={!r} is not found".format(path))
                continue
            target = data
            for name in path.lstrip("#").split("/"):
                if name:
                    target = target[name]
            subdata.update(target)
    w = LooseDictWalker(on_container=emit_mixin)
    w.walk([marker], data)
    for path in pop_path_list:
        data.pop(path, None)
