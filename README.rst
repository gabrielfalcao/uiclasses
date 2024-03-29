UIClasses - Data-Modeling for User Interfaces
##############################################


.. image:: https://img.shields.io/pypi/dm/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/codecov/c/github/gabrielfalcao/uiclasses
   :target: https://codecov.io/gh/gabrielfalcao/uiclasses

.. image:: https://github.com/gabrielfalcao/uiclasses/actions/workflows/main.yml/badge.svg
   :target: https://github.com/gabrielfalcao/uiclasses/actions/workflows/main.yml

.. image:: https://img.shields.io/readthedocs/uiclasses
   :target: https://uiclasses.readthedocs.io/

.. image:: https://img.shields.io/github/license/gabrielfalcao/uiclasses?label=Github%20License
   :target: https://github.com/gabrielfalcao/uiclasses/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/pypi/l/uiclasses?label=PyPi%20License
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/pypi/format/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/pypi/status/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/pypi/pyversions/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/pypi/implementation/uiclasses
   :target: https://pypi.org/project/uiclasses

.. image:: https://img.shields.io/snyk/vulnerabilities/github/gabrielfalcao/uiclasses
   :target: https://github.com/gabrielfalcao/uiclasses/network/alerts

.. image:: https://img.shields.io/github/v/tag/gabrielfalcao/uiclasses
   :target: https://github.com/gabrielfalcao/uiclasses/releases

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

.. code:: python

   from uiclasses import Model


   class BlogPost(Model):
       id: int
       title: str
       body: str


   post1 = BlogPost({"id": 1, "title": "title 1", "body": "body 1", "wimsical_extra_field": "lala land"})
   post2 = BlogPost(id=2, title="title 2", body="body 2", extradata='stored but invisible')

   published = BlogPost.List([post1, post2])

   print(published.format_pretty_table())


.. image:: https://github.com/gabrielfalcao/uiclasses/raw/master/docs/source/_static/screenshot-blog-list-pretty-table.png


.. code:: python

   print(published.format_robust_table())

.. image:: https://github.com/gabrielfalcao/uiclasses/raw/master/docs/source/_static/screenshot-blog-list-robust-table.png



Notes:
======


- This is not designed to be fast, when adding data to models their
  types might cast and validated, which is costly.
  - filtering collections by string values cause glob match
