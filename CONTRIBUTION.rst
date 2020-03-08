Contributing
============

Code of conduct
---------------

Everyone who is participating to this project is expected to uphold the
`code of
conduct <https://github.com/NewStore-oss/uiclasses/blob/master/CODE_OF_CONDUCT.md>`__.

How can I contribute?
---------------------


Writing a new PR
~~~~~~~~~~~~~~~~

- Fork and clone the git repository
- Create a branch
- Run ``make tdd`` and leave the terminal window open, this will
  automatically run all the tests every time you modify a python file.
- Make your modifications.
- Add unit tests for all your changes and additions
  - Make sure that tests are readable.
  - Don't fall into the temptation of creating global variables for
    your tests, make all the preparation for your tests within each
    test case.

- Don't let the coverage drop from 100%.


Reporting a bug
~~~~~~~~~~~~~~~

In case you find a bug please check the next points before you submit a
bug.

- Search for a similar issue in `issues
  <https://github.com/NewStore-OSS/uiclasses/issues>`__ to prevent
  duplicated tickets, this will save us time triaging bugs.
- When creating a new issue, tag it with the label "bug"
-  Choose a clear and descriptive title to identify the problem.
- Share a code snippet of how to reproduce the problem, if that's a
  problem then try to share as much detail as possible.
- Provide details about your runtime: Python Version, Operating system, etc.

Suggestion a new feature or improvement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Search for a similar issue in `issues
  <https://github.com/NewStore-OSS/uiclasses/issues>`__ to prevent
  duplicated tickets, this will save us time triaging bugs.
- When creating a new issue, tag it with the label "enhancement"


Code style
^^^^^^^^^^

- Run `black <https://black.readthedocs.io/en/stable/>`_ before commiting.
- Make sure that all checks for your PR pass.
