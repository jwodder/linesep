"""
Functions for reading a file or file-like object as a series of entries
delimited by a given string or regex.  Each function returns a generator of the
entries, optionally with the delimiters included.  The file-like object may
produce either bytes or characters; the type of the separator should match, and
the same type will be returned.

The three functions differ in how a delimiter immediately at the beginning or
end of the file is treated, as well as in how retained delimiters are returned:

``read_preceded`` is for delimiters that mark the beginning of an entry; when
retained, the delimiters are placed at the beginning of each entry (except
possibly the first).  A delimiter at the beginning of a file does not produce
an entry for the empty string before it, and a delimiter at the end of a file
indicates an empty entry.

``read_separated`` is for delimiters that separate one entry from another; when
retained, the delimiters are included in the returned generator as separate
elements.  A delimiter at the start or end of a file produces an entry for the
empty string before or after it.

``read_terminated`` is for delimiters that mark the end of an entry; when
retained, the delimiters are placed at the end of each entry (except possibly
the last).  A delimiter at the start of a file indicates an empty entry, and a
delimiter at the end of a file does not produce an entry for the empty string
after it.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'linesep@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/linesep'

import re

def read_preceded(fp, sep, retain=False, size=512):
    """
    Read from a file-like object ``fp`` containing entries starting
    with/preceded by the string or compiled regex ``sep`` and return a
    generator of the entries.  An empty file will always produce an empty
    generator.

    If ``retain`` is `True`, each entry (except possibly the first) will have
    its leading delimiter prepended to it.  If ``sep`` is a compiled regex, the
    delimiter will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, leading delimiters will not be present in the
    output entries.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    # Omits empty leading entry
    entries = read_separated(fp, sep, retain=retain, size=size)
    e = next(entries)
    if e:
        yield e
    if retain:
        entries = _join_pairs(entries)
    for e in entries:
        yield e

def read_separated(fp, sep, retain=False, size=512):
    """
    Read from a file-like object ``fp`` containing entries separated by the
    string or compiled regex ``sep`` and return a generator of the entries.  An
    empty file will always produce a generator with one element, the empty
    string.

    If ``retain`` is `True`, the separators will be included in the output: the
    generator will contain an odd number of elements, alternating between
    entries and separators, starting with a (possibly empty) entry.  If ``sep``
    is a compiled regex, the separator elements will be the strings matched by
    the regex; any capturing subgroups will be ignored.

    If ``retain`` is `False`, separators will not be present in the output.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    # http://stackoverflow.com/a/7054512/744178
    if not hasattr(sep, 'match'):
        sep = re.compile(re.escape(sep))
    buff = ''
    for chunk in iter(lambda: fp.read(size), ''):
        buff += chunk
        lastend = 0
        for m in sep.finditer(buff):
            yield buff[lastend:m.start()]
            if retain:
                yield m.group()
            lastend = m.end()
        buff = buff[lastend:]
    yield buff

def read_terminated(fp, sep, retain=False, size=512):
    """
    Read from a file-like object ``fp`` containing entries terminated by the
    string or compiled regex ``sep`` and return a generator of the entries.  An
    empty file will always produce an empty generator.

    If ``retain`` is `True`, each entry (except possibly the last) will have
    its terminator appended to it.  If ``sep`` is a compiled regex, the
    terminator will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, terminators will not be present in the output
    entries.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    # Omits empty trailing entry
    prev = None
    entries = read_separated(fp, sep, retain=retain, size=size)
    if retain:
        entries = _join_pairs(entries)
    for e in entries:
        if prev is not None:
            yield prev
        prev = e
    if prev:
        yield prev

def split_preceded(s, sep, retain=False):
    """
    Split a string ``s`` into zero or more entries starting with/preceded by
    the string or compiled regex ``sep`` and return a list of the entries.  An
    empty string will always produce an empty list.

    If ``retain`` is `True`, each entry (except possibly the first) will have
    its leading delimiter prepended to it.  If ``sep`` is a compiled regex, the
    delimiter will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, leading delimiters will not be present in the
    output entries.
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries[1:] = list(_join_pairs(entries[1:]))
    if entries[0] == '':
        entries.pop(0)
    return entries

def split_separated(s, sep, retain=False):
    """
    Split a string ``s`` into one or more entries separated by the string or
    compiled regex ``sep`` and return a list of the entries.  An empty string
    will always produce a list with one element, the empty string.

    If ``retain`` is `True`, the separators will be included in the output: the
    list will contain an odd number of elements, alternating between entries
    and separators, starting with a (possibly empty) entry.  If ``sep`` is a
    compiled regex, the separator elements will be the strings matched by the
    regex; any capturing subgroups will be ignored.

    If ``retain`` is `False`, separators will not be present in the output.
    """
    # http://stackoverflow.com/a/7054512/744178
    if not hasattr(sep, 'match'):
        sep = re.compile(re.escape(sep))
    entries = []
    lastend = 0
    for m in sep.finditer(s):
        entries.append(s[lastend:m.start()])
        if retain:
            entries.append(m.group())
        lastend = m.end()
    entries.append(s[lastend:])
    return entries

def split_terminated(s, sep, retain=False):
    """
    Split a string ``s`` into zero or more entries terminated by the string or
    compiled regex ``sep`` and return a list of the entries.  An empty string
    will always produce an empty list.

    If ``retain`` is `True`, each entry (except possibly the last) will have
    its terminator appended to it.  If ``sep`` is a compiled regex, the
    terminator will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, terminators will not be present in the output
    entries.
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries = list(_join_pairs(entries))
    if entries[-1] == '':
        entries.pop()
    return entries

def join_preceded(iterable, sep):
    """
    Join the elements of ``iterable`` (which must all be strings) together,
    preceding each one with ``sep``
    """
    return sep[0:0].join(sep + s for s in iterable)

def join_separated(iterable, sep):
    """
    Join the elements of ``iterable`` (which must all be strings) together,
    separating consecutive elements with ``sep``
    """
    return sep.join(iterable)

def join_terminated(iterable, sep):
    """
    Join the elements of ``iterable`` (which must all be strings) together,
    terminating each one with ``sep``
    """
    return sep[0:0].join(s + sep for s in iterable)

def write_preceded(fp, iterable, sep):
    """
    Write the elements of ``iterable`` (which must all be strings) to ``fp``,
    preceding each one with ``sep``
    """
    for s in iterable:
        fp.write(sep)
        fp.write(s)

def write_separated(fp, iterable, sep):
    """
    Write the elements of ``iterable`` (which must all be strings) to ``fp``,
    separating consecutive elements with ``sep``
    """
    first = True
    for s in iterable:
        if first:
            first = False
        else:
            fp.write(sep)
        fp.write(s)

def write_terminated(fp, iterable, sep):
    """
    Write the elements of ``iterable`` (which must all be strings) to ``fp``,
    terminating each one with ``sep``
    """
    for s in iterable:
        fp.write(s)
        fp.write(sep)

def _join_pairs(iterable):
    """
    Concatenate each pair of consecutive strings in ``iterable``.  If there are
    an odd number of items in ``iterable``, the last one will be returned
    unmodified.
    """
    i = iter(iterable)
    while True:
        a = next(i)
        try:
            b = next(i)
        except StopIteration:
            yield a
            return
        else:
            yield a + b
