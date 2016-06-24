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
        "text": '',
        "sep": '\n',
        "preceded": [],
        "terminated": [],
        "separated": [''],
        "preceded_retained": [],
        "terminated_retained": [],
        "separated_retained": [''],
    }),

    ('no_sep', {
        "text": 'foo',
        "sep": '\n',
        "preceded": ['foo'],
        "terminated": ['foo'],
        "separated": ['foo'],
        "preceded_retained": ['foo'],
        "terminated_retained": ['foo'],
        "separated_retained": ['foo'],
    }),

    ('one_sep', {
        "text": '\n',
        "sep": '\n',
        "preceded": [''],
        "terminated": [''],
        "separated": ['', ''],
        "preceded_retained": ['\n'],
        "terminated_retained": ['\n'],
        "separated_retained": ['', '\n', ''],
    }),

    ('two_seps', {
        "text": '\n\n',
        "sep": '\n',
        "preceded": ['', ''],
        "terminated": ['', ''],
        "separated": ['', '', ''],
        "preceded_retained": ['\n', '\n'],
        "terminated_retained": ['\n', '\n'],
        "separated_retained": ['', '\n', '', '\n', ''],
    }),

    ('text_sep', {
        "text": 'foo\n',
        "sep": '\n',
        "preceded": ['foo', ''],
        "preceded_retained": ['foo', '\n'],
        "separated": ['foo', ''],
        "separated_retained": ['foo', '\n', ''],
        "terminated": ['foo'],
        "terminated_retained": ['foo\n']
    }),

    ('sep_text', {
        "text": '\nfoo',
        "sep": '\n',
        "preceded": ['foo'],
        "preceded_retained": ['\nfoo'],
        "separated": ['', 'foo'],
        "separated_retained": ['', '\n', 'foo'],
        "terminated": ['', 'foo'],
        "terminated_retained": ['\n', 'foo']
    }),

    ('text_sep_text', {
        "text": 'foo\nbar',
        "sep": '\n',
        "preceded": ['foo', 'bar'],
        "preceded_retained": ['foo', '\nbar'],
        "separated": ['foo', 'bar'],
        "separated_retained": ['foo', '\n', 'bar'],
        "terminated": ['foo', 'bar'],
        "terminated_retained": ['foo\n', 'bar']
    }),

    ('sep_text_sep', {
        "text": '\nfoo\n',
        "sep": '\n',
        "preceded": ['foo', ''],
        "preceded_retained": ["\nfoo", "\n"],
        "separated": ['', 'foo', ''],
        "separated_retained": ['', '\n', 'foo', '\n', ''],
        "terminated": ['', 'foo'],
        "terminated_retained": ['\n', 'foo\n'],
    }),

    ('regex01', {
        "text": 'abca|bc',
        "sep": re.compile(r'a|b'),
        "preceded": ['', 'c', '|', 'c'],
        "preceded_retained": ['a', 'bc', 'a|', 'bc'],
        "separated": ['', '', 'c', '|', 'c'],
        "separated_retained": ['', 'a', '', 'b', 'c', 'a', '|', 'b', 'c'],
        "terminated": ['', '', 'c', '|', 'c'],
        "terminated_retained": ['a', 'b', 'ca', '|b', 'c'],
    }),

    ('regex_literal', {
        "text": 'abca|bc',
        "sep": 'a|b',
        "preceded": ['abc', 'c'],
        "preceded_retained": ['abc', 'a|bc'],
        "separated": ['abc', 'c'],
        "separated_retained": ['abc', 'a|b', 'c'],
        "terminated": ['abc', 'c'],
        "terminated_retained": ['abca|b', 'c'],
    }),

    ('regex_groups', {
        "text": 'abca|bc',
        "sep": re.compile(r'(a)|(b)'),
        "preceded": ['', 'c', '|', 'c'],
        "preceded_retained": ['a', 'bc', 'a|', 'bc'],
        "separated": ['', '', 'c', '|', 'c'],
        "separated_retained": ['', 'a', '', 'b', 'c', 'a', '|', 'b', 'c'],
        "terminated": ['', '', 'c', '|', 'c'],
        "terminated_retained": ['a', 'b', 'ca', '|b', 'c'],
    }),

    ('straddling_delim', {
        "text": "This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |\r\n|  <--- There should be a split right there; is there?",
        "sep": "\r\n",
        "preceded": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", "|  <--- There should be a split right there; is there?"],
        "preceded_retained": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", "\r\n|  <--- There should be a split right there; is there?"],
        "separated": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", "|  <--- There should be a split right there; is there?"],
        "separated_retained": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", "\r\n", "|  <--- There should be a split right there; is there?"],
        "terminated": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |", "|  <--- There should be a split right there; is there?"],
        "terminated_retained": ["This test is intended to test splitting when the separator is a multicharacter delimiter that straddles the boundary between the 512-character chunks that the `read_*` functions divide their input into.  Unfortunately, I'm already bored of writing this test, and I still have 237 characters left to go.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco Here it comes  --->  |\r\n", "|  <--- There should be a split right there; is there?"],
    }),

    ('big_entry', {
        "text": "This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|\r\n| deserunt mollit anim id est laborum.",
        "sep": "\r\n",
        "preceded": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|", "| deserunt mollit anim id est laborum."],
        "preceded_retained": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|", "\r\n| deserunt mollit anim id est laborum."],
        "separated": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|", "| deserunt mollit anim id est laborum."],
        "separated_retained": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|", "\r\n", "| deserunt mollit anim id est laborum."],
        "terminated": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|", "| deserunt mollit anim id est laborum."],
        "terminated_retained": ["This test is intended to test splitting when a single entry is longer than the 512-character chunk size.  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.  Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia|\r\n", "| deserunt mollit anim id est laborum."],
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
    assert list(linesep.read_preceded(StringIO(text), sep, retain=False)) == preceded

def test_read_terminated(text, sep, terminated):
    assert list(linesep.read_terminated(StringIO(text), sep, retain=False)) == terminated

def test_read_separated(text, sep, separated):
    assert list(linesep.read_separated(StringIO(text), sep, retain=False)) == separated

def test_read_preceded_retained(text, sep, preceded_retained):
    assert list(linesep.read_preceded(StringIO(text), sep, retain=True)) == preceded_retained

def test_read_terminated_retained(text, sep, terminated_retained):
    assert list(linesep.read_terminated(StringIO(text), sep, retain=True)) == terminated_retained

def test_read_separated_retained(text, sep, separated_retained):
    assert list(linesep.read_separated(StringIO(text), sep, retain=True)) == separated_retained
