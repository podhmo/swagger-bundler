from ..modifiers import bundling
from ..modifiers.ordering import ordering
from ..modifiers import orphancheck
from .. import loading


class FileConcatDriver:
    def transform(self, ctx, data, namespace=None):
        return bundling.transform(ctx, data, namespace=namespace)

    def run(self, ctx, inp, outp, namespace=None):
        subcontext = ctx.make_subcontext_from_port(inp)
        result = bundling.transform(subcontext, subcontext.data, namespace=namespace, last=True)

        orphancheck.check_orphan_reference(self.ctx, result, exception_on_fail=False)

        ordered = ordering(result)
        loading.dump(ordered, outp)
