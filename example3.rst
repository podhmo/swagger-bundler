# structure

.. code-block:: bash

   tree
   examples/nested
   ├── main.yaml
   └── swagger-bundler.ini
   
   0 directories, 2 files
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
   bundle = swagger_bundler.postscript:lifting_definition
   add_namespace =
   validate =


nested/main.yaml

.. code-block:: yaml

   definitions:
     X:
       type: string
     Foo:
       type: object
       properties:
         bar:
           type: object
           properties:
             boo:
               type: object
               properties:
                 yoo:
                   type: object
                   properties:
                     yah:
                       type: object
                       properties:
                         yay:
                           type: string
                 x:
                   $ref: '#/definitions/X'
     Boo:
       type: array
       items:
         type: object
         properties:
           foo:
             $ref: "#/definitions/Foo"
           user:
             properties:
               name:
                 type: string
               age:
                 type: number
           grouplist:
             type: array
             items:
               properties:
                 name:
                   type: string


## generated.yaml

.. code-block:: yaml

   definitions:
     X:
       type: string
     Foo:
       type: object
       properties:
         bar:
           $ref: '#/definitions/FooBar'
     FooBar:
       type: object
       properties:
         boo:
           $ref: '#/definitions/FooBarBoo'
       x-auto-generated: true
     FooBarBoo:
       type: object
       properties:
         yoo:
           $ref: '#/definitions/FooBarBooYoo'
         x:
           $ref: '#/definitions/X'
       x-auto-generated: true
     FooBarBooYoo:
       type: object
       properties:
         yah:
           $ref: '#/definitions/FooBarBooYooYah'
       x-auto-generated: true
     FooBarBooYooYah:
       type: object
       properties:
         yay:
           type: string
       x-auto-generated: true
     Boo:
       type: array
       items:
         $ref: '#/definitions/BooItems'
     BooItems:
       type: object
       properties:
         foo:
           $ref: '#/definitions/Foo'
         user:
           $ref: '#/definitions/BooItemsUser'
         grouplist:
           $ref: '#/definitions/BooItemsGrouplist'
       x-auto-generated: true
     BooItemsGrouplist:
       type: array
       items:
         $ref: '#/definitions/BooItemsGrouplistItems'
       x-auto-generated: true
     BooItemsGrouplistItems:
       type: object
       properties:
         name:
           type: string
       x-auto-generated: true
     BooItemsUser:
       type: object
       properties:
         name:
           type: string
         age:
           type: number
       x-auto-generated: true
