from __future__ import annotations
import pytest
from pytest_subtests import SubTests
from linesep import (
    PrecededSplitter,
    SeparatedSplitter,
    SplitterClosedError,
    SplitterEmptyError,
    TerminatedSplitter,
)
from linesep.splitters import ConstantSplitter


def encode_list(txt: list[str]) -> list[bytes]:
    return [s.encode("utf-8") for s in txt]


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], []),
        ("\0", True, [""], [[]], []),
        ("\0", False, ["foo"], [[]], ["foo"]),
        ("\0", True, ["foo"], [[]], ["foo"]),
        ("\0", False, ["\0"], [[""]], []),
        ("\0", True, ["\0"], [["\0"]], []),
        ("\0", False, ["\0\0"], [["", ""]], []),
        ("\0", True, ["\0\0"], [["\0", "\0"]], []),
        ("\0", False, ["foo\0"], [["foo"]], []),
        ("\0", True, ["foo\0"], [["foo\0"]], []),
        ("\0", False, ["\0foo"], [[""]], ["foo"]),
        ("\0", True, ["\0foo"], [["\0"]], ["foo"]),
        ("\0", False, ["foo\0bar"], [["foo"]], ["bar"]),
        ("\0", True, ["foo\0bar"], [["foo\0"]], ["bar"]),
        ("\0", False, ["\0foo\0"], [["", "foo"]], []),
        ("\0", True, ["\0foo\0"], [["\0", "foo\0"]], []),
        ("\0", False, ["\0\0foo"], [["", ""]], ["foo"]),
        ("\0", True, ["\0\0foo"], [["\0", "\0"]], ["foo"]),
        ("\0", False, ["foo\0\0"], [["foo", ""]], []),
        ("\0", True, ["foo\0\0"], [["foo\0", "\0"]], []),
        (
            "\0",
            False,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc", "defgh"],
                ["i", "jklmnop"],
                ["qrs"],
                ["tuvwxy", "z"],
            ],
            [],
        ),
        (
            "\0",
            True,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc\0", "defgh\0"],
                ["i\0", "jklmnop\0"],
                ["qrs\0"],
                ["tuvwxy\0", "z\0"],
            ],
            [],
        ),
        ("\0", False, ["\0abc", "def\0ghi"], [[""], ["abcdef"]], ["ghi"]),
        ("\0", True, ["\0abc", "def\0ghi"], [["\0"], ["abcdef\0"]], ["ghi"]),
        (
            "</>",
            False,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc"], ["def"], ["ghi"], ["jkl<"]],
            ["mnop"],
        ),
        (
            "</>",
            True,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc</>"], ["def</>"], ["ghi</>"], ["jkl<</>"]],
            ["mnop"],
        ),
    ],
)
def test_terminated_splitter(
    subtests: SubTests,
    sep: str,
    retain: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    with subtests.test("str"):
        splitter = TerminatedSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.split(x) == y
        splitter.close()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = TerminatedSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.split(x.encode("utf-8")) == encode_list(y)
        bsplitter.close()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], []),
        ("\0", True, [""], [[]], []),
        ("\0", False, ["foo"], [[]], ["foo"]),
        ("\0", True, ["foo"], [[]], ["foo"]),
        ("\0", False, ["\0"], [[]], [""]),
        ("\0", True, ["\0"], [[]], ["\0"]),
        ("\0", False, ["\0\0"], [[""]], [""]),
        ("\0", True, ["\0\0"], [["\0"]], ["\0"]),
        ("\0", False, ["foo\0"], [["foo"]], [""]),
        ("\0", True, ["foo\0"], [["foo"]], ["\0"]),
        ("\0", False, ["\0foo"], [[]], ["foo"]),
        ("\0", True, ["\0foo"], [[]], ["\0foo"]),
        ("\0", False, ["foo\0bar"], [["foo"]], ["bar"]),
        ("\0", True, ["foo\0bar"], [["foo"]], ["\0bar"]),
        ("\0", False, ["\0foo\0"], [["foo"]], [""]),
        ("\0", True, ["\0foo\0"], [["\0foo"]], ["\0"]),
        ("\0", False, ["\0\0foo"], [[""]], ["foo"]),
        ("\0", True, ["\0\0foo"], [["\0"]], ["\0foo"]),
        ("\0", False, ["foo\0\0"], [["foo", ""]], [""]),
        ("\0", True, ["foo\0\0"], [["foo", "\0"]], ["\0"]),
        (
            "\0",
            False,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc", "defgh"],
                ["i", "jklmnop"],
                ["qrs"],
                ["tuvwxy", "z"],
            ],
            [""],
        ),
        (
            "\0",
            True,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc", "\0defgh"],
                ["\0i", "\0jklmnop"],
                ["\0qrs"],
                ["\0tuvwxy", "\0z"],
            ],
            ["\0"],
        ),
        ("\0", False, ["\0abc", "def\0ghi"], [[], ["abcdef"]], ["ghi"]),
        ("\0", True, ["\0abc", "def\0ghi"], [[], ["\0abcdef"]], ["\0ghi"]),
        (
            "</>",
            False,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc"], ["def"], ["ghi"], ["jkl<"]],
            ["mnop"],
        ),
        (
            "</>",
            True,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc"], ["</>def"], ["</>ghi"], ["</>jkl<"]],
            ["</>mnop"],
        ),
    ],
)
def test_preceded_splitter(
    subtests: SubTests,
    sep: str,
    retain: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    with subtests.test("str"):
        splitter = PrecededSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.split(x) == y
        splitter.close()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = PrecededSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.split(x.encode("utf-8")) == encode_list(y)
        bsplitter.close()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], [""]),
        ("\0", True, [""], [[]], [""]),
        ("\0", False, ["foo"], [[]], ["foo"]),
        ("\0", True, ["foo"], [[]], ["foo"]),
        ("\0", False, ["\0"], [[""]], [""]),
        ("\0", True, ["\0"], [["", "\0"]], [""]),
        ("\0", False, ["\0\0"], [["", ""]], [""]),
        ("\0", True, ["\0\0"], [["", "\0", "", "\0"]], [""]),
        ("\0", False, ["foo\0"], [["foo"]], [""]),
        ("\0", True, ["foo\0"], [["foo", "\0"]], [""]),
        ("\0", False, ["\0foo"], [[""]], ["foo"]),
        ("\0", True, ["\0foo"], [["", "\0"]], ["foo"]),
        ("\0", False, ["foo\0bar"], [["foo"]], ["bar"]),
        ("\0", True, ["foo\0bar"], [["foo", "\0"]], ["bar"]),
        ("\0", False, ["\0foo\0"], [["", "foo"]], [""]),
        ("\0", True, ["\0foo\0"], [["", "\0", "foo", "\0"]], [""]),
        ("\0", False, ["\0\0foo"], [["", ""]], ["foo"]),
        ("\0", True, ["\0\0foo"], [["", "\0", "", "\0"]], ["foo"]),
        ("\0", False, ["foo\0\0"], [["foo", ""]], [""]),
        ("\0", True, ["foo\0\0"], [["foo", "\0", "", "\0"]], [""]),
        (
            "\0",
            False,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc", "defgh"],
                ["i", "jklmnop"],
                ["qrs"],
                ["tuvwxy", "z"],
            ],
            [""],
        ),
        (
            "\0",
            True,
            ["012345", "abc\0defgh\0i", "\0jklmnop\0", "qrs\0tuv", "wxy\0z\0"],
            [
                [],
                ["012345abc", "\0", "defgh", "\0"],
                ["i", "\0", "jklmnop", "\0"],
                ["qrs", "\0"],
                ["tuvwxy", "\0", "z", "\0"],
            ],
            [""],
        ),
        ("\0", False, ["\0abc", "def\0ghi"], [[""], ["abcdef"]], ["ghi"]),
        ("\0", True, ["\0abc", "def\0ghi"], [["", "\0"], ["abcdef", "\0"]], ["ghi"]),
        (
            "</>",
            False,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc"], ["def"], ["ghi"], ["jkl<"]],
            ["mnop"],
        ),
        (
            "</>",
            True,
            ["abc</>def", "</>ghi</", ">jkl<", "</>mnop"],
            [["abc", "</>"], ["def", "</>"], ["ghi", "</>"], ["jkl<", "</>"]],
            ["mnop"],
        ),
    ],
)
def test_separated_splitter(
    subtests: SubTests,
    sep: str,
    retain: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    with subtests.test("str"):
        splitter = SeparatedSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.split(x) == y
        splitter.close()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = SeparatedSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.split(x.encode("utf-8")) == encode_list(y)
        bsplitter.close()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "klass", [PrecededSplitter, SeparatedSplitter, TerminatedSplitter]
)
def test_empty_sep(klass: type[ConstantSplitter]) -> None:
    with pytest.raises(ValueError) as excinfo:
        klass("")
    assert str(excinfo.value) == "Separator cannot be empty"
    with pytest.raises(ValueError) as excinfo:
        klass(b"")
    assert str(excinfo.value) == "Separator cannot be empty"


