.. code-block:: bash

  $ tree
  .
  ├── generated.yaml
  ├── main.yaml
  └── parts
      ├── human-state.yaml
      ├── type.yaml
      └── verify-state.yaml

  $ swagger-bundler bundle main.yaml > generated.yaml


main.yaml

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

parts/human-state.yaml

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

parts/verify-state.yaml

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


.. code-block:: yaml

  definitions:
    type:
      type: string
      enum:
        - active
        - inactive
