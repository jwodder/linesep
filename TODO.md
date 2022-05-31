- Add examples to the README showing regexes, writing, joining, & splitting

- Deprecate reading with a regex delimiter?

- Write more tests:
    - Make the `read_*` and `write_*` tests operate on actual files
    - Test splitting the same input with different `chunk_size` values (both
      prime and highly divisible)
    - Test empty separator?


New Features
------------
- Add functions for creating codecs that convert between `\n` and given
  separators? (cf. `io.IncrementalNewlineDecoder`)
- Give the `read_*` functions arguments for only accepting regex matches with
  certain buffers/surroundings?
- Add "incremental splitting" classes that are fed text piecemeal and output
  delimited items as each (non-regex) delimiter is encountered?
    - Include a convenience method that takes an iterable of strs and returns a
      generator of split strs
    - Add separate methods for feeding input without retrieving output,
      fetching one split item at a time, and querying whether there are any
      split items left to fetch?
    - Add a universal newlines incremental splitter?
