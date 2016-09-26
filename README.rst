swagger-bundler
========================================

this is individual tool for bundling swagger definitions.

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

0. generate your config file
1. use it

0. generating your config file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

swagger-bundler needs config file for using. so, at first, you must generate config file.

::

   $ swagger-bundler config --init
   generate ~/venv/web/work/swagger-bundler.ini.

the stragegy of finding config file, following below.

your current working directory is `~/venv/web/work/`. then,

1. find `~/venv/web/work/swagger-bundler.ini`
2. find `~/venv/web/swagger-bundler.ini`
3. find `~/venv/swagger-bundler.ini`
4. find `~/swagger-bundler.ini`

config file is not found. then lookup `~/.swagger-bundle.ini`.

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


swagger-bundler has two commands.

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

For example. the structure of current working directory is such as below.

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

and run it.

.. code-block:: bash

 $ swagger-bundler bundle main.yaml

- definitions in x.yaml, y.yaml are renamed (with namespace). (e.g. foo -> ZZZFoo)
- definitions in common.yaml are not renamed. (e.g. bar -> bar)

link of `example <example.rst>`_.

concat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is just concatnate files.

::

   $ swagger-bundler concat [file1.yaml] [file2.yaml] ...
