.. currentmodule:: linesep

Core Functions
==============

Notes
-----

- Strings, filehandles, and regexes passed to the ``*_preceded``,
  ``*_separated``, and ``*_terminated`` functions may be either binary or text.
  However, the arguments to a single invocation of a function must be either
  all binary or all text, and the return type will match.


- Using the ``read_*`` functions with a variable-length regular expression is
  unreliable.  The only truly foolproof way to split on such regexes is to
  first read the whole file into memory and then call one of the ``split_*``
  functions.  As a result, passing a regular expression separator to a
  ``read_*`` function is deprecated starting in version 0.4.0, and support for
  this will be removed in version 1.0.

- Note the following about how the different types of separators are handled at
  the beginning & end of input:

  - When segments are terminated by a given separator, a separator at the
    beginning of the input creates an empty leading segment, and a separator at
    the end of the input simply terminates the last segment.

  - When segments are separated by a given separator, a separator at the
    beginning of the input creates an empty leading segment, and a separator at
    the end of the input creates an empty trailing segment.

  - When segments are preceded by a given separator, a separator at the
    beginning of the input simple starts the first segment, and a separator at
    the end of the input creates an empty trailing segment.

- Two adjacent separators always create an empty segment between them, unless
  the separator is a regex that spans both separators at once.

Splitting Strings
-----------------

.. autofunction:: split_preceded
.. autofunction:: split_separated
.. autofunction:: split_terminated

Joining Strings
---------------

.. autofunction:: join_preceded
.. autofunction:: join_separated
.. autofunction:: join_terminated

Reading from Filehandles
------------------------

.. autofunction:: read_preceded
.. autofunction:: read_separated
.. autofunction:: read_terminated

Writing to Filehandles
----------------------

.. autofunction:: write_preceded
.. autofunction:: write_separated
.. autofunction:: write_terminated
