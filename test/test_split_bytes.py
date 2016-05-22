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

]

def test_split_preceded(text, sep, preceded, **_):
    assert linesep.split_preceded(text, sep, retain=False) == preceded

def test_split_terminated(text, sep, terminated, **_):
    assert linesep.split_terminated(text, sep, retain=False) == terminated

def test_split_separated(text, sep, separated, **_):
    assert linesep.split_separated(text, sep, retain=False) == separated

def test_split_preceded_retained(text, sep, preceded_retained, **_):
    assert linesep.split_preceded(text, sep, retain=True) == preceded_retained

def test_split_terminated_retained(text, sep, terminated_retained, **_):
    assert linesep.split_terminated(text, sep, retain=True) == terminated_retained

def test_split_separated_retained(text, sep, separated_retained, **_):
    assert linesep.split_separated(text, sep, retain=True) == separated_retained

def test_read_preceded(text, sep, preceded, **_):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=False)) == preceded

def test_read_terminated(text, sep, terminated, **_):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=False)) == terminated

def test_read_separated(text, sep, separated, **_):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=False)) == separated

def test_read_preceded_retained(text, sep, preceded_retained, **_):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=True)) == preceded_retained

def test_read_terminated_retained(text, sep, terminated_retained, **_):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=True)) == terminated_retained

def test_read_separated_retained(text, sep, separated_retained, **_):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=True)) == separated_retained
