import sys
import linesep

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io       import BytesIO as StringIO

def test_terminated_empty():
    assert list(linesep.read_terminated(StringIO(), '\n')) == []

def test_preceded_empty():
    assert list(linesep.read_preceded(StringIO(), '\n')) == []

def test_separated_empty():
    assert list(linesep.read_separated(StringIO(), '\n')) == ['']
