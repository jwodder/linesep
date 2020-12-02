"""
Handling lines with arbitrary separators

``linesep`` provides basic functions for reading, writing, splitting, & joining
text with custom separators that can occur either before, between, or after
the segments they separate.

Visit <https://github.com/jwodder/linesep> for more information.
"""

__version__      = '0.3.0'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'linesep@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/linesep'

__all__ = [
    "ascii_splitlines",
    "join_preceded",
    "join_separated",
    "join_terminated",
    "read_paragraphs",
    "read_preceded",
    "read_separated",
    "read_terminated",
    "split_paragraphs",
    "split_preceded",
    "split_separated",
    "split_terminated",
    "write_preceded",
    "write_separated",
    "write_terminated",
]

import re
import sys
from   typing import AnyStr, IO, Union

if sys.version_info[:2] >= (3,9):
    from collections.abc import Iterable, Iterator
    from re import Pattern
    List = list
else:
    from typing import Iterable, Iterator, List, Pattern

def read_preceded(
    fp: IO[AnyStr],
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
    chunk_size: int = 512,
) -> Iterator[AnyStr]:
    """
    Read segments from a file-like object ``fp`` in which the beginning of each
    segment is indicated by the string or compiled regex ``sep``.  A generator
    of segments is returned; an empty file will always produce an empty
    generator.

    Data is read from the filehandle ``chunk_size`` characters at a time.  If
    ``sep`` is a variable-length compiled regex and a delimiter in the file
    crosses a chunk boundary, the results are undefined.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the start of a new
        segment wherever it occurs
    :param bool retain: whether to include the delimiters at the beginning of
        each segment
    :param int chunk_size: how many bytes or characters to read from ``fp`` at
        a time
    :return: a generator of the segments in ``fp``
    :rtype: generator of binary or text strings
    """
    # Omits empty leading entry
    entries = read_separated(fp, sep, retain=retain, chunk_size=chunk_size)
    e = next(entries)
    if e:
        yield e
    if retain:
        entries = _join_pairs(entries)
    for e in entries:
        yield e

def read_separated(
    fp: IO[AnyStr],
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
    chunk_size: int = 512,
) -> Iterator[AnyStr]:
    """
    Read segments from a file-like object ``fp`` in which segments are
    separated by the string or compiled regex ``sep``.  A generator of segments
    is returned; an empty file will always produce a generator with one
    element, the empty string.

    Data is read from the filehandle ``chunk_size`` characters at a time.  If
    ``sep`` is a variable-length compiled regex and a delimiter in the file
    crosses a chunk boundary, the results are undefined.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the end of one
        segment and the beginning of another wherever it occurs
    :param bool retain: When `True`, the segment separators will be included in
        the output, with the elements of the generator alternating between
        segments and separators, starting with a (possibly empty) segment
    :param int chunk_size: how many bytes or characters to read from ``fp`` at
        a time
    :return: a generator of the segments in ``fp``
    :rtype: generator of binary or text strings
    """
    seppattern = _ensure_compiled(sep)
    empty = fp.read(0)  # b'' or u'' as appropriate
    buff = empty
    for chunk in iter(lambda: fp.read(chunk_size), empty):
        buff += chunk
        lastend = 0
        for m in seppattern.finditer(buff):
            yield buff[lastend:m.start()]
            if retain:
                yield m.group()
            lastend = m.end()
        buff = buff[lastend:]
    yield buff

def read_terminated(
    fp: IO[AnyStr],
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
    chunk_size: int = 512,
) -> Iterator[AnyStr]:
    """
    Read segments from a file-like object ``fp`` in which the end of each
    segment is indicated by the string or compiled regex ``sep``.  A generator
    of segments is returned; an empty file will always produce an empty
    generator.

    Data is read from the filehandle ``chunk_size`` characters at a time.  If
    ``sep`` is a variable-length compiled regex and a delimiter in the file
    crosses a chunk boundary, the results are undefined.

    :param fp: a binary or text file-like object
    :param sep: a string or compiled regex that indicates the end of a segment
        wherever it occurs
    :param bool retain: whether to include the delimiters at the end of each
        segment
    :param int chunk_size: how many bytes or characters to read from ``fp`` at
        a time
    :return: a generator of the segments in ``fp``
    :rtype: generator of binary or text strings
    """
    # Omits empty trailing entry
    prev = None
    entries = read_separated(fp, sep, retain=retain, chunk_size=chunk_size)
    if retain:
        entries = _join_pairs(entries)
    for e in entries:
        if prev is not None:
            yield prev
        prev = e
    if prev:
        yield prev

