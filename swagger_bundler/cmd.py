import sys
import os.path
import click
import logging

from swagger_bundler import make_rootcontext_from_configparser
from swagger_bundler import config as configuration
import swagger_bundler.ordering as ordering
import swagger_bundler.bundling as bundling
import swagger_bundler.composing as composing
import swagger_bundler.loading as loading


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
    ctx = make_rootcontext_from_configparser(parser)
    ordering.setup()
    return ctx


@main.command(help="show config")
@click.argument("file", required=False, default=None)
@click.option("--init/--", help="generates ini file", default=False)
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


@main.command(help="bundles many source files into single file")
@click.argument("file", required=True, type=click.Path(exists=True))
@click.option("--namespace", help="namespace", default=None)
@click.option("--input", help="input format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", help="output format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--watch", help="watch files(glob)", default=None)
@click.option("--no-watch", help="no watch files(glob)", default=None)
@click.option("--outfile", help="output file", default=None)
@click.option("--log/--", help="activate logging(for debug)", default=False)  # TODO: まじめに
def bundle(file, namespace, input, output, watch, no_watch, outfile, log):
    loading.setup(output=output, input=input)

    if log:
        logging.basicConfig(level=logging.DEBUG)

    def run():
        ctx = _prepare()
        with open(file) as rf:
            if outfile:
                with open(outfile, "w") as wf:
                    bundling.run(ctx, rf, wf, namespace=namespace)
            else:
                bundling.run(ctx, rf, sys.stdout, namespace=namespace)
    if not watch:
        run()
    else:
        if outfile is None:
            sys.stderr.write(click.style("--outfile is not set\n", bold=True, fg="yellow"))
        from swagger_bundler.watch import do_watch
        return do_watch(run, path=".", pattern=watch, ignore_pattern=no_watch, outfile=outfile)


@main.command(help="validates via swagger-2.0 spec")
@click.argument("file", required=True, type=click.Path(exists=True))
def validate(file):
    import swagger_bundler.validation as validation
    with open(file) as rf:
        ctx = _prepare()
        validation.run(ctx, rf, sys.stdout)


@main.command(help="concatnates many swagger-definition files")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--input", help="input format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", help="output format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
def concat(files, input, output):
    ctx = _prepare()
    loading.setup(output=output, input=input)
    composing.run(ctx, files, sys.stdout)


def _on_config_file_is_not_found():
    sys.stderr.write("config file not found:\nplease run `swagger-bundler config --init`\n")
    sys.stderr.flush()
    sys.exit(-1)


if __name__ == "__main__":
    main()
