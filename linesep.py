# -*- coding: utf-8 -*-
"""
Handling lines with arbitrary separators

This module provides basic functions for reading & writing text with custom
line separators that can occur either before, between, or after lines — though
its primary purpose is actually to allow me to experiment with proper Python
packaging & testing procedures.  Being actually useful is not its #1 goal.

Visit <https://github.com/jwodder/linesep> for more information.
"""

__version__      = '0.2.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'linesep@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/linesep'

import re

def read_preceded(fp, sep, retain=False, size=512):
    """
    Read lines from a file-like object ``fp`` in which the beginning of each
    line is indicated by the string or compiled regex ``sep``.  A generator of
    lines is returned; an empty file will always produce an empty generator.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the start of a new
        line wherever it occurs
    :param bool retain: whether to include the delimiters at the beginning of
        each line
    :param int size: how many bytes or characters to read from ``fp`` at a time
    :return: a generator of the lines in ``fp``
    :rtype: generator of binary or text strings
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
    Read lines from a file-like object ``fp`` in which lines are separated by
    the string or compiled regex ``sep``.  A generator of lines is returned; an
    empty file will always produce a generator with one element, the empty
    string.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the end of one line
        and the beginning of another wherever it occurs
    :param bool retain: When `True`, the line separators will be included in
        the output, with the elements of the generator alternating between
        lines and separators, starting with a (possibly empty) line
    :param int size: how many bytes or characters to read from ``fp`` at a time
    :return: a generator of the lines in ``fp``
    :rtype: generator of binary or text strings
    """
    # http://stackoverflow.com/a/7054512/744178
    if not hasattr(sep, 'match'):
        sep = re.compile(re.escape(sep))
    empty = fp.read(0)  # b'' or u'' as appropriate
    buff = empty
    for chunk in iter(lambda: fp.read(size), empty):
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
    Read lines from a file-like object ``fp`` in which the end of each line is
    indicated by the string or compiled regex ``sep``.  A generator of lines is
    returned; an empty file will always produce an empty generator.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the end of a line
        wherever it occurs
    :param bool retain: whether to include the delimiters at the end of each
        line
    :param int size: how many bytes or characters to read from ``fp`` at a time
    :return: a generator of the lines in ``fp``
    :rtype: generator of binary or text strings
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
    Split a string ``s`` into zero or more lines starting with/preceded by the
    string or compiled regex ``sep``.  A list of lines is returned; an empty
    input string will always produce an empty list.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the start of a new
        line wherever it occurs
    :param bool retain: whether to include the delimiters at the beginning of
        each line
    :return: a list of the lines in ``s``
    :rtype: list of binary or text strings
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries[0:] = list(_join_pairs(entries[1:]))
    if not entries[0]:
        entries.pop(0)
    return entries

def split_separated(s, sep, retain=False):
    """
    Split a string ``s`` into one or more lines separated by the string or
    compiled regex ``sep``.  A list of lines is returned; an empty input string
    will always produce a list with one element, the empty string.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the end of one line
        and the beginning of another wherever it occurs
    :param bool retain: When `True`, the line separators will be included in
        the output, with the elements of the list alternating between lines and
        separators, starting with a (possibly empty) line
    :return: a list of the lines in ``s``
    :rtype: list of binary or text strings
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
    Split a string ``s`` into zero or more lines terminated by the
    string or compiled regex ``sep``.  A list of lines is returned; an empty
    input string will always produce an empty list.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the end of a line
        wherever it occurs
    :param bool retain: whether to include the delimiters at the end of each
        line
    :return: a list of the lines in ``s``
    :rtype: list of binary or text strings
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries = list(_join_pairs(entries))
    if not entries[-1]:
        entries.pop()
    return entries

def join_preceded(iterable, sep):
    """
    Join the elements of ``iterable`` together, preceding each one with ``sep``

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep[0:0].join(sep + s for s in iterable)

def join_separated(iterable, sep):
    """
    Join the elements of ``iterable`` together, separating consecutive elements
    with ``sep``

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep.join(iterable)

def join_terminated(iterable, sep):
    """
    Join the elements of ``iterable`` together, appending ``sep`` to each one

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep[0:0].join(s + sep for s in iterable)

def write_preceded(fp, iterable, sep):
    """
    Write the elements of ``iterable`` to ``fp``, preceding each one with
    ``sep``

    :param fp: a binary or text file-like object
    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :return: `None`
    """
    for s in iterable:
        fp.write(sep)
        fp.write(s)

def write_separated(fp, iterable, sep):
    """
    Write the elements of ``iterable`` to ``fp``, separating consecutive
    elements with ``sep``

    :param fp: a binary or text file-like object
    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :return: `None`
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
    Write the elements of ``iterable`` to ``fp``, appending ``sep`` to each one

    :param fp: a binary or text file-like object
    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :return: `None`
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
    for a in i:
        try:
            b = next(i)
        except StopIteration:
            yield a
            return
        else:
            yield a + b
