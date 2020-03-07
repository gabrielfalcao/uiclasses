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



.. note:: Every :py:class:`~uiclasses.base.Model` is a
             :py:func:`~uiclasses.base.basic_dataclass` and assumes
             that all fields with `type annotations
             <https://docs.python.org/3/library/typing.html>`_ are
             visible, this is powered by
             :py:func:`dataclasses.fields`.
