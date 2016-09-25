import sys
import os.path
import click

from swagger_bundler import make_rootcontext
from swagger_bundler import config as configuration
import swagger_bundler.mangling as mangling
import swagger_bundler.bundling as bundling
import swagger_bundler.ordering as ordering
import swagger_bundler.generating as generating


@click.group()
@click.pass_context
def main(ctx_):
    # ctx_ is click's context. not swagger_bundler.context.Context.
    return ctx_.get_help()


def _prepare():
    config_path = configuration.pickup_config(os.getcwd()) or "~/.{}".format(configuration.CONFIG_NAME)
    if not os.path.exists(config_path):
        return _on_config_file_is_not_found()
    parser = configuration.load_config(config_path)
    ctx = make_rootcontext(parser)
    ordering.setup()
    return ctx


@main.command()
@click.argument("file", required=False, default=None)
@click.option("--init/--", default=False)
def config(file, init):
    config_path = configuration.pickup_config(os.getcwd(), default=None)
    if init:
        config_path = config_path or os.path.join(os.getcwd(), configuration.CONFIG_NAME)
        return configuration.init_config(config_path)
    else:
        if config_path is None:
            return _on_config_file_is_not_found()
        config = configuration.load_config(config_path)
        return configuration.describe_config(config, sys.stdout)


@main.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
def bundle(files):
    ctx = _prepare()
    bundling.bundle(ctx, files, sys.stdout)


@main.command()
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option("--namespace", "-ns", default=None)
def mangle(file, namespace):
    ctx = _prepare()
    if file is None:
        mangling.mangle(ctx, sys.stdin, sys.stdout, namespace=namespace)
    else:
        with open(file) as rf:
            mangling.mangle(ctx, rf, sys.stdout, namespace=namespace)


@main.command(help="generating bundled yaml. (see: namespace and bundle field)")
@click.argument("file", required=True, type=click.Path(exists=True))
def generate(file):
    ctx = _prepare()
    if file is None:
        generating.generate(ctx, sys.stdin, sys.stdout)
    else:
        with open(file) as rf:
            generating.generate(ctx, rf, sys.stdout)


def _on_config_file_is_not_found():
    sys.stderr.write("config file not found:\nplease run `swagger-bundler config --init`\n")
    sys.stderr.flush()
    sys.exit(-1)


if __name__ == "__main__":
    main()
