import click
import sys
import swagger_bundler.mangling as mangling
import swagger_bundler.bundling as bundling
import swagger_bundler.ordering as ordering


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


if __name__ == "__main__":
    main()
