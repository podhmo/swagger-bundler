from .. import loading
from ..modifiers.ordering import ordering, make_dict
from ..modifiers.composing import transform


def run(ctx, files, outp):
    result = transform(ctx, make_dict(), files, last=True)
    ordered = ordering(result)
    loading.dump(ordered, outp)
