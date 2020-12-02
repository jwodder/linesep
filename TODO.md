- Add examples to the README showing regexes, writing, joining, & splitting

- Deprecate reading with a regex delimiter?

- Write more tests:
    - Make the `read_*` and `write_*` tests operate on actual files
    - Test splitting the same input with different `chunk_size` values (both
      prime and highly divisible)
    - Test empty separator?
    - Test splitting a Unicode string on one of the bytes in its UTF-8 encoding
    - Test text containing Unicode
    - Test bytes containing Unicode


New Features
------------
- Add functions for creating codecs that convert between `\n` and given
  separators? (cf. `io.IncrementalNewlineDecoder`)
- Give the `read_*` functions arguments for only accepting regex matches with
  certain buffers/surroundings?
