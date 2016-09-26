.. code-block:: bash

  $ tree
   .
   ├── generated.yaml
   ├── main.yaml
   ├── parts
   │   ├── common.yaml
   │   ├── x.yaml
   │   └── y.yaml
   └── swagger-bundler.ini

  $ swagger-bundler bundle main.yaml > generated.yaml

main.yaml

.. code-block:: yaml

   x-bundler-namespace: ZZZ
   x-bundler-compose:
     - ./parts/y.yaml
   x-bundler-concat:
     - ./parts/common.yaml

common.yaml

.. code-block:: yaml

   responses:
     UnexpectedError:
       description: Unexpected error
       schema:
         $ref: '#/definitions/Error'

   definitions:
     Error:
       type: object
       properties:
         code:
           type: integer
           format: int32

x.yaml

.. code-block:: yaml

   paths:
     /products:
       get:
         summary: Product Types
         description: <description>
         responses:
           200:
             description: An array of products
             schema:
               $ref: '#/definitions/ProductList'
           default:
             $ref: '#/responses/UnexpectedError'

   definitions:
     ProductList:
       type: array
       items:
         $ref: '#/definitions/Product'
     Product:
       type: object
       properties:
         product_id:
           type: string
           description: Unique ID.
         description:
           type: string
           description: Description of product.
         display_name:
           type: string
           description: Display name of product.


y.yaml

.. code-block:: yaml

   x-bundler-compose:
     - x.yaml

   paths:
     /seriess:
       get:
         summary: Series Types
         description: <description>
         responses:
           200:
             description: An array of seriess
             schema:
               $ref: '#/definitions/SeriesList'
           default:
             $ref: '#/responses/UnexpectedError'

   definitions:
     SeriesList:
       type: array
       items:
         $ref: '#/definitions/Series'
     Series:
       type: object
       properties:
         series_id:
           type: string
           description: Unique ID.
         display_name:
           type: string
           description: Display name of series.
         products:
           type: array
           items:
             $ref: "#/definitions/Product"
           description: Display name of series.

generated.yaml

.. code-block:: yaml

   definitions:
     ZZZProductList:
       type: array
       items:
         $ref: '#/definitions/ZZZProduct'
     ZZZProduct:
       type: object
       properties:
         product_id:
           type: string
           description: Unique ID.
         description:
           type: string
           description: Description of product.
         display_name:
           type: string
           description: Display name of product.
     ZZZSeriesList:
       type: array
       items:
         $ref: '#/definitions/ZZZSeries'
     ZZZSeries:
       type: object
       properties:
         series_id:
           type: string
           description: Unique ID.
         display_name:
           type: string
           description: Display name of series.
         products:
           type: array
           items:
             $ref: '#/definitions/ZZZProduct'
           description: Display name of series.
     Error:
       type: object
       properties:
         code:
           type: integer
           format: int32
   responses:
     UnexpectedError:
       description: Unexpected error
       schema:
         $ref: '#/definitions/Error'
   paths:
     /products:
       get:
         summary: Product Types
         description: <description>
         responses:
           200:
             description: An array of products
             schema:
               $ref: '#/definitions/ZZZProductList'
           default:
             $ref: '#/responses/UnexpectedError'
     /seriess:
       get:
         summary: Series Types
         description: <description>
         responses:
           200:
             description: An array of series
             schema:
               $ref: '#/definitions/ZZZSeriesList'
           default:
             $ref: '#/responses/UnexpectedError'
