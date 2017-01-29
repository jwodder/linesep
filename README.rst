.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://travis-ci.org/jwodder/linesep.svg?branch=master
    :target: https://travis-ci.org/jwodder/linesep

.. image:: https://coveralls.io/repos/github/jwodder/linesep/badge.svg?branch=master
    :target: https://coveralls.io/github/jwodder/linesep?branch=master

.. image:: https://img.shields.io/pypi/pyversions/linesep.svg
    :target: https://pypi.python.org/pypi/linesep

.. image:: https://img.shields.io/github/license/jwodder/linesep.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/linesep>`_
| `PyPI <https://pypi.python.org/pypi/linesep>`_
| `Issues <https://github.com/jwodder/linesep/issues>`_

This module provides basic functions for reading & writing text with custom
line separators that can occur either before, between, or after lines — though
its primary purpose is actually to allow me to experiment with proper Python
packaging & testing procedures.  Being actually useful is not its #1 goal.


Installation
============

Just use `pip <https://pip.pypa.io>`_ (You have pip, right?) to install
``linesep``::

    pip install linesep


Examples
========

Reading paragraphs separated by a blank line::

    with open('text.txt') as fp:
        for entry in linesep.read_separated(fp, '\n\n'):
            ...

Parsing output from ``find -print0``::

    find = subprocess.Popen(
        ['find', '/', '-some', '-complicated', '-condition', '-print0'],
        stdout=subprocess.PIPE,
    )
    for filepath in linesep.read_terminated(find.stdout, '\0'):
        ...

A poor man's JSON Sequence parser::

    for entry in linesep.read_preceded(fp, '\x1E'):
        try:
            obj = json.loads(entry)
        except ValueError:
            pass
        else:
            yield obj


See Also
========

Prior art: <http://bugs.python.org/issue1152248#msg109117>
