.. _Tutorial:


Tutorial
========

This is a basic guide to the most basic usage of the module.


In this guide we will define data models for data returned by the
Github API to retrieve users https://developer.github.com/v3/users/
and present this data to the UI layer in a concise way.

At the end we will also build a very simple client to the Github API.


Declaring a Model for user interfaces
-------------------------------------


The model below is defined according to the `Single User Response
<https://developer.github.com/v3/users/#get-a-single-user>`_ from the Github V3
API.


Take a look here to see what a full json response `looks like
<https://developer.github.com/v3/users/#response>`_ before continuing
so the model definition below will make more sense.

Okay, so you see there are several fields, but only a few of the User
properties are relevant for user-interface purposes.


.. testcode::

   from uiclasses import Model

   class GithubUser(Model):
       login: str
       email: str
       hireable: bool
       public_repos: int
       public_gists: int
       followers: int
       following: int

Every field declared with `type annotations
<https://docs.python.org/3/library/typing.html>`_ is considered to be
visible in the user interface.

This is this is powered by :py:func:`dataclasses.fields`.


Two ways of instantiating models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


1. Passing a :py:class:`dict`
+++++++++++++++++++++++++++++

.. testcode::

   octocat = GithubUser({
       "login": "octocat",
   })

   print(octocat.to_dict())

.. testoutput::

   {
       "login": "octocat",
   }


1. Passing a keyword-arguments
++++++++++++++++++++++++++++++

.. testcode::

   octocat = GithubUser(
       login="octocat",
   )
   print(octocat.to_dict())

.. testoutput::

   {
       "login": "octocat",
   }

Automatic getters and setters
-----------------------------

Every visible field becomes a property that can be accessed directly
via instance as if it were a regular ``@property``


.. testcode::

   user1 = GithubUser()
   user1.login = "octocat"

   print(user1.to_dict())


.. testoutput::

   {
       "login": "octocat",
   }


Invisible Getters/Setters
~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it can be useful to define properties that act on the
internal data of a model without making them visible to the user
interface.

UIClasses provides special annotations to achieve this with 3 variations:

- Read-only Getters
- Write-only Setters
- Read-Write Properties


Read-only Getters
+++++++++++++++++

.. testcode::

   from uiclasses import Model


   class User(Model):
       id: int
       username: str
       token: Getter[str]


   foobar = User(id=1, username="foobar", token="some-data")
   print(foobar.to_dict())
   print(foobar.token)
   print(foobar.get_table_columns())

   try:
       foobar.token = 'another-value'
   except Exception as e:
       print(e)


.. testoutput::

   {
       "id": 1,
       "username": "foobar",
       "token": "some-data",
   }
   "some-data"
   ["id", "username"]
   "'User' object has no attribute 'token'"


Write-only Getters
++++++++++++++++++

.. testcode::

   from uiclasses import Model


   class User(Model):
       id: int
       username: str
       token: Setter[str]


   foobar = User(id=1, username="foobar", token="some-data")
   print(foobar.to_dict())
   foobar.token = 'another-value'
   print(foobar.to_dict())
   print(foobar.get_table_columns())

   try:
       print(foobar.token)
   except Exception as e:
       print(e)

.. testoutput::

   {
       "id": 1,
       "username": "foobar",
       "token": "some-data",
   }
   {
       "id": 1,
       "username": "foobar",
       "token": "another-value",
   }
   ["id", "username"]
   "'User' object has no attribute 'token'"



Read-write Properties
+++++++++++++++++++++


.. testcode::

   from uiclasses import Model


   class User(Model):
       id: int
       username: str
       token: Property[str]


   foobar = User(id=1, username="foobar", token="some-data")
   print(foobar.token)
   print(foobar.to_dict())
   foobar.token = 'another-value'
   print(foobar.token)
   print(foobar.to_dict())
   print(foobar.get_table_columns())


.. testoutput::

   "some-data"
   {
       "id": 1,
       "username": "foobar",
       "token": "some-data",
   }
   "another-value"
   {
       "id": 1,
       "username": "foobar",
       "token": "another-value",
   }
   ["id", "username"]
