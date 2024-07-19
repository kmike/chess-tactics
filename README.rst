=============
chess-tactics
=============

.. image:: https://img.shields.io/pypi/v/chess-tactics.svg
   :target: https://pypi.python.org/pypi/chess-tactics
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/chess-tactics.svg
   :target: https://pypi.python.org/pypi/chess-tactics
   :alt: Supported Python Versions

.. image:: https://github.com/kmike/chess-tactics/workflows/tox/badge.svg
   :target: https://github.com/kmike/chess-tactics/actions
   :alt: Build Status

``chess-tactics`` is a Python library (based on python-chess)
to work with common chess tactics.

Included:

* static exchange evaluation functions,
* detection of tactical patterns on the board,
* classification of common tactical mistakes, such as hanging a piece
  or missing a fork.


* License: MIT

Development
===========

To work on the repository, install pre-commit and run ``pre-commit install``
to install the hooks.
