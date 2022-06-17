"""
Handling lines with arbitrary separators

``linesep`` provides basic functions for reading, writing, splitting, & joining
text with custom separators that can occur either before, between, or after
the segments they separate.

Visit <https://github.com/jwodder/linesep> or <https://linesep.rtfd.io> for
more information.
"""

__version__ = "0.4.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "linesep@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/linesep"

from .funcs import (
    ascii_splitlines,
    join_preceded,
    join_separated,
    join_terminated,
    read_paragraphs,
    read_preceded,
    read_separated,
    read_terminated,
    split_paragraphs,
    split_preceded,
    split_separated,
    split_terminated,
    write_preceded,
    write_separated,
    write_terminated,
)
from .splitters import (
    PrecededSplitter,
    SeparatedSplitter,
    Splitter,
    SplitterClosedError,
    SplitterEmptyError,
    SplitterState,
    TerminatedSplitter,
    UniversalNewlineSplitter,
    get_newline_splitter,
)

__all__ = [
    "PrecededSplitter",
    "SeparatedSplitter",
    "Splitter",
    "SplitterClosedError",
    "SplitterEmptyError",
    "SplitterState",
    "TerminatedSplitter",
    "UniversalNewlineSplitter",
    "ascii_splitlines",
    "get_newline_splitter",
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