def split_preceded(
    s: AnyStr,
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
) -> List[AnyStr]:
    """
    Split a string ``s`` into zero or more segments starting with/preceded by
    the string or compiled regex ``sep``.  A list of segments is returned; an
    empty input string will always produce an empty list.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the start of a new
        segment wherever it occurs
    :param bool retain: whether to include the delimiters at the beginning of
        each segment
    :return: a list of the segments in ``s``
    :rtype: list of binary or text strings
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries[1:] = list(_join_pairs(entries[1:]))
    if not entries[0]:
        entries.pop(0)
    return entries

def split_separated(
    s: AnyStr,
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
) -> List[AnyStr]:
    """
    Split a string ``s`` into one or more segments separated by the string or
    compiled regex ``sep``.  A list of segments is returned; an empty input
    string will always produce a list with one element, the empty string.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the end of one
        segment and the beginning of another wherever it occurs
    :param bool retain: When `True`, the segment separators will be included in
        the output, with the elements of the list alternating between segments
        and separators, starting with a (possibly empty) segment
    :return: a list of the segments in ``s``
    :rtype: list of binary or text strings
    """
    seppattern = _ensure_compiled(sep)
    entries = []
    lastend = 0
    for m in seppattern.finditer(s):
        entries.append(s[lastend:m.start()])
        if retain:
            entries.append(m.group())
        lastend = m.end()
    entries.append(s[lastend:])
    return entries

def split_terminated(
    s: AnyStr,
    sep: Union[AnyStr, Pattern[AnyStr]],
    retain: bool = False,
) -> List[AnyStr]:
    """
    Split a string ``s`` into zero or more segments terminated by the
    string or compiled regex ``sep``.  A list of segments is returned; an empty
    input string will always produce an empty list.

    :param s: a binary or text string
    :param sep: a string or compiled regex that indicates the end of a segment
        wherever it occurs
    :param bool retain: whether to include the delimiters at the end of each
        segment
    :return: a list of the segments in ``s``
    :rtype: list of binary or text strings
    """
    entries = split_separated(s, sep, retain)
    if retain:
        entries = list(_join_pairs(entries))
    if not entries[-1]:
        entries.pop()
    return entries

def join_preceded(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr:
    """
    Join the elements of ``iterable`` together, preceding each one with ``sep``

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep[0:0].join(sep + s for s in iterable)

def join_separated(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr:
    """
    Join the elements of ``iterable`` together, separating consecutive elements
    with ``sep``

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep.join(iterable)

def join_terminated(iterable: Iterable[AnyStr], sep: AnyStr) -> AnyStr:
    """
    Join the elements of ``iterable`` together, appending ``sep`` to each one

    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :rtype: a binary or text string
    """
    return sep[0:0].join(s + sep for s in iterable)

def write_preceded(fp: IO[AnyStr], iterable: Iterable[AnyStr], sep: AnyStr) -> None:
    """
    Write the elements of ``iterable`` to the filehandle ``fp``, preceding each
    one with ``sep``

    :param fp: a binary or text file-like object
    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :return: `None`
    """
    for s in iterable:
        fp.write(sep)
        fp.write(s)

def write_separated(fp: IO[AnyStr], iterable: Iterable[AnyStr], sep: AnyStr) -> None:
    """
    Write the elements of ``iterable`` to the filehandle ``fp``, separating
    consecutive elements with ``sep``

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

def write_terminated(fp: IO[AnyStr], iterable: Iterable[AnyStr], sep: AnyStr) -> None:
    """
    Write the elements of ``iterable`` to the filehandle ``fp``, appending
    ``sep`` to each one

    :param fp: a binary or text file-like object
    :param iterable: an iterable of binary or text strings
    :param sep: a binary or text string
    :return: `None`
    """
    for s in iterable:
        fp.write(s)
        fp.write(sep)

def _join_pairs(iterable: Iterable[AnyStr]) -> Iterator[AnyStr]:
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

def _ensure_compiled(sep: Union[AnyStr, Pattern[AnyStr]]) -> Pattern[AnyStr]:
    if isinstance(sep, (bytes, str)):
        return re.compile(re.escape(sep))
    else:
        return sep

_EOL_RGX = re.compile(r'\r\n?|\n')

def ascii_splitlines(s: str, keepends: bool = False) -> List[str]:
    """
    .. versionadded:: 0.3.0

    Like `str.splitlines()`, except it only treats LF, CR LF, and CR as line
    endings
    """
    lines = []
    lastend = 0
    for m in _EOL_RGX.finditer(s):
        if keepends:
            lines.append(s[lastend:m.end()])
        else:
            lines.append(s[lastend:m.start()])
        lastend = m.end()
    if lastend < len(s):
        lines.append(s[lastend:])
    return lines

def read_paragraphs(fp: Iterable[str]) -> Iterable[str]:
    """
    .. versionadded:: 0.3.0

    Read a text filehandle or other iterable of lines (with trailing line
    endings retained) paragraph by paragraph.  Each paragraph is terminated by
    one or more blank lines (i.e., lines containining only a line ending).
    Trailing and embedded line endings in each paragraph are retained.

    Only LF, CR LF, and CR are recognized as line endings.
    """
    para: List[str] = []
    for line in fp:
        if not _is_blank(line) and para and _is_blank(para[-1]):
            yield ''.join(para)
            para = [line]
        else:
            para.append(line)
    if para:
        yield ''.join(para)

def _is_blank(line: str) -> bool:
    return line in ('\n', '\r', '\r\n')

_EOL_RGX2 = r'(?:\r\n|\r(?!\n)|\n)'
_EOPARA_RGX = re.compile(fr'\A{_EOL_RGX2}+|{_EOL_RGX2}{{2,}}')

def split_paragraphs(s: str) -> List[str]:
    """
    .. versionadded:: 0.3.0

    Split a string into paragraphs, each one terminated by one or more blank
    lines (i.e., lines containining only a line ending).  Trailing and embedded
    line endings in each paragraph are retained.

    Only LF, CR LF, and CR are recognized as line endings.
    """
    return split_terminated(s, _EOPARA_RGX, retain=True)
