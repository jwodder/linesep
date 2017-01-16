- Documentation:
    - Add notes about potential pitfalls with regexes

        The only truly foolproof way to split on regexes is to read the whole
        file into memory, and if that's an option for you, you don't need this
        module anyway.

    - Point out in the docstrings that the `read_*` functions read the files
      piecemeal rather than reading them entirely into memory?
    - Add examples to the README showing regexes, writing, joining, & splitting
    - Point out somewhere that the bytes/text nature of the input must match
      that of the separator
- Write more tests
- Make the `read_*` and `write_*` tests operate on actual files
- Feed `.coverage` files to Coveralls
- Test against and indicate support for Python 3.6 and pypy
- Create a Readthedocs site?

- Upload to PyPI

- Add a convenience function for reading/splitting on `\r\n?|\n`?
- Add a `read_paragraphs` function that treats two or more consecutive empty
  lines as a delimiter
- Add functions for creating codecs that convert between `\n` and given
  separators? (cf. `io.IncrementalNewlineDecoder`)
- For next version: Give the `read_*` functions arguments for only accepting
  regex matches with certain buffers/surroundings?
- idea: Reorganize the functions into three submodules — `separated`,
  `terminated`, and `preceded` — that each contain functions named `read`,
  `write`, `join`, and `split`