def test_feed_get() -> None:
    splitter = TerminatedSplitter("\0")
    assert not splitter.closed
    splitter.feed("foo\0bar\0baz")
    assert not splitter.closed
    assert splitter.nonempty
    assert splitter.get() == "foo"
    assert splitter.nonempty
    assert splitter.get() == "bar"
    assert not splitter.nonempty
    assert not splitter.closed  # type: ignore[unreachable]
    with pytest.raises(SplitterEmptyError) as excinfo:
        splitter.get()
    assert str(excinfo.value) == "No items available in splitter"
    assert not splitter.nonempty
    assert not splitter.closed
    splitter.close()
    assert splitter.closed
    assert splitter.nonempty
    splitter.close()
    assert splitter.closed
    assert splitter.nonempty
    assert splitter.get() == "baz"
    assert not splitter.nonempty
    with pytest.raises(SplitterClosedError) as excinfo:
        splitter.feed("extra")
    assert str(excinfo.value) == "Cannot feed data to closed splitter"
    assert splitter.closed
    assert not splitter.nonempty


def test_split_final() -> None:
    splitter = TerminatedSplitter("\0")
    assert splitter.split("\0abc\0def\0gh") == ["", "abc", "def"]
    assert splitter.split("i\0jkl\0mno\0", final=True) == ["ghi", "jkl", "mno"]
    assert not splitter.nonempty
    assert splitter.getall() == []
