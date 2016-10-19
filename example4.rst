# structure

.. code-block:: bash

   tree
   examples/mixin
   ├── __pycache__
   │   └── transform.cpython-35.pyc
   ├── main.yaml
   ├── swagger-bundler.ini
   └── transform.py
   
   1 directory, 4 files
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
   bundle = ./transform.py:activate_mixin
   add_namespace =
   validate =


mixin/transform.py

.. code-block:: python

   from swagger_bundler import highlight
   from swagger_bundler.postscript import LooseDictWalker
   
   
   def activate_mixin(ctx, data, marker="x-bundler-mixin", pop_path_list=["x-bundler-types"], *args, **kwargs):
       if not kwargs.get("last"):
           return data
   
       def emit_mixin(subdata):
           path_list = subdata.pop(marker, None)
           if isinstance(path_list, (str, bytes)):
               path_list = [path_list]
           for path in path_list:
               if not path.startswith("#"):
                   highlight.show_on_warning("mixin: path={!r} is not found".format(path))
                   continue
               target = data
               for name in path.lstrip("#").split("/"):
                   if name:
                       target = target[name]
               subdata.update(target)
       w = LooseDictWalker(on_container=emit_mixin)
       w.walk([marker], data)
       for path in pop_path_list:
           data.pop(path, None)




mixin/main.yaml

.. code-block:: yaml

   x-bundler-types:
     id:
       pattern: '[0-9a-f]{24}'
     s:
       type: string
   
   
   definitions:
     pair:
       type: object
       properties:
         left:
           type: string
           x-bundler-mixin: '#/x-bundler-types/id'
         right:
           type: string
           x-bundler-mixin: '#/x-bundler-types/id'
     id:
       x-bundler-mixin: ['#/x-bundler-types/id', '#/x-bundler-types/s']
       description: object id
   
   parameters:
     siteId:
       x-bundler-mixin: ['#/x-bundler-types/id', '#/x-bundler-types/s']
   
   
   paths:
     /sites/{siteId}:
       PATCH:
         operationId: updateSite
         parameters:
         - name: siteId
           in: path
           required: true
           x-bundler-mixin: ['#/x-bundler-types/id', '#/x-bundler-types/s']
         - name: body
           in: body
           schema:
             type: object
             properties:
               url:
                 $ref: "#/definitions/id"
               userId:
                 $ref: "#/definitions/id"
         responses:
           200:
             description: OK


## generated.yaml

.. code-block:: yaml

   definitions:
     pair:
       type: object
       properties:
         left:
           type: string
           pattern: '[0-9a-f]{24}'
         right:
           type: string
           pattern: '[0-9a-f]{24}'
     id:
       description: object id
       pattern: '[0-9a-f]{24}'
       type: string
   paths:
     /sites/{siteId}:
       PATCH:
         operationId: updateSite
         parameters:
         - name: siteId
           in: path
           required: true
           pattern: '[0-9a-f]{24}'
           type: string
         - name: body
           in: body
           schema:
             type: object
             properties:
               url:
                 $ref: '#/definitions/id'
               userId:
                 $ref: '#/definitions/id'
         responses:
           200:
             description: OK
   parameters:
     siteId:
       pattern: '[0-9a-f]{24}'
       type: string
