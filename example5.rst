# structure

.. code-block:: bash

   tree
   examples/deref
   ├── color
   │   ├── cmyk.yaml
   │   └── rgb.yaml
   ├── group
   │   └── group.yaml
   ├── main.yaml
   ├── swagger-bundler.ini
   └── x.yaml
   
   2 directories, 6 files
   swagger-bundler bundle main.yaml > generated.yaml

## swagger-bundler.ini(config file)

.. code-block::

   [DEFAULT]
   
   [special_marker]
   # todo: gentle description.
   namespace = x-bundler-namespace
   compose = x-bundler-compose
   concat = x-bundler-concat
   exposed = x-bundler-exposed
   
   [postscript_hook]
   # lambda ctx, data, *args, **kwargs: do_something()
   ## examples:
   # swagger_bundler.postscript:echo
   # or
   # a/b/c/d.py:function_name
   compose =
   bundle =
   add_namespace =
   validate =
   load = swagger_bundler.postscript:deref_support_for_extra_file



deref/color/cmyk.yaml

.. code-block:: yaml

   definitions:
     color:
       type: string
       enum:
         - C
         - M
         - Y
         - K


deref/color/rgb.yaml

.. code-block:: yaml

   definitions:
     color:
       type: string
       enum:
         - r
         - g
         - b


deref/group/group.yaml

.. code-block:: yaml

   definitions:
     group:
       type: string
       enum:
         - A
         - B
         - C
     color:
       $ref: "../color/rgb.yaml#/definitions/color"


deref/main.yaml

.. code-block:: yaml

   x-bundler-compose:
     - x.yaml as X
   
   definitions:
     foo:
       $ref: "./group/group.yaml#/definitions/group"
     color:
       $ref: "group/group.yaml#/definitions/color"


deref/x.yaml

.. code-block:: yaml

   definitions:
     color:
       $ref: color/cmyk.yaml#/definitions/color


## generated.yaml

.. code-block:: yaml

   definitions:
     XColor:
       type: string
       enum:
       - C
       - M
       - Y
       - K
     foo:
       type: string
       enum:
       - A
       - B
       - C
     color:
       type: string
       enum:
       - r
       - g
       - b