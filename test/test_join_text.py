from   __future__ import unicode_literals
import re
import linesep

try:
    from StringIO import StringIO
except ImportError:
    from io       import StringIO

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
        "entries": [],
        "sep": '\n',
        "preceded": '',
        "terminated": '',
        "separated": '',
    }),

    ('empty_str', {
        "entries": [''],
        "sep": '\n',
        "preceded": '\n',
        "terminated": '\n',
        "separated": '',
    }),

]

def test_join_preceded(entries, sep, preceded):
    assert linesep.join_preceded(entries, sep) == preceded

def test_join_terminated(entries, sep, terminated):
    assert linesep.join_terminated(entries, sep) == terminated

def test_join_separated(entries, sep, separated):
    assert linesep.join_separated(entries, sep) == separated

def test_write_preceded(entries, sep, preceded):
    fp = StringIO()
    linesep.write_preceded(fp, entries, sep)
    assert fp.getvalue() == preceded

def test_write_terminated(entries, sep, terminated):
    fp = StringIO()
    linesep.write_terminated(fp, entries, sep)
    assert fp.getvalue() == terminated

def test_write_separated(entries, sep, separated):
    fp = StringIO()
    linesep.write_separated(fp, entries, sep)
    assert fp.getvalue() == separated
