uiclasses
##########

- Powered by `Python 3 Data Classes <https://docs.python.org/3/library/dataclasses.html>`_.
- Objects optimized for user interfaces.
- Methods to traverse nested dicts, convert to and from json
- ModelList and ModelSet collections for robust manipulation of collections of models.
- No I/O happens in models.
- Collections can be easily cached to leverage responsive user interfaces.



Installation
============


.. code:: bash

   pip install uiclasses


Basic Usage
===========



.. code:: bash

Notes:
======


- This is not designed to be fast, when adding data to models their
  types might cast and validated, which is costly.
  - filtering collections by string values cause glob match
