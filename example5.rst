# structure

.. code-block:: bash

   tree
   examples/deref
   ├── color
   │   ├── cmyk.yaml
   │   └── rgb.yaml
   ├── group
   │   ├── group.yaml
   │   ├── numbers.yaml
   │   └── primitive.yaml
   ├── main.yaml
   ├── swagger-bundler.ini
   └── x.yaml
   
   2 directories, 8 files
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

   x-bundler-concat:
     - numbers.yaml
   
   definitions:
     group:
       name:
         $ref: "./primitive.yaml#/definitions/name"
       num:
         $ref: "#/definitions/num"


deref/group/numbers.yaml

.. code-block:: yaml

   definitions:
     num:
       type: number
       enum:
         - 1
         - 2
         - 3


deref/group/primitive.yaml

.. code-block:: yaml

   definitions:
     name:
       type: string
       enum:
         - A
         - B
         - C
   


deref/main.yaml

.. code-block:: yaml

   x-bundler-compose:
     - x.yaml as X
   
   definitions:
     color:
       $ref: "color/cmyk.yaml#/definitions/color"
     rgb:
       $ref: "color/rgb.yaml#/definitions/color"
     cmyk:
       $ref: "color/cmyk.yaml#/definitions/color"


deref/x.yaml

.. code-block:: yaml

   x-bundler-compose:
     - group/group.yaml as X
   
   definitions:
     color:
       $ref: "color/rgb.yaml#/definitions/color"


## generated.yaml

.. code-block:: yaml

   definitions:
     num:
       type: number
       enum:
       - 1
       - 2
       - 3
     XGroup:
       name:
         $ref: '#/definitions/XName'
       num:
         $ref: '#/definitions/num'
     XName:
       type: string
       enum:
       - A
       - B
       - C
     XColor:
       type: string
       enum:
       - r
       - g
       - b
     color:
       type: string
       enum:
       - C
       - M
       - Y
       - K
     rgb:
       x-conflicted: color/rgb.yaml#/definitions/color
       type: string
       enum:
       - r
       - g
       - b
     cmyk:
       $ref: '#/definitions/color'
