import linesep

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io       import BytesIO

scenarios = [

    ('empty', {
        "entries": [],
        "sep": b'\n',
        "preceded": b'',
        "terminated": b'',
        "separated": b'',
    }),

    ('empty_str', {
        "entries": [b''],
        "sep": b'\n',
        "preceded": b'\n',
        "terminated": b'\n',
        "separated": b'',
    }),

    ('nonempty', {
        "entries": [b'foo'],
        "sep": b'\n',
        "preceded": b'\nfoo',
        "terminated": b'foo\n',
        "separated": b'foo',
    }),

    ('two_nonempty', {
        "entries": [b'foo', b'bar'],
        "sep": b'\n',
        "preceded": b'\nfoo\nbar',
        "terminated": b'foo\nbar\n',
        "separated": b'foo\nbar',
    }),

]

def test_join_preceded(entries, sep, preceded):
    assert linesep.join_preceded(entries, sep) == preceded

def test_join_terminated(entries, sep, terminated):
    assert linesep.join_terminated(entries, sep) == terminated

def test_join_separated(entries, sep, separated):
    assert linesep.join_separated(entries, sep) == separated

def test_write_preceded(entries, sep, preceded):
    fp = BytesIO()
    linesep.write_preceded(fp, entries, sep)
    assert fp.getvalue() == preceded

def test_write_terminated(entries, sep, terminated):
    fp = BytesIO()
    linesep.write_terminated(fp, entries, sep)
    assert fp.getvalue() == terminated

def test_write_separated(entries, sep, separated):
    fp = BytesIO()
    linesep.write_separated(fp, entries, sep)
    assert fp.getvalue() == separated
