# structure

.. code-block:: bash

   tree
   examples/qualified-import
   ├── generated.yaml
   ├── main.yaml
   └── parts
       ├── human-state.yaml
       ├── type.yaml
       └── verify-state.yaml
   
   1 directory, 5 files
   swagger-bundler bundle main.yaml > generated.yaml


qualified-import/main.yaml

.. code-block:: yaml

   x-bundler-namespace: My
   x-bundler-compose:
     - parts/human-state.yaml as H
     - parts/verify-state.yaml as V
   
   definitions:
     manager:
       type: object
       properties:
         name:
           type: string
         humanState:
           $ref: '#/definitions/HState'
         state:
           $ref: '#/definitions/VState'


qualified-import/parts/human-state.yaml

.. code-block:: yaml

   x-bundler-concat:
     - type.yaml
   
   definitions:
     state:
       properties:
         type:
           $ref: "#/definitions/type"
         status:
           type: string
           enum:
             - hungry
             - angry
             - sad
             - happy
             - dead


qualified-import/parts/type.yaml

.. code-block:: yaml

   definitions:
     type:
       type: string
       enum:
         - active
         - inactive


qualified-import/parts/verify-state.yaml

.. code-block:: yaml

   x-bundler-compose:
     - type.yaml
   
   definitions:
     state:
       properties:
         type:
           $ref: "#/definitions/type"
         status:
           type: string
           enum:
             - ok
             - ng
   


## generated.yaml

.. code-block:: yaml

   definitions:
     type:
       type: string
       enum:
       - active
       - inactive
     MyHState:
       properties:
         type:
           $ref: '#/definitions/type'
         status:
           type: string
           enum:
           - hungry
           - angry
           - sad
           - happy
           - dead
     MyVType:
       type: string
       enum:
       - active
       - inactive
     MyVState:
       properties:
         type:
           $ref: '#/definitions/MyVType'
         status:
           type: string
           enum:
           - ok
           - ng
     MyManager:
       type: object
       properties:
         name:
           type: string
         humanState:
           $ref: '#/definitions/MyHState'
         state:
           $ref: '#/definitions/MyVState'
