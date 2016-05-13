import linesep

try:
    from StringIO import StringIO
except ImportError:
    from io       import BytesIO as StringIO

def test_terminated_empty():
    assert list(linesep.read_terminated(StringIO(), '\n')) == []

def test_preceded_empty():
    assert list(linesep.read_preceded(StringIO(), '\n')) == []

def test_separated_empty():
    assert list(linesep.read_separated(StringIO(), '\n')) == ['']
