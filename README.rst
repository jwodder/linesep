This module provides functions for reading a file or file-like object as a
series of entries delimited by a given string or regex.  The three functions
differ in how a delimiter immediately at the beginning or end of the file is
treated, as well as in how retained delimiters are returned.

::

    read_preceded(fp, sep, retain=False, size=512)

``read_preceded`` is for delimiters that mark the beginning of an entry; when
retained, the delimiters are prepended to the beginning of each entry (except
possibly the first).  A delimiter at the beginning of a file does not produce
an entry for the empty string before it, and a delimiter at the end of a file
indicates an empty entry.

::

    read_separated(fp, sep, retain=False, size=512)

``read_separated`` is for delimiters that separate one entry from another; when
retained, the delimiters are included in the returned generator as separate
elements.  A delimiter at the start or end of a file produces an entry for the
empty string before or after it.

::

    read_terminated(fp, sep, retain=False, size=512)

``read_terminated`` is for delimiters that mark the end of an entry; when
retained, the delimiters are appended to the end of each entry (except possibly
the last).  A delimiter at the start of a file indicates an empty entry, and a
delimiter at the end of a file does not produce an entry for the empty string
after it.


Each function takes the following arguments:

``fp``
    A file or file-like object (specifically, one that supports the ``read``
    method).  ``fp`` may produce either bytes or characters; the type of
    ``sep`` should match, and the same type will be returned.

``sep``
    A string (bytes or unicode) or compiled ``re.RegexObject`` for delimiting
    entries

``retain``
    Whether to include the delimiters in the output; default value: ``False``

``size``
    How many bytes or characters to read from ``fp`` at a time; default value:
    512

Each function returns a generator of the entries, optionally including
delimiters.

Examples
--------

Reading paragraphs separated by a blank line::

    with open('text.txt') as fp:
        for entry in linesep.read_separated(fp, '\n\n'):
            ...

Parsing output from ``find -print0``::

    find = subprocess.Popen(['find', '/', '-some', '-complicated', '-condition',
                                     '-print0'], stdout=subprocess.PIPE)
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

..
    TODO: example with regexes

See Also
--------

Prior art: <http://bugs.python.org/issue1152248#msg109117>
