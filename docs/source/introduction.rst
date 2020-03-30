.. _Introduction:


Introduction
============


UIClasses is a library that leverages data-modeling for the
user-interface layer of your python project.

It provides the :py:class:`~uiclasses.Model` class that adds `Data
Classe <https://docs.python.org/3/library/dataclasses.html>`_ features
to its subclasses.

With UIClasses you can separate backend from frontend data modeling,
preventing coupling in your python project.

This is not an ORM
------------------

UIClasses is designed to work in tandem with your favorite ORM, not a replacement for it.

Java has DAO (Data-access objects) and POJO (Plain Old Java Objects),
usually POJOs are used at the UI-layer of an application with data
mapped from a DAO whose data came from the storage layer of an
application.

In this context, UIClasses are POJOs, and ORM Models, for example
SQLAlchemy, are DAOs.


Bags of Variables
------------------

- Objects optimized for user interfaces.
- Methods to traverse nested dicts, convert to and from json
- ModelList and ModelSet collections for robust manipulation of collections of models.
- No I/O happens in models.
- Collections can be easily cached to leverage responsive user interfaces.


How to install
--------------


.. code:: bash

   pip3 install uiclasses
