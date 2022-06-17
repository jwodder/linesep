.. currentmodule:: linesep

Splitter Classes
================

``linesep`` provides a set of classes (called :dfn:`splitters`) for splitting
strings in chunks, inspired by the `~codecs.IncrementalEncoder` and
`~codecs.IncrementalDecoder` classes of the `codecs` module.  Input is fed to a
splitter instance one piece at a time, and the segments split from the input so
far are (depending on the methods used) either returned immediately or else
retrieveable from the splitter afterwards.  This is useful when you have a data
source that is neither a string nor a filehandle.

If the input is in the form of an iterable, a splitter can be used to iterate
over it and yield each segment:

>>> import linesep
>>> splitter = linesep.SeparatedSplitter("|", retain=True)
>>> input_data = ["one|two|thr", "ee|four|", "five||six"]
>>> for item in splitter.itersplit(input_data):
...     print(repr(item))
...
'one'
'|'
'two'
'|'
'three'
'|'
'four'
'|'
'five'
'|'
''
'|'
'six'

Alternatively, input can be provided to the splitter one piece at a time by
passing it to the `~Splitter.split()` method, which returns all newly-split off
items:

>>> splitter = linesep.TerminatedSplitter("\0", retain=False)
>>> splitter.split("foo\0bar\0baz")
['foo', 'bar']
>>> splitter.split("\0quux\0gnusto\0", final=True)
['baz', 'quux', 'gnusto']

At a lower level, input can be provided to the `~Splitter.feed()` method, and
the output can be retrieved with `~Splitter.get()` or `~Splitter.getall()`:

>>> splitter = linesep.UniversalNewlineSplitter(retain=True, translate=True)
>>> splitter.feed("foo\nbar\r\nbaz")
>>> splitter.nonempty
True
>>> splitter.get()
'foo\n'
>>> splitter.nonempty
True
>>> splitter.get()
'bar\n'
>>> splitter.nonempty
False
>>> splitter.get()
Traceback (most recent call last):
    ...
SplitterEmptyError: No items available in splitter
>>> splitter.close()
>>> splitter.nonempty
True
>>> splitter.get()
'baz'
>>> splitter.nonempty
False

Like the ``*_preceded``, ``*_separated``, and ``*_terminated`` functions,
strings passed to splitters may be either binary or text.  However, the input
to a single instance of a splitter must be either all binary or all text, and
the output type will match.


Splitters
---------

.. autoclass:: Splitter
    :member-order: bysource

.. autoclass:: PrecededSplitter
    :no-members:

.. autoclass:: SeparatedSplitter
    :no-members:

.. autoclass:: TerminatedSplitter
    :no-members:

.. autoclass:: UniversalNewlineSplitter
    :no-members:

Utilities
---------

.. autofunction:: get_newline_splitter

.. autoclass:: SplitterState()
    :no-members:

.. autoexception:: SplitterClosedError
    :show-inheritance:

.. autoexception:: SplitterEmptyError
    :show-inheritance:
