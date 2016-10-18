# structure

.. code-block:: bash

   tree
   examples/basic
   ├── generated.yaml
   ├── main.yaml
   ├── parts
   │   ├── error.yaml
   │   ├── product.yaml
   │   └── series.yaml
   ├── product.yaml
   └── series.yaml
   
   1 directory, 7 files
   swagger-bundler bundle main.yaml > generated.yaml


basic/main.yaml

.. code-block:: yaml

   x-bundler-namespace: ZZZ
   x-bundler-compose:
     - ./product.yaml
     - ./series.yaml
   
   swagger: '2.0'
   info:
     title: example
     description: swagger-bundler examples
     version: "1.0.0"
   
   host: localhost
   
   schemes:
     - http
   
   basePath: /api/v1
   produces:
     - application/json
   consumes:
     - application/json


basic/parts/error.yaml

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


basic/parts/product.yaml

.. code-block:: yaml

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


basic/parts/series.yaml

.. code-block:: yaml

   x-bundler-compose:
     - product.yaml
   
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


basic/product.yaml

.. code-block:: yaml

   x-bundler-concat:
     - ./parts/error.yaml
   x-bundler-compose:
     - ./parts/product.yaml
   
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
   


basic/series.yaml

.. code-block:: yaml

   x-bundler-concat:
     - ./parts/error.yaml
   x-bundler-compose:
     - ./parts/series.yaml
   
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


## generated.yaml

.. code-block:: yaml

   swagger: '2.0'
   info:
     title: example
     description: swagger-bundler examples
     version: 1.0.0
   host: localhost
   schemes:
   - http
   basePath: /api/v1
   consumes:
   - application/json
   produces:
   - application/json
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
             description: An array of seriess
             schema:
               $ref: '#/definitions/ZZZSeriesList'
           default:
             $ref: '#/responses/UnexpectedError'
