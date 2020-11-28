.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/jwodder/linesep/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/linesep/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/linesep/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/linesep

.. image:: https://img.shields.io/pypi/pyversions/linesep.svg
    :target: https://pypi.org/project/linesep

.. image:: https://img.shields.io/github/license/jwodder/linesep.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/linesep>`_
| `PyPI <https://pypi.org/project/linesep>`_
| `Issues <https://github.com/jwodder/linesep/issues>`_

``linesep`` provides basic functions for reading, writing, splitting, & joining
text with custom separators that can occur either before, between, or after the
segments they separate.

Installation
============
``linesep`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install::

    python3 -m pip install linesep


Examples
========

Reading paragraphs separated by a blank line:

.. code:: python

    with open('text.txt') as fp:
        for entry in linesep.read_separated(fp, '\n\n'):
            ...

Parsing output from ``find -print0``:

.. code:: python

    find = subprocess.Popen(
        ['find', '/', '-some', '-complicated', '-condition', '-print0'],
        stdout=subprocess.PIPE,
    )
    for filepath in linesep.read_terminated(find.stdout, '\0'):
        ...

A poor man's JSON Sequence parser:

.. code:: python

    for entry in linesep.read_preceded(fp, '\x1E'):
        try:
            obj = json.loads(entry)
        except ValueError:
            pass
        else:
            yield obj


API
===

**Note**: Strings, filehandles, and regexes passed to this library's functions
may be either binary or text.  However, the arguments to a single invocation of
a function must be either all binary or all text, and the return type will
match.

**Note**: Using the ``read_*`` functions with a variable-length regular
expression is unreliable.  The only truly foolproof way to split on such
regexes is to first read the whole file into memory and then call one of the
``split_*`` functions.

.. code:: python

    linesep.read_preceded(
        fp: IO[AnyStr],
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
        chunk_size: int = 512,
    ) -> Iterator[AnyStr]

Read segments from a file-like object ``fp`` in which the beginning of each
segment is indicated by the string or compiled regex ``sep``.  A generator of
segments is returned; an empty file will always produce an empty generator.

If ``retain`` is true, the delimiters are included at the beginning of each
segment; otherwise, they are discarded.

Data is read from the filehandle ``chunk_size`` characters at a time.  If
``sep`` is a variable-length compiled regex and a delimiter in the file crosses
a chunk boundary, the results are undefined.

.. code:: python

    linesep.read_separated(
        fp: IO[AnyStr],
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
        chunk_size: int = 512,
    ) -> Iterator[AnyStr]

Read segments from a file-like object ``fp`` in which segments are separated by
the string or compiled regex ``sep``.  A generator of segments is returned; an
empty file will always produce a generator with one element, the empty string.

If ``retain`` is true, the delimiters are included in the output, with the
elements of the generator alternating between segments and separators, starting
with a (possible empty) segment.  If ``retain`` is false, the delimiters will
be discarded.

Data is read from the filehandle ``chunk_size`` characters at a time.  If
``sep`` is a variable-length compiled regex and a delimiter in the file crosses
a chunk boundary, the results are undefined.

.. code:: python

    linesep.read_terminated(
        fp: IO[AnyStr],
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
        chunk_size: int = 512,
    ) -> Iterator[AnyStr]

Read segments from a file-like object ``fp`` in which the end of each segment
is indicated by the string or compiled regex ``sep``.  A generator of segments
is returned; an empty file will always produce an empty generator.

If ``retain`` is true, the delimiters are included at the end of each segment;
otherwise, they are discarded.

Data is read from the filehandle ``chunk_size`` characters at a time.  If
``sep`` is a variable-length compiled regex and a delimiter in the file crosses
a chunk boundary, the results are undefined.

.. code:: python

    linesep.split_preceded(
        s: AnyStr,
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
    ) -> List[AnyStr]

Split a string ``s`` into zero or more segments starting with/preceded by the
string or compiled regex ``sep``.  A list of segments is returned; an empty
input string will always produce an empty list.

If ``retain`` is true, the delimiters are included at the beginning of each
segment; otherwise, they are discarded.

.. code:: python

    linesep.split_separated(
        s: AnyStr,
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
    ) -> List[AnyStr]

Split a string ``s`` into one or more segments separated by the string or
compiled regex ``sep``.  A list of segments is returned; an empty input string
will always produce a list with one element, the empty string.

If ``retain`` is true, the delimiters are included in the output, with the
elements of the list alternating between segments and separators, starting
with a (possible empty) segment.  If ``retain`` is false, the delimiters will
be discarded.

.. code:: python

    linesep.split_terminated(
        s: AnyStr,
        sep: Union[AnyStr, re.Pattern[AnyStr]],
        retain: bool = False,
    ) -> List[AnyStr]

Split a string ``s`` into zero or more segments terminated by the string or
compiled regex ``sep``.  A list of segments is returned; an empty input string
will always produce an empty list.

If ``retain`` is true, the delimiters are included at the end of each segment;
otherwise, they are discarded.

.. code:: python

    linesep.join_preceded(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr

Join the elements of ``iterable`` together, preceding each one with ``sep``.

.. code:: python

    linesep.join_separated(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr

Join the elements of ``iterable`` together, separating consecutive elements
with ``sep``.

.. code:: python

    linesep.join_terminated(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr

Join the elements of ``iterable`` together, appending ``sep`` to each one.

.. code:: python

    linesep.write_preceded(
        fp: IO[AnyStr],
        iterable: Iterable[AnyStr],
        sep: AnyStr,
    ) -> None

Write the elements of ``iterable`` to the filehandle ``fp``, preceding each one
with ``sep``.

.. code:: python

    linesep.write_separated(
        fp: IO[AnyStr],
        iterable: Iterable[AnyStr],
        sep: AnyStr,
    ) -> None

Write the elements of ``iterable`` to the filehandle ``fp``, separating
consecutive elements with ``sep``.

.. code:: python

    linesep.write_terminated(
        fp: IO[AnyStr],
        iterable: Iterable[AnyStr],
        sep: AnyStr,
    ) -> None

Write the elements of ``iterable`` to the filehandle ``fp``, appending ``sep``
to each one.
