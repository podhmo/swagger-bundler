import click
import sys
from swagger_bundler import make_rootcontext
import swagger_bundler.mangling as mangling
import swagger_bundler.bundling as bundling
import swagger_bundler.ordering as ordering
import swagger_bundler.generating as generating


@click.group()
@click.pass_context
def main(ctx):
    return ctx.get_help()


def _prepare():
    ctx = make_rootcontext()
    ordering.setup()
    return ctx


@main.command()
@click.argument("files", nargs=-1, required=True)
def bundle(files):
    ctx = _prepare()
    bundling.bundle(ctx, files, sys.stdout)


@main.command()
@click.argument("file", required=False)
@click.option("--namespace", "-ns", default=None)
def mangle(file, namespace):
    ctx = _prepare()
    if file is None:
        mangling.mangle(ctx, sys.stdin, sys.stdout, namespace=namespace)
    else:
        with open(file) as rf:
            mangling.mangle(ctx, rf, sys.stdout, namespace=namespace)


@main.command(help="generating bundled yaml. (see: namespace and bundle field)")
@click.argument("file", required=True)
def generate(file):
    ctx = _prepare()
    if file is None:
        generating.generate(ctx, sys.stdin, sys.stdout)
    else:
        with open(file) as rf:
            generating.generate(ctx, rf, sys.stdout)


if __name__ == "__main__":
    main()
