.. _API Reference:


API Reference
=============


Model
-----

.. doctest::

   >>> from uiclasses import Model
   >>>
   >>> class User(Model):
   ...     email: str
   ...

.. autoclass:: uiclasses.Model


Model.List
----------

.. doctest::

   >>> user1 = User(email="aaaa@test.com")
   >>> user2 = User(email="bbbb@test.com")
   >>>
   >>> users = User.List([user1, user2, user1])
   >>> users
   User.List[user1, user2, user3]


.. autoclass:: uiclasses.collections.ModelList

Model.Set
---------

An ordered set for managing unique items.

.. doctest::

   >>> user1 = User(email="aaaa@test.com")
   >>> user2 = User(email="bbbb@test.com")
   >>>
   >>> users = User.Set([user1, user2, user1])
   >>> users
   User.Set[user1, user2]


.. autoclass:: uiclasses.collections.ModelSet


DataBag
-------

.. autoclass:: uiclasses.DataBag


UserFriendlyObject
------------------

.. autoclass:: uiclasses.UserFriendlyObject


DataBagChild
------------

.. autoclass:: uiclasses.DataBag


IterableColletion
-----------------

.. autoclass:: uiclasses.collections.IterableCollection


Utils
-----

.. automodule:: uiclasses.utils


File-System Helpers
-------------------

.. automodule:: uiclasses.fs


Meta
----

.. automodule:: uiclasses.meta
