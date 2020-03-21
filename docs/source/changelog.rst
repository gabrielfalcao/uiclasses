.. _changelog:

Release History
---------------

Changes in 2.0.3
~~~~~~~~~~~~~~~~

- perform ``super()__setattr__`` behavior even when an explicit setter
  is not defined and the attribute does not exist in the instance.

Changes in 2.0.2
~~~~~~~~~~~~~~~~

- fix python 3.6 support.

Changes in 2.0.1
~~~~~~~~~~~~~~~~

- don't try to cast annotations containing ``typing.Generic`` or
  ``typing.Any``.


Changes in 2.0.0
~~~~~~~~~~~~~~~~

- support explicit declaration of getters and setters that are not
  visible properties.

- implement type casting for all model attributes.

- automatic parsing of boolean-looking strings for fields of type
  bool.

Changes in 1.1.1
~~~~~~~~~~~~~~~~~

- Allow ``Model(x)`` where ``x`` is not a dict but can be cast into a dict.

Changes in 1.1.0
~~~~~~~~~~~~~~~~~

- Model.Set() and Model.List() not support generators.
