import pytest
from linesep import (
    join_preceded,
    join_separated,
    join_terminated,
    write_preceded,
    write_separated,
    write_terminated,
)

SCENARIOS = [
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


@pytest.mark.parametrize(
    "joiner,writer,entries,sep,joined",
    [
        pytest.param(joiner, writer, v["entries"], v["sep"], v[mode], id=k)
        for k, v in SCENARIOS
        for joiner, writer, mode in [
            (join_separated, write_separated, "separated"),
            (join_terminated, write_terminated, "terminated"),
            (join_preceded, write_preceded, "preceded"),
        ]
    ],
)
def test_join(subtests, joiner, writer, entries, sep, joined, tmp_path):
    bentries = [e.encode("utf-8") for e in entries]
    with subtests.test("join-str"):
        assert joiner(entries, sep) == joined
    with subtests.test("join-bytes"):
        assert joiner(bentries, sep.encode("utf-8")) == joined.encode("utf-8")
    with subtests.test("write-str"):
        p = tmp_path / "text"
        with p.open("w", newline="") as fp:
            writer(fp, entries, sep)
        with p.open(encoding="utf-8", newline="") as fp:
            assert fp.read() == joined
    with subtests.test("write-bytes"):
        p = tmp_path / "bytes"
        with p.open("wb") as fp:
            writer(fp, bentries, sep.encode("utf-8"))
        assert p.read_bytes() == joined.encode("utf-8")
