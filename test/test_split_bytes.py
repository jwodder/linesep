from   io import BytesIO
import re
import linesep

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

    ('no_sep', {
        "text": b'foo',
        "sep": b'\n',
        "preceded": [b'foo'],
        "terminated": [b'foo'],
        "separated": [b'foo'],
        "preceded_retained": [b'foo'],
        "terminated_retained": [b'foo'],
        "separated_retained": [b'foo'],
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

    ('text_sep', {
        "text": b'foo\n',
        "sep": b'\n',
        "preceded": [b'foo', b''],
        "preceded_retained": [b'foo', b'\n'],
        "separated": [b'foo', b''],
        "separated_retained": [b'foo', b'\n', b''],
        "terminated": [b'foo'],
        "terminated_retained": [b'foo\n']
    }),

    ('sep_text', {
        "text": b'\nfoo',
        "sep": b'\n',
        "preceded": [b'foo'],
        "preceded_retained": [b'\nfoo'],
        "separated": [b'', b'foo'],
        "separated_retained": [b'', b'\n', b'foo'],
        "terminated": [b'', b'foo'],
        "terminated_retained": [b'\n', b'foo']
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

    ('sep_sep_text', {
        "text": b'\n\nfoo',
        "sep": b'\n',
        "preceded": [b'', b'foo'],
        "preceded_retained": [b"\n", b"\nfoo"],
        "separated": [b'', b'', b'foo'],
        "separated_retained": [b'', b'\n', b'', b'\n', b'foo'],
        "terminated": [b'', b'', b'foo'],
        "terminated_retained": [b'\n', b'\n', b'foo'],
    }),

    ('text_sep_sep', {
        "text": b'foo\n\n',
        "sep": b'\n',
        "preceded": [b'foo', b'', b''],
        "preceded_retained": [b'foo', b'\n', b'\n'],
        "separated": [b'foo', b'', b''],
        "separated_retained": [b'foo', b'\n', b'', b'\n', b''],
        "terminated": [b'foo', b''],
        "terminated_retained": [b'foo\n', b'\n'],
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
        "text": b"This test is intended to test splitting when the separator"
                b" is a multicharacter delimiter that straddles the boundary"
                b" between the 512-character chunks that the `read_*`"
                b" functions divide their input into.  Unfortunately, I'm"
                b" already bored of writing this test, and I still have 237"
                b" characters left to go.  Lorem ipsum dolor sit amet,"
                b" consectetur adipisicing elit, sed do eiusmod tempor"
                b" incididunt ut labore et dolore magna aliqua.  Ut enim ad"
                b" minim veniam, quis nostrud exercitation ullamco Here it"
                b" comes  --->  |\r\n|  <--- There should be a split right"
                b" there; is there?",
        "sep": b"\r\n",
        "preceded": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |",
            b"|  <--- There should be a split right there; is there?"
        ],
        "preceded_retained": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |",
            b"\r\n|  <--- There should be a split right there; is there?"
        ],
        "separated": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |",
            b"|  <--- There should be a split right there; is there?"
        ],
        "separated_retained": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |",
            b"\r\n",
            b"|  <--- There should be a split right there; is there?"
        ],
        "terminated": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |",
            b"|  <--- There should be a split right there; is there?"
        ],
        "terminated_retained": [
            b"This test is intended to test splitting when the separator is a"
            b" multicharacter delimiter that straddles the boundary between"
            b" the 512-character chunks that the `read_*` functions divide"
            b" their input into.  Unfortunately, I'm already bored of writing"
            b" this test, and I still have 237 characters left to go.  Lorem"
            b" ipsum dolor sit amet, consectetur adipisicing elit, sed do"
            b" eiusmod tempor incididunt ut labore et dolore magna aliqua.  Ut"
            b" enim ad minim veniam, quis nostrud exercitation ullamco Here it"
            b" comes  --->  |\r\n",
            b"|  <--- There should be a split right there; is there?"
        ],
    }),

    ('big_entry', {
        "text": b"This test is intended to test splitting when a single entry"
                b" is longer than the 512-character chunk size.  Lorem ipsum"
                b" dolor sit amet, consectetur adipisicing elit, sed do"
                b" eiusmod tempor incididunt ut labore et dolore magna aliqua."
                b"  Ut enim ad minim veniam, quis nostrud exercitation ullamco"
                b" laboris nisi ut aliquip ex ea commodo consequat.  Duis aute"
                b" irure dolor in reprehenderit in voluptate velit esse cillum"
                b" dolore eu fugiat nulla pariatur.  Excepteur sint occaecat"
                b" cupidatat non proident, sunt in culpa qui officia|\r\n|"
                b" deserunt mollit anim id est laborum.",
        "sep": b"\r\n",
        "preceded": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|",
            b"| deserunt mollit anim id est laborum."
        ],
        "preceded_retained": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|",
            b"\r\n| deserunt mollit anim id est laborum."
        ],
        "separated": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|",
            b"| deserunt mollit anim id est laborum."
        ],
        "separated_retained": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|",
            b"\r\n",
            b"| deserunt mollit anim id est laborum."
        ],
        "terminated": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|",
            b"| deserunt mollit anim id est laborum."
        ],
        "terminated_retained": [
            b"This test is intended to test splitting when a single entry is"
            b" longer than the 512-character chunk size.  Lorem ipsum dolor"
            b" sit amet, consectetur adipisicing elit, sed do eiusmod tempor"
            b" incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            b" veniam, quis nostrud exercitation ullamco laboris nisi ut"
            b" aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            b" reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            b" nulla pariatur.  Excepteur sint occaecat cupidatat non"
            b" proident, sunt in culpa qui officia|\r\n",
            b"| deserunt mollit anim id est laborum."
        ],
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
    assert linesep.split_terminated(text, sep, retain=True) \
        == terminated_retained

def test_split_separated_retained(text, sep, separated_retained):
    assert linesep.split_separated(text, sep, retain=True) == separated_retained

def test_read_preceded(text, sep, preceded):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=False)) \
        == preceded

def test_read_terminated(text, sep, terminated):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=False)) \
        == terminated

def test_read_separated(text, sep, separated):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=False)) \
        == separated

def test_read_preceded_retained(text, sep, preceded_retained):
    assert list(linesep.read_preceded(BytesIO(text), sep, retain=True)) \
        == preceded_retained

def test_read_terminated_retained(text, sep, terminated_retained):
    assert list(linesep.read_terminated(BytesIO(text), sep, retain=True)) \
        == terminated_retained

def test_read_separated_retained(text, sep, separated_retained):
    assert list(linesep.read_separated(BytesIO(text), sep, retain=True)) \
        == separated_retained
