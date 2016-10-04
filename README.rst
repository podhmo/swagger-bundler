swagger-bundler
========================================

This is individual tool for bundling swagger definitions.

- python3 only (python3.5+ is better)

setup
----------------------------------------

::

   $ pip install "swagger-bundler[validation]"

or

::

   $ pip install -e git+git@github.com:podhmo/swagger-bundler.git@master#egg=swagger_bundler


getting started
----------------------------------------

0. generating your config file
1. using it

0. generating your config file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

swagger-bundler needs config file for using. so, at first, you must generate config file.

::

   $ swagger-bundler config --init
   generate ~/venv/web/work/swagger-bundler.ini.

The stragegy of finding config file, following below.

Your current working directory is `~/venv/web/work/`. then,

1. finds `~/venv/web/work/swagger-bundler.ini`
2. finds `~/venv/web/swagger-bundler.ini`
3. finds `~/venv/swagger-bundler.ini`
4. finds `~/swagger-bundler.ini`

Config file is not found, then, lookup `~/.swagger-bundle.ini`.

1. how to use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

  Usage: swagger-bundler [OPTIONS] COMMAND [ARGS]...

  Options:
    --help  Show this message and exit.

  Commands:
    bundle    bundles many source files into single file
    concat    concatnates many swagger-definition files
    config    show config
    validate  validates via swagger-2.0 spec


Swagger-bundler has two commands.

- bundle
- concat

bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the main feature. bundling many source files into one single swagger-definition file.

::

   $ swagger-bundler bundle <file.yaml>

The target file of swagger-bundler, it can use three special-marker.

- x-bundler-namespace -- when bundling, using this value as prefix string.
- x-bundler-compose -- importing from other files with namespace
- x-bundler-concat -- importing from other files **without namespace**

For example. the structure of current working directory is such as below,

::

  .
  ├── main.yaml
  └── parts
      ├── common.yaml
      ├── x.yaml
      └── y.yaml


and the content of main.yaml is this.


.. code-block:: yaml

  x-bundler-namespace: ZZZ
  x-bundler-compose:
    - ./parts/x.yaml
    - ./parts/y.yaml
  x-bundler-concat:
    - ./parts/common.yaml

And run it.

.. code-block:: bash

 $ swagger-bundler bundle main.yaml

- definitions in x.yaml, y.yaml are renamed (with namespace). (e.g. foo -> ZZZFoo)
- definitions in common.yaml are not renamed. (e.g. bar -> bar)

The link of `example <example.rst>`_.


qualified import.

.. code-block:: yaml

  x-bundler-namespace: O
  x-bundler-compose:
    - ../parts/x-state.yaml as X
    - ../parts/y-state.yaml as Y

then

- state of x-state.yaml is converting XState, eventually, OXState
- state of y-state.yaml is converting YState, eventually, OYState

the link of `example(qualified import) <example2.rst>`_

concat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is just concatnate files.

::

   $ swagger-bundler concat [file1.yaml] [file2.yaml] ...


appendix:
----------------------------------------

- `watch` option is supported.

watch option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   # installed with [watch]
   $ pip install "swagger-bundler[watch]"
   $ swagger-bundler bundle --watch "*.yaml" --outfile="/tmp/output.yaml" src.yaml
