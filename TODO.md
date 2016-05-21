- Documentation:
    - Update README and module docstring
    - Add notes about potential pitfalls with regexes

        The only truly foolproof way to split on regexes is to read the whole
        file into memory, and if that's an option for you, you don't need this
        module anyway.

    - Point out in the README (and docstrings?) that the `read_*` functions
      read the files piecemeal rather than reading them entirely into memory
- Write tests
    - Test `write_*` and `join_*`
    - Test bytes
    - Search "data-driven testing"?
- Upload to PyPI
