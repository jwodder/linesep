.. module:: linesep

==================================================
linesep — Handling lines with arbitrary separators
==================================================

`GitHub <https://github.com/jwodder/linesep>`_
| `PyPI <https://pypi.org/project/linesep/>`_
| `Documentation <https://linesep.readthedocs.io>`_
| `Issues <https://github.com/jwodder/linesep/issues>`_
| :doc:`Changelog <changelog>`

.. toctree::
    :hidden:

    core
    splitters
    misc
    changelog

``linesep`` provides basic functions & classes for reading, writing, splitting,
& joining text with custom separators that can occur either before, between, or
after the segments they separate.

Installation
============
``linesep`` requires Python 3.10 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install::

    python3 -m pip install linesep


Examples
========

Reading sections separated by a "``---``" line:

.. code:: python

    with open('text.txt') as fp:
        for entry in linesep.read_separated(fp, '\n---\n'):
            ...

Parsing output from ``find -print0``:

.. code:: python

    find = subprocess.Popen(
        ['find', '/', '-some', '-complicated', '-condition', '-print0'],
        stdout=subprocess.PIPE,
    )
    for filepath in linesep.read_terminated(find.stdout, '\0'):
        ...

A poor man's `JSON Text Sequence <https://tools.ietf.org/html/rfc7464>`_ parser:

.. code:: python

    for entry in linesep.read_preceded(fp, '\x1E'):
        try:
            obj = json.loads(entry)
        except ValueError:
            pass
        else:
            yield obj

Read from a text file one paragraph at a time:

.. code:: python

    with open("my-novel.txt") as fp:
        for paragraph in linesep.read_paragraphs(fp):
            ...

Split input from an ``anyio.TextReceiveStream`` on newlines:

.. code:: python

    async with anyio.TextReceiveStream( ... ) as stream:
        splitter = linesep.UnicodeNewlineSplitter()
        async for line in splitter.aitersplit(stream):
            print(line)


Indices and tables
==================
* :ref:`genindex`
* :ref:`search`
