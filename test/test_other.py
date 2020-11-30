import pytest
from   linesep import ascii_splitlines

@pytest.mark.parametrize('s,lines', [
    ('', []),
    ('foobar', ['foobar']),
    ('foo\n', ['foo']),
    ('foo\r', ['foo']),
    ('foo\r\n', ['foo']),
    ('foo\n\r', ['foo', '']),
    ('foo\nbar', ['foo', 'bar']),
    ('foo\rbar', ['foo', 'bar']),
    ('foo\r\nbar', ['foo', 'bar']),
    ('foo\n\rbar', ['foo', '', 'bar']),
    ('foo\n\nbar', ['foo', '', 'bar']),
    ('foo\n\nbar\n', ['foo', '', 'bar']),
    (
        'Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029'
        'characters?',
        ['Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029'
         'characters?'],
    ),
])
def test_ascii_splitlines(s, lines):
    assert ascii_splitlines(s) == lines

@pytest.mark.parametrize('s,lines', [
    ('', []),
    ('foobar', ['foobar']),
    ('foo\n', ['foo\n']),
    ('foo\r', ['foo\r']),
    ('foo\r\n', ['foo\r\n']),
    ('foo\n\r', ['foo\n', '\r']),
    ('foo\nbar', ['foo\n', 'bar']),
    ('foo\rbar', ['foo\r', 'bar']),
    ('foo\r\nbar', ['foo\r\n', 'bar']),
    ('foo\n\rbar', ['foo\n', '\r', 'bar']),
    ('foo\n\nbar', ['foo\n', '\n', 'bar']),
    ('foo\n\nbar\n', ['foo\n', '\n', 'bar\n']),
    (
        'Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029'
        'characters?',
        ['Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029'
         'characters?'],
    ),
])
def test_ascii_splitlines_keepends(s, lines):
    assert ascii_splitlines(s, keepends=True) == lines
