.. _changelog:

Release History
---------------

Changes in 3.0.0
~~~~~~~~~~~~~~~~

- Replace ``uiclasses.collections.List.children`` with ``uiclasses.collections.List.descendants``.
- Replace ``uiclasses.collections.Set.children`` with ``uiclasses.collections.Set.descendants``.
- Replace ``uiclasses.utils.traverse_dict_descendants`` with ``uiclasses.utils.traverse_dict_descendants``.

Changes in 2.3.2
~~~~~~~~~~~~~~~~

- Add same ``only_visible`` of ``serialize()`` to ``to_dict()`` and
  ``serialize_field()``.

- Pass correct ``only_visible`` within ``serialize_all()`` and
  ``serialize_visible()``.

Changes in 2.3.1
~~~~~~~~~~~~~~~~

- Change behavior of ``serialize_visible()`` to omit ``None`` values.

Changes in 2.3.0
~~~~~~~~~~~~~~~~

- Add method ``serialize_visible()`` and ``serialize_all()`` to
  ``Model`` and ``IterableCollection``.

- Add boolean parameter ``only_visible`` in
  ``uiclasses.base.Model.serialize()`` - to decide whether to call
  ``serialize_visible()`` or ``serialize_all()``.


Changes in 2.2.1
~~~~~~~~~~~~~~~~

- Add behavior to ``uiclasses.collections.is_iterable()`` consider
  anything with a callable ``__iter__`` attribute a callable.


Changes in 2.2.0
~~~~~~~~~~~~~~~~

- Change behavior of explicit ``__visible_attributes__`` declaration:
  when declared, the visible fields will be exactly those. If not
  declared, visible fields will be extracted from type annotations.

- The old behavior of ``__visible_attributes__`` is now available
  through ``Model.__declared_attributes__`` which
  ``__visible_attributes__`` (if any) with types from annotations.

- Support casting IterableCollection with itself and
  introduce ``uiclasses.collections.is_iterable()`` helper function.

- Show RuntimeWarning if typing module is installed as distribution
  package in python > 3.6.1.

Changes in 2.1.0
~~~~~~~~~~~~~~~~

- Support nested model types.
- Cast values to their known type when instantiating a new Model.

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
