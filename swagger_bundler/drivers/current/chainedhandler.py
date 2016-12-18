from dictknife.chain import ChainedContext
from .refspec import RefSpec


class ChainedHandler(ChainedContext):  # Renamed. Because it is confusing that swagger_bundler has also context.
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
