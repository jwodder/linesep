import sys
import linesep

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io       import BytesIO as StringIO

def test_terminated_one_sep():
    assert list(linesep.read_terminated(StringIO('\n'), '\n', retain=False)) == ['']

def test_preceded_one_sep():
    assert list(linesep.read_preceded(StringIO('\n'), '\n', retain=False)) == ['']

def test_separated_one_sep():
    assert list(linesep.read_separated(StringIO('\n'), '\n', retain=False)) == ['', '']


def test_terminated_one_sep_retained():
    assert list(linesep.read_terminated(StringIO('\n'), '\n', retain=True)) == ['\n']

def test_preceded_one_sep_retained():
    assert list(linesep.read_preceded(StringIO('\n'), '\n', retain=True)) == ['\n']

def test_separated_one_sep_retained():
    assert list(linesep.read_separated(StringIO('\n'), '\n', retain=True)) == ['', '\n', '']
