from typing import List, Type
import pytest
from pytest_subtests import SubTests
from linesep import (
    EmptySplitterError,
    PrecededSplitter,
    SeparatedSplitter,
    SplitterEndedError,
    TerminatedSplitter,
)
from linesep.splitters import ConstantSplitter


def encode_list(txt: List[str]) -> List[bytes]:
    return [s.encode("utf-8") for s in txt]


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
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
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], []),
        ("\0", True, [""], [[]], []),
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
    inputs: List[str],
    outputs: List[List[str]],
    endput: List[str],
) -> None:
    with subtests.test("str"):
        splitter = TerminatedSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.process(x) == y
        splitter.end()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = TerminatedSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.process(x.encode("utf-8")) == encode_list(y)
        bsplitter.end()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
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
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], []),
        ("\0", True, [""], [[]], []),
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
    inputs: List[str],
    outputs: List[List[str]],
    endput: List[str],
) -> None:
    with subtests.test("str"):
        splitter = PrecededSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.process(x) == y
        splitter.end()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = PrecededSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.process(x.encode("utf-8")) == encode_list(y)
        bsplitter.end()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "sep,retain,inputs,outputs,endput",
    [
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
        ("\0", False, [], [[]], []),
        ("\0", True, [], [[]], []),
        ("\0", False, [""], [[]], [""]),
        ("\0", True, [""], [[]], [""]),
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
    inputs: List[str],
    outputs: List[List[str]],
    endput: List[str],
) -> None:
    with subtests.test("str"):
        splitter = SeparatedSplitter(sep, retain=retain)
        for x, y in zip(inputs, outputs):
            assert splitter.process(x) == y
        splitter.end()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter = SeparatedSplitter(sep.encode("utf-8"), retain=retain)
        for x, y in zip(inputs, outputs):
            assert bsplitter.process(x.encode("utf-8")) == encode_list(y)
        bsplitter.end()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "klass", [PrecededSplitter, SeparatedSplitter, TerminatedSplitter]
)
def test_empty_sep(klass: Type[ConstantSplitter]) -> None:
    with pytest.raises(ValueError) as excinfo:
        klass("")
    assert str(excinfo.value) == "Separator cannot be empty"
    with pytest.raises(ValueError) as excinfo:
        klass(b"")
    assert str(excinfo.value) == "Separator cannot be empty"


def test_feed_get() -> None:
    splitter = TerminatedSplitter("\0")
    assert not splitter.ended
    splitter.feed("foo\0bar\0baz")
    assert not splitter.ended
    assert splitter.has_next
    assert splitter.get() == "foo"
    assert splitter.has_next
    assert splitter.get() == "bar"
    assert not splitter.has_next
    assert not splitter.ended  # type: ignore[unreachable]
    with pytest.raises(EmptySplitterError) as excinfo:
        splitter.get()
    assert str(excinfo.value) == "No items available in splitter"
    assert not splitter.has_next
    assert not splitter.ended
    splitter.end()
    assert splitter.ended
    assert splitter.has_next
    splitter.end()
    assert splitter.ended
    assert splitter.has_next
    assert splitter.get() == "baz"
    assert not splitter.has_next
    with pytest.raises(SplitterEndedError) as excinfo:
        splitter.feed("extra")
    assert str(excinfo.value) == "Cannot feed data to splitter after calling end()"
    assert splitter.ended
    assert not splitter.has_next


def test_process_final() -> None:
    splitter = TerminatedSplitter("\0")
    assert splitter.process("\0abc\0def\0gh") == ["", "abc", "def"]
    assert splitter.process("i\0jkl\0mno\0", final=True) == ["ghi", "jkl", "mno"]
    assert not splitter.has_next
    assert splitter.getall() == []
