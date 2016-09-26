import sys
import os.path
import click

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
    parser = _get_config_parser()
    ctx = make_rootcontext_from_configparser(parser)
    ordering.setup()
    return ctx


def _get_config_parser():
    config_path = configuration.pickup_config(os.getcwd()) or "~/.{}".format(configuration.CONFIG_NAME)
    if not os.path.exists(config_path):
        return _on_config_file_is_not_found()
    return configuration.load_config(config_path)


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


@main.command(help="bundle yaml")
@click.argument("file", required=True, type=click.Path(exists=True))
@click.option("--input", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--log/--", default=False)  # TODO: まじめに
def bundle(file, input, output, log):
    ctx = _prepare()
    loading.setup(output=output, input=input)
    if log:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    with open(file) as rf:
        bundling.run(ctx, rf, sys.stdout)


@main.command()
@click.argument("file", required=True, type=click.Path(exists=True))
def validate(file):
    import swagger_bundler.validation as validation
    with open(file) as rf:
        validation.run(rf, sys.stdout)


@main.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--input", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", type=click.Choice([loading.Format.yaml, loading.Format.json]))
def concat(files, input, output):
    ctx = _prepare()
    loading.setup(output=output, input=input)
    composing.run(ctx, files, sys.stdout)


@main.command()
def init():
    parser = _get_config_parser()
    template = """\
# special marker for swagger-bundler
# {c[special_marker][namespace]}:
# {c[special_marker][compose]}:
# {c[special_marker][concat]}:

# specification: https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md
# sample: http://editor.swagger.io/#/

swagger: {c[template][swagger]!r}
info:
  title: {c[template][info_title]}
  description: {c[template][info_description]}
  version: {c[template][info_version]}
host: {c[template][host]}
schemes:
- {c[template][schemes]}
basePath: {c[template][basePath]}
produces:
-  {c[template][produces]}
consumes:
-  {c[template][produces]}

definitions:

responses:

paths:
"""
    sys.stdout.write(template.format(c=parser))


def _on_config_file_is_not_found():
    sys.stderr.write("config file not found:\nplease run `swagger-bundler config --init`\n")
    sys.stderr.flush()
    sys.exit(-1)


if __name__ == "__main__":
    main()
