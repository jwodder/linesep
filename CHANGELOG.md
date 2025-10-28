v0.6.0 (in development)
-----------------------
- Support Python 3.14

v0.5.1 (2024-12-01)
-------------------
- Support Python 3.11, 3.12, and 3.13
- Migrated from setuptools to hatch
- Drop support for Python 3.7

v0.5.0 (2022-06-22)
-------------------
- Added `UnicodeNewlineSplitter` for incremental splitting on Unicode line
  ending sequences
- Added `ParagraphSplitter` for incremental splitting on blank lines

v0.4.0 (2022-06-17)
-------------------
- Passing a regular expression separator to a `read_*()` function is now
  deprecated, and support will be removed in version 1.0.
- Added `TerminatedSplitter`, `PrecededSplitter`, `SeparatedSplitter`, &
  `UniversalNewlineSplitter` classes and `get_newline_splitter()` function for
  incremental splitting of strings in chunks
- Drop support for Python 3.6
- Moved documentation from README file to a Read the Docs site

v0.3.1 (2022-05-31)
-------------------
- Support Python 3.10
- Refine return type annotation on `read_paragraphs()`

v0.3.0 (2020-12-02)
-------------------
- Added `ascii_splitlines()`, `read_paragraphs()`, and `split_paragraphs()`
  functions

v0.2.0 (2020-11-28)
-------------------
- Now support only Python 3.6 and up (tested through 3.9) and PyPy3
- Add type annotations
- Renamed the "`size`" parameter of the `read_*` functions to `chunk_size`
- Add API documentation to README

v0.1.1 (2017-05-29)
-------------------
- Remove a `PendingDeprecationWarning` generated in newer versions of Python
  3.5 and 3.6
- More testing infrastructure
- PyPy now supported

v0.1.0 (2017-01-16)
-------------------
Initial release
