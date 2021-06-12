from io import StringIO
import linesep

scenarios = [
    (
        "empty",
        {
            "entries": [],
            "sep": "\n",
            "preceded": "",
            "terminated": "",
            "separated": "",
        },
    ),
    (
        "empty_str",
        {
            "entries": [""],
            "sep": "\n",
            "preceded": "\n",
            "terminated": "\n",
            "separated": "",
        },
    ),
    (
        "nonempty",
        {
            "entries": ["foo"],
            "sep": "\n",
            "preceded": "\nfoo",
            "terminated": "foo\n",
            "separated": "foo",
        },
    ),
    (
        "two_nonempty",
        {
            "entries": ["foo", "bar"],
            "sep": "\n",
            "preceded": "\nfoo\nbar",
            "terminated": "foo\nbar\n",
            "separated": "foo\nbar",
        },
    ),
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
