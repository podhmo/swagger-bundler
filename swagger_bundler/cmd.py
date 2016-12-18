import sys
import os.path
import click
import logging
import swagger_bundler.config as configuration
import swagger_bundler.loading as loading
from swagger_bundler.drivers.concat import run as concat_run


@click.group()
@click.pass_context
def main(ctx_):
    # ctx_ is click's context. not swagger_bundler.context.Context.
    return ctx_.get_help()


@main.command(help="show config")
@click.argument("file", required=False, default=None)
@click.option("--init/--", help="generates ini file", default=False)
def config(file, init):
    config_path = configuration.pickup_config(os.getcwd(), default=None)
    if init:
        return configuration.init_config(".")
    else:
        if config_path is None:
            return configuration.exit_config_file_is_not_found()
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
        ctx = configuration.setup()
        with open(file) as rf:
            if outfile:
                with open(outfile, "w") as wf:
                    ctx.driver.run(ctx, rf, wf, namespace=namespace)
            else:
                ctx.driver.run(ctx, rf, sys.stdout, namespace=namespace)
    if not watch:
        run()
    else:
        if outfile is None:
            sys.stderr.write(click.style("--outfile is not set\n", bold=True, fg="yellow"))
        from swagger_bundler.watch import do_watch
        return do_watch(run, path=".", pattern=watch, ignore_pattern=no_watch, outfile=outfile)


@main.command(help="migration from older format")
@click.argument("file", required=True, type=click.Path(exists=True))
@click.option("--src", required=True)
@click.option("--dst", required=True)
@click.option("--dry-run/--force", default=False)
@click.option("--input", help="input format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", help="output format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--log/--", help="activate logging(for debug)", default=False)  # TODO: まじめに
def migrate(file, src, dst, dry_run, input, output, log):
    loading.setup(output=output, input=input)

    if log:
        logging.basicConfig(level=logging.DEBUG)
    from swagger_bundler.drivers import MigrationDriver
    ctx = configuration.setup(driver_class=MigrationDriver)
    with open(file) as rf:
        ctx.driver.run(ctx, rf, sys.stdout)
        ctx.driver.emit(ctx, replacer=lambda x: x.replace(src, dst), dry_run=dry_run)


@main.command(help="validates via swagger-2.0 spec")
@click.argument("file", required=True, type=click.Path(exists=True))
def validate(file):
    import swagger_bundler.validation as validation
    with open(file) as rf:
        ctx = configuration.setup()
        validation.run(ctx, rf, sys.stdout)


@main.command(help="concatnates many swagger-definition files")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--input", help="input format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
@click.option("--output", help="output format", type=click.Choice([loading.Format.yaml, loading.Format.json]))
def concat(files, input, output):
    ctx = configuration.setup()
    loading.setup(output=output, input=input)
    concat_run(ctx, files, sys.stdout)


if __name__ == "__main__":
    main()
