import click
import sys
import swagger_bundler.mangling as mangling
import swagger_bundler.bundling as bundling
import swagger_bundler.ordering as ordering
import swagger_bundler.generating as generating


@click.group()
@click.pass_context
def main(ctx):
    return ctx.get_help()


@main.command()
@click.argument("files", nargs=-1, required=True)
def bundle(files):
    ordering.setup()
    bundling.bundle(files, sys.stdout)


@main.command()
@click.argument("file", required=False)
@click.option("--namespace", "-ns", default=None)
def mangle(file, namespace):
    ordering.setup()
    if file is None:
        mangling.mangle(sys.stdin, sys.stdout, namespace=namespace)
    else:
        with open(file) as rf:
            mangling.mangle(rf, sys.stdout, namespace=namespace)


@main.command(help="generating bundled yaml. (see: namespace and bundle field)")
@click.argument("file", required=True)
def generate(file):
    ordering.setup()
    if file is None:
        generating.generate(sys.stdin, sys.stdout)
    else:
        with open(file) as rf:
            generating.generate(rf, sys.stdout)


if __name__ == "__main__":
    main()
