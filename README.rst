ui-classes
##########

`Data Classes <https://docs.python.org/3/library/dataclasses.html>`_ with superpowers:

- Objects are presentable in user interfaces.
- ModelList and ModelSet collections for robust manipulation of collections of models.



Installation
============


.. code:: bash

   pip install ui-classes


Basic Usage
===========



.. code:: bash

Notes:
======


- This is not designed to be fast, when adding data to models their
  types might cast and validated, which is costly.
  - filtering collections by string values cause glob match
