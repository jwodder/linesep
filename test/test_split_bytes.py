import re
import linesep

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io       import BytesIO

# Based on <https://pytest.org/latest/example/parametrize.html#a-quick-port-of-testscenarios>
def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for scenario in metafunc.module.scenarios:
        idlist.append(scenario[0])
        argvalues.append([scenario[1][argname] for argname in metafunc.fixturenames])
    metafunc.parametrize(metafunc.fixturenames, argvalues, ids=idlist, scope="module")

scenarios = [

    ('empty', {
        "text": b'',
        "sep": b'\n',
        "preceded": [],
        "terminated": [],
        "separated": [b''],
        "preceded_retained": [],
        "terminated_retained": [],
        "separated_retained": [b''],
    }),

    ('one_sep', {
        "text": b'\n',
        "sep": b'\n',
        "preceded": [b''],
        "terminated": [b''],
        "separated": [b'', b''],
        "preceded_retained": [b'\n'],
        "terminated_retained": [b'\n'],
        "separated_retained": [b'', b'\n', b''],
    }),

    ('two_seps', {
        "text": b'\n\n',
        "sep": b'\n',
        "preceded": [b'', b''],
        "terminated": [b'', b''],
        "separated": [b'', b'', b''],
        "preceded_retained": [b'\n', b'\n'],
        "terminated_retained": [b'\n', b'\n'],
        "separated_retained": [b'', b'\n', b'', b'\n', b''],
    }),

    ('text_sep_text', {
        "text": b'foo\nbar',
        "sep": b'\n',
        "preceded": [b'foo', b'bar'],
        "preceded_retained": [b'foo', b'\nbar'],
        "separated": [b'foo', b'bar'],
        "separated_retained": [b'foo', b'\n', b'bar'],
        "terminated": [b'foo', b'bar'],
        "terminated_retained": [b'foo\n', b'bar']
    }),

    ('sep_text_sep', {
        "text": b'\nfoo\n',
        "sep": b'\n',
        "preceded": [b'foo', b''],
        "preceded_retained": [b"\nfoo", b"\n"],
        "separated": [b'', b'foo', b''],
        "separated_retained": [b'', b'\n', b'foo', b'\n', b''],
        "terminated": [b'', b'foo'],
        "terminated_retained": [b'\n', b'foo\n'],
    }),

    ('regex01', {
        "text": b'abca|bc',
        "sep": re.compile(br'a|b'),
        "preceded": [b'', b'c', b'|', b'c'],
        "preceded_retained": [b'a', b'bc', b'a|', b'bc'],
        "separated": [b'', b'', b'c', b'|', b'c'],
        "separated_retained": [b'', b'a', b'', b'b', b'c', b'a', b'|', b'b', b'c'],
        "terminated": [b'', b'', b'c', b'|', b'c'],
        "terminated_retained": [b'a', b'b', b'ca', b'|b', b'c'],
    }),

    ('regex_literal', {
        "text": b'abca|bc',
        "sep": b'a|b',
        "preceded": [b'abc', b'c'],
        "preceded_retained": [b'abc', b'a|bc'],
        "separated": [b'abc', b'c'],
        "separated_retained": [b'abc', b'a|b', b'c'],
        "terminated": [b'abc', b'c'],
        "terminated_retained": [b'abca|b', b'c'],
    }),

    ('regex_groups', {
        "text": b'abca|bc',
        "sep": re.compile(br'(a)|(b)'),
        "preceded": [b'', b'c', b'|', b'c'],
        "preceded_retained": [b'a', b'bc', b'a|', b'bc'],
        "separated": [b'', b'', b'c', b'|', b'c'],
        "separated_retained": [b'', b'a', b'', b'b', b'c', b'a', b'|', b'b', b'c'],
        "terminated": [b'', b'', b'c', b'|', b'c'],
        "terminated_retained": [b'a', b'b', b'ca', b'|b', b'c'],
    }),

    ('straddling_delim', {
        "text": b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |\r\n|  <--- There should be a split right there; is there?",
        "sep": b"\r\n",
        "preceded": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", b"|  <--- There should be a split right there; is there?"],
        "preceded_retained": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", b"\r\n|  <--- There should be a split right there; is there?"],
        "separated": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", b"|  <--- There should be a split right there; is there?"],
        "separated_retained": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", b"\r\n", b"|  <--- There should be a split right there; is there?"],
        "terminated": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", b"|  <--- There should be a split right there; is there?"],
        "terminated_retained": [b"This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |\r\n", b"|  <--- There should be a split right there; is there?"],
    }),

]

def test_split_preceded(text, sep, preceded):
    assert linesep.split_preceded(text, sep, retain=False) == preceded

def test_split_terminated(text, sep, terminated):
    assert linesep.split_terminated(text, sep, retain=False) == terminated

def test_split_separated(text, sep, separated):
    assert linesep.split_separated(text, sep, retain=False) == separated

def test_split_preceded_retained(text, sep, preceded_retained):
    assert linesep.split_preceded(text, sep, retain=True) == preceded_retained

def test_split_terminated_retained(text, sep, terminated_retained):
    assert linesep.split_terminated(text, sep, retain=True) == terminated_retained

def test_split_separated_retained(text, sep, separated_retained):
    assert linesep.split_separated(text, sep, retain=True) == separated_retained

def test_read_preceded(text, sep, preceded):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=False)) == preceded

def test_read_terminated(text, sep, terminated):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=False)) == terminated

def test_read_separated(text, sep, separated):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=False)) == separated

def test_read_preceded_retained(text, sep, preceded_retained):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=True)) == preceded_retained

def test_read_terminated_retained(text, sep, terminated_retained):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=True)) == terminated_retained

def test_read_separated_retained(text, sep, separated_retained):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=True)) == separated_retained
