from __future__ import annotations
from collections.abc import AsyncIterator
import pytest
from pytest_subtests import SubTests
from linesep import (
    ParagraphSplitter,
    PrecededSplitter,
    SeparatedSplitter,
    SplitterClosedError,
    SplitterEmptyError,
    TerminatedSplitter,
    UnicodeNewlineSplitter,
    UniversalNewlineSplitter,
    get_newline_splitter,
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


@pytest.mark.parametrize(
    "retain,translate,inputs,outputs,endput",
    [
        (False, False, [], [[]], []),
        (True, False, [], [[]], []),
        (False, False, [""], [[]], []),
        (True, False, [""], [[]], []),
        (False, False, ["foo"], [[]], ["foo"]),
        (False, False, ["foo\n"], [["foo"]], []),
        (False, False, ["foo\r\n"], [["foo"]], []),
        (False, False, ["foo\r"], [[]], ["foo"]),
        (False, False, ["foo\v"], [[]], ["foo\v"]),
        (False, False, ["foo\f"], [[]], ["foo\f"]),
        (False, False, ["foo\x1c"], [[]], ["foo\x1c"]),
        (False, False, ["foo\x1d"], [[]], ["foo\x1d"]),
        (False, False, ["foo\x1e"], [[]], ["foo\x1e"]),
        (False, False, ["foo\x85"], [[]], ["foo\x85"]),
        (False, False, ["foo\u2028"], [[]], ["foo\u2028"]),
        (False, False, ["foo\u2029"], [[]], ["foo\u2029"]),
        (False, False, ["foo\r", "bar"], [[], ["foo"]], ["bar"]),
        (False, False, ["foo\r", "\nbar"], [[], ["foo"]], ["bar"]),
        (False, False, ["foo\rbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\nbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\n\nbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\n\r\nbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\n\rbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\vbar"], [["foo"]], ["\vbar"]),
        (False, False, ["foo\v\fbar"], [[]], ["foo\v\fbar"]),
        (False, False, ["foo\f\x1cbar"], [[]], ["foo\f\x1cbar"]),
        (False, False, ["foo\x1c\x1dbar"], [[]], ["foo\x1c\x1dbar"]),
        (False, False, ["foo\x1d\x1ebar"], [[]], ["foo\x1d\x1ebar"]),
        (False, False, ["foo\x1e\x85bar"], [[]], ["foo\x1e\x85bar"]),
        (False, False, ["foo\x85\u2028bar"], [[]], ["foo\x85\u2028bar"]),
        (False, False, ["foo\u2028\u2029bar"], [[]], ["foo\u2028\u2029bar"]),
        (False, False, ["foo\u2029\nbar"], [["foo\u2029"]], ["bar"]),
        (True, False, ["foo\n"], [["foo\n"]], []),
        (True, False, ["foo\r\n"], [["foo\r\n"]], []),
        (True, False, ["foo\r"], [[]], ["foo\r"]),
        (True, False, ["foo\r", "bar"], [[], ["foo\r"]], ["bar"]),
        (True, False, ["foo\r", "\nbar"], [[], ["foo\r\n"]], ["bar"]),
        (True, False, ["foo\rbar"], [["foo\r"]], ["bar"]),
        (True, False, ["foo\r\nbar"], [["foo\r\n"]], ["bar"]),
        (True, False, ["foo\r\n\nbar"], [["foo\r\n", "\n"]], ["bar"]),
        (True, False, ["foo\r\n\r\nbar"], [["foo\r\n", "\r\n"]], ["bar"]),
        (True, False, ["foo\r\n\rbar"], [["foo\r\n", "\r"]], ["bar"]),
        (True, True, ["foo\n"], [["foo\n"]], []),
        (True, True, ["foo\r\n"], [["foo\n"]], []),
        (True, True, ["foo\r"], [[]], ["foo\n"]),
        (True, True, ["foo\r", "bar"], [[], ["foo\n"]], ["bar"]),
        (True, True, ["foo\r", "\nbar"], [[], ["foo\n"]], ["bar"]),
        (True, True, ["foo\rbar"], [["foo\n"]], ["bar"]),
        (True, True, ["foo\r\nbar"], [["foo\n"]], ["bar"]),
        (True, True, ["foo\r\n\nbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\r\n\r\nbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\r\n\rbar"], [["foo\n", "\n"]], ["bar"]),
    ],
)
def test_universal_newline_splitter(
    subtests: SubTests,
    retain: bool,
    translate: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    with subtests.test("str"):
        splitter: UniversalNewlineSplitter[str] = UniversalNewlineSplitter(
            retain=retain, translate=translate
        )
        for x, y in zip(inputs, outputs):
            assert splitter.split(x) == y
        splitter.close()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter: UniversalNewlineSplitter[bytes] = UniversalNewlineSplitter(
            retain=retain, translate=translate
        )
        for x, y in zip(inputs, outputs):
            assert bsplitter.split(x.encode("utf-8")) == encode_list(y)
        bsplitter.close()
        assert bsplitter.getall() == encode_list(endput)


@pytest.mark.parametrize(
    "newline,retain,outputs",
    [
        (None, False, ["fee", "fie", "foe", "foo"]),
        (None, True, ["fee\n", "fie\n", "foe\n", "foo\n"]),
        ("", True, ["fee\n", "fie\r", "foe\r\n", "foo\n"]),
        ("\n", False, ["fee", "fie\rfoe\r", "foo"]),
        ("\n", True, ["fee\n", "fie\rfoe\r\n", "foo\n"]),
        ("\r", False, ["fee\nfie", "foe", "\nfoo\n"]),
        ("\r", True, ["fee\nfie\r", "foe\r", "\nfoo\n"]),
        ("\r\n", False, ["fee\nfie\rfoe", "foo\n"]),
        ("\r\n", True, ["fee\nfie\rfoe\r\n", "foo\n"]),
    ],
)
def test_get_newline_splitter(
    newline: str | None, retain: bool, outputs: list[str]
) -> None:
    splitter = get_newline_splitter(newline, retain=retain)
    assert splitter.split("fee\nfie\rfoe\r\nfoo\n", final=True) == outputs


@pytest.mark.parametrize("newline", ["\0", "\v", "\f", "\x85", "\u2028"])
def test_get_newline_separator_bad_newline(newline: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        get_newline_splitter(newline)
    assert str(excinfo.value) == f"Invalid 'newline' value: {newline!r}"


def test_reset() -> None:
    splitter = TerminatedSplitter("\0", retain=True)
    assert splitter.split("foo\0bar") == ["foo\0"]
    assert splitter.split("baz\0quux\0", final=True) == ["barbaz\0", "quux\0"]
    splitter.reset()
    assert splitter.split("baz\0quux\0", final=True) == ["baz\0", "quux\0"]


def test_getstate_setstate() -> None:
    splitter = TerminatedSplitter("\0", retain=True)
    assert splitter.split("foo\0bar") == ["foo\0"]
    st = splitter.getstate()
    assert splitter.split("baz\0quux\0", final=True) == ["barbaz\0", "quux\0"]
    splitter.setstate(st)
    assert splitter.split("\0baz\0quux\0", final=True) == ["bar\0", "baz\0", "quux\0"]


def test_getstate_setstate_closed() -> None:
    splitter = TerminatedSplitter("\0", retain=True)
    splitter.close()
    st = splitter.getstate()
    splitter.reset()
    assert splitter.split("foo\0bar") == ["foo\0"]
    splitter.setstate(st)
    with pytest.raises(SplitterClosedError):
        splitter.feed("baz\0")


def test_getstate_setstate_first_preceded() -> None:
    splitter = PrecededSplitter("\0", retain=True)
    assert splitter.split("\0") == []
    st = splitter.getstate()
    assert splitter.split("foo\0bar", final=True) == ["\0foo", "\0bar"]
    splitter.setstate(st)
    assert splitter.split("\0quux", final=True) == ["\0", "\0quux"]


def test_reset_first_preceded() -> None:
    splitter = PrecededSplitter("\0", retain=True)
    assert splitter.split("\0") == []
    splitter.reset()
    assert splitter.split("\0bar", final=True) == ["\0bar"]


def test_getstate_setstate_get_some() -> None:
    splitter = SeparatedSplitter("\0")
    splitter.feed("foo\0bar\0baz")
    assert splitter.get() == "foo"
    st = splitter.getstate()
    splitter.feed("quux\0glarch")
    splitter.close()
    assert splitter.getall() == ["bar", "bazquux", "glarch"]
    assert splitter.getall() == []
    splitter.setstate(st)
    splitter.feed("\0gnusto\0cleesh")
    splitter.close()
    assert splitter.getall() == ["bar", "baz", "gnusto", "cleesh"]
    assert splitter.getall() == []


def test_itersplit() -> None:
    splitter = TerminatedSplitter("\0")
    it = splitter.itersplit(["foo\0bar", "baz\0quux\0", "\0gnusto\0cleesh"])
    assert next(it) == "foo"
    assert next(it) == "barbaz"
    assert next(it) == "quux"
    assert next(it) == ""
    assert next(it) == "gnusto"
    assert next(it) == "cleesh"
    with pytest.raises(StopIteration):
        next(it)


@pytest.mark.asyncio
async def test_aitersplit() -> None:
    async def ayielder() -> AsyncIterator[str]:
        yield "foo\0bar"
        yield "baz\0quux\0"
        yield "\0gnusto\0cleesh"

    splitter = TerminatedSplitter("\0")
    ait = splitter.aitersplit(ayielder())
    assert await anext(ait) == "foo"
    assert await anext(ait) == "barbaz"
    assert await anext(ait) == "quux"
    assert await anext(ait) == ""
    assert await anext(ait) == "gnusto"
    assert await anext(ait) == "cleesh"
    with pytest.raises(StopAsyncIteration):
        await anext(ait)


@pytest.mark.parametrize(
    "retain,translate,inputs,outputs,endput",
    [
        (False, False, [], [[]], []),
        (True, False, [], [[]], []),
        (False, False, [""], [[]], []),
        (True, False, [""], [[]], []),
        (False, False, ["foo"], [[]], ["foo"]),
        (False, False, ["foo\n"], [["foo"]], []),
        (False, False, ["foo\r\n"], [["foo"]], []),
        (False, False, ["foo\r"], [[]], ["foo"]),
        (False, False, ["foo\v"], [["foo"]], []),
        (False, False, ["foo\f"], [["foo"]], []),
        (False, False, ["foo\x1c"], [["foo"]], []),
        (False, False, ["foo\x1d"], [["foo"]], []),
        (False, False, ["foo\x1e"], [["foo"]], []),
        (False, False, ["foo\x85"], [["foo"]], []),
        (False, False, ["foo\u2028"], [["foo"]], []),
        (False, False, ["foo\u2029"], [["foo"]], []),
        (False, False, ["foo\r", "bar"], [[], ["foo"]], ["bar"]),
        (False, False, ["foo\r", "\nbar"], [[], ["foo"]], ["bar"]),
        (False, False, ["foo\rbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\nbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\n\nbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\n\r\nbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\n\rbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\r\vbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\v\fbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\f\x1cbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\x1c\x1dbar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\x1d\x1ebar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\x1e\x85bar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\x85\u2028bar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\u2028\u2029bar"], [["foo", ""]], ["bar"]),
        (False, False, ["foo\u2029\nbar"], [["foo", ""]], ["bar"]),
        (True, False, ["foo\n"], [["foo\n"]], []),
        (True, False, ["foo\r\n"], [["foo\r\n"]], []),
        (True, False, ["foo\r"], [[]], ["foo\r"]),
        (True, False, ["foo\v"], [["foo\v"]], []),
        (True, False, ["foo\f"], [["foo\f"]], []),
        (True, False, ["foo\x1c"], [["foo\x1c"]], []),
        (True, False, ["foo\x1d"], [["foo\x1d"]], []),
        (True, False, ["foo\x1e"], [["foo\x1e"]], []),
        (True, False, ["foo\x85"], [["foo\x85"]], []),
        (True, False, ["foo\u2028"], [["foo\u2028"]], []),
        (True, False, ["foo\u2029"], [["foo\u2029"]], []),
        (True, False, ["foo\r", "bar"], [[], ["foo\r"]], ["bar"]),
        (True, False, ["foo\r", "\nbar"], [[], ["foo\r\n"]], ["bar"]),
        (True, False, ["foo\rbar"], [["foo\r"]], ["bar"]),
        (True, False, ["foo\r\nbar"], [["foo\r\n"]], ["bar"]),
        (True, False, ["foo\r\n\nbar"], [["foo\r\n", "\n"]], ["bar"]),
        (True, False, ["foo\r\n\r\nbar"], [["foo\r\n", "\r\n"]], ["bar"]),
        (True, False, ["foo\r\n\rbar"], [["foo\r\n", "\r"]], ["bar"]),
        (True, False, ["foo\r\vbar"], [["foo\r", "\v"]], ["bar"]),
        (True, False, ["foo\v\fbar"], [["foo\v", "\f"]], ["bar"]),
        (True, False, ["foo\f\x1cbar"], [["foo\f", "\x1c"]], ["bar"]),
        (True, False, ["foo\x1c\x1dbar"], [["foo\x1c", "\x1d"]], ["bar"]),
        (True, False, ["foo\x1d\x1ebar"], [["foo\x1d", "\x1e"]], ["bar"]),
        (True, False, ["foo\x1e\x85bar"], [["foo\x1e", "\x85"]], ["bar"]),
        (True, False, ["foo\x85\u2028bar"], [["foo\x85", "\u2028"]], ["bar"]),
        (True, False, ["foo\u2028\u2029bar"], [["foo\u2028", "\u2029"]], ["bar"]),
        (True, False, ["foo\u2029\nbar"], [["foo\u2029", "\n"]], ["bar"]),
        (True, True, ["foo\n"], [["foo\n"]], []),
        (True, True, ["foo\r\n"], [["foo\n"]], []),
        (True, True, ["foo\r"], [[]], ["foo\n"]),
        (True, True, ["foo\v"], [["foo\n"]], []),
        (True, True, ["foo\f"], [["foo\n"]], []),
        (True, True, ["foo\x1c"], [["foo\n"]], []),
        (True, True, ["foo\x1d"], [["foo\n"]], []),
        (True, True, ["foo\x1e"], [["foo\n"]], []),
        (True, True, ["foo\x85"], [["foo\n"]], []),
        (True, True, ["foo\u2028"], [["foo\n"]], []),
        (True, True, ["foo\u2029"], [["foo\n"]], []),
        (True, True, ["foo\r", "bar"], [[], ["foo\n"]], ["bar"]),
        (True, True, ["foo\r", "\nbar"], [[], ["foo\n"]], ["bar"]),
        (True, True, ["foo\rbar"], [["foo\n"]], ["bar"]),
        (True, True, ["foo\r\nbar"], [["foo\n"]], ["bar"]),
        (True, True, ["foo\r\n\nbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\r\n\r\nbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\r\n\rbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\r\vbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\v\fbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\f\x1cbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\x1c\x1dbar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\x1d\x1ebar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\x1e\x85bar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\x85\u2028bar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\u2028\u2029bar"], [["foo\n", "\n"]], ["bar"]),
        (True, True, ["foo\u2029\nbar"], [["foo\n", "\n"]], ["bar"]),
    ],
)
def test_unicode_newline_splitter(
    retain: bool,
    translate: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    splitter = UnicodeNewlineSplitter(retain=retain, translate=translate)
    for x, y in zip(inputs, outputs):
        assert splitter.split(x) == y
    splitter.close()
    assert splitter.getall() == endput


@pytest.mark.parametrize(
    "retain,translate,inputs,outputs,endput",
    [
        (False, False, [], [[]], []),
        (True, False, [], [[]], []),
        (False, False, [""], [[]], []),
        (True, False, [""], [[]], []),
        (False, False, ["foo\n"], [[]], ["foo"]),
        (False, False, ["foo\r"], [[]], ["foo"]),
        (False, False, ["foo\r\n"], [[]], ["foo"]),
        (False, False, ["foo\nbar"], [[]], ["foo\nbar"]),
        (False, False, ["foo\r\nbar"], [[]], ["foo\r\nbar"]),
        (False, False, ["foo\rbar"], [[]], ["foo\rbar"]),
        (False, False, ["foo\v"], [[]], ["foo\v"]),
        (False, False, ["foo\f"], [[]], ["foo\f"]),
        (False, False, ["foo\x1c"], [[]], ["foo\x1c"]),
        (False, False, ["foo\x1d"], [[]], ["foo\x1d"]),
        (False, False, ["foo\x1e"], [[]], ["foo\x1e"]),
        (False, False, ["foo\x85"], [[]], ["foo\x85"]),
        (False, False, ["foo\u2028"], [[]], ["foo\u2028"]),
        (False, False, ["foo\u2029"], [[]], ["foo\u2029"]),
        (False, False, ["foo\n\n"], [["foo"]], []),
        (False, False, ["foo\n\r"], [["foo"]], []),
        (False, False, ["foo\n\r", "\n"], [["foo"], []], []),
        (False, False, ["foo\n\nbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\n\r\nbar"], [["foo"]], ["bar"]),
        (False, False, ["foo\r\rbar"], [["foo"]], ["bar"]),
        (False, False, ["\nfoo"], [[""]], ["foo"]),
        (False, False, ["\r\nfoo"], [[""]], ["foo"]),
        (False, False, ["\rfoo"], [[""]], ["foo"]),
        (
            False,
            False,
            ["foo\nbar\n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar", "baz"]],
            ["quux"],
        ),
        (
            False,
            False,
            ["foo\nbar\n\n", "\nbaz\n\n\nquux"],
            [["foo\nbar"], ["baz"]],
            ["quux"],
        ),
        (
            False,
            False,
            ["foo\nbar\n \n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n ", "baz"]],
            ["quux"],
        ),
        (
            False,
            False,
            ["foo\n", "bar\n", "baz\n", "\n", "\n", "\n", "quux\n", "\n"],
            [[], [], [], ["foo\nbar\nbaz"], [], [], [], ["quux"]],
            [],
        ),
        (False, False, ["foo\r\vbar"], [[]], ["foo\r\vbar"]),
        (False, False, ["foo\v\fbar"], [[]], ["foo\v\fbar"]),
        (False, False, ["foo\f\x1cbar"], [[]], ["foo\f\x1cbar"]),
        (False, False, ["foo\x1c\x1dbar"], [[]], ["foo\x1c\x1dbar"]),
        (False, False, ["foo\x1d\x1ebar"], [[]], ["foo\x1d\x1ebar"]),
        (False, False, ["foo\x1e\x85bar"], [[]], ["foo\x1e\x85bar"]),
        (False, False, ["foo\x85\u2028bar"], [[]], ["foo\x85\u2028bar"]),
        (False, False, ["foo\u2028\u2029bar"], [[]], ["foo\u2028\u2029bar"]),
        (False, False, ["foo\u2029\nbar"], [[]], ["foo\u2029\nbar"]),
        (True, False, ["foo\n"], [[]], ["foo\n"]),
        (True, False, ["foo\r"], [[]], ["foo\r"]),
        (True, False, ["foo\r\n"], [[]], ["foo\r\n"]),
        (True, False, ["foo\nbar"], [[]], ["foo\nbar"]),
        (True, False, ["foo\r\nbar"], [[]], ["foo\r\nbar"]),
        (True, False, ["foo\rbar"], [[]], ["foo\rbar"]),
        (True, False, ["foo\n\n"], [[]], ["foo\n\n"]),
        (True, False, ["foo\n\r"], [[]], ["foo\n\r"]),
        (True, False, ["foo\n\r", "\n"], [[], []], ["foo\n\r\n"]),
        (True, False, ["foo\n\nbar"], [["foo\n\n"]], ["bar"]),
        (True, False, ["foo\r\n\r\nbar"], [["foo\r\n\r\n"]], ["bar"]),
        (True, False, ["foo\r\rbar"], [["foo\r\r"]], ["bar"]),
        (True, False, ["\nfoo"], [["\n"]], ["foo"]),
        (True, False, ["\r\nfoo"], [["\r\n"]], ["foo"]),
        (True, False, ["\rfoo"], [["\r"]], ["foo"]),
        (
            True,
            False,
            ["foo\nbar\n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            False,
            ["foo\nbar\n\n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n\n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            False,
            ["foo\nbar\n \n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n \n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            False,
            ["foo\n", "bar\n", "baz\n", "\n", "\n", "\n", "quux\n", "\n"],
            [[], [], [], [], [], [], ["foo\nbar\nbaz\n\n\n\n"], []],
            ["quux\n\n"],
        ),
        (True, True, ["foo\n"], [[]], ["foo\n"]),
        (True, True, ["foo\r"], [[]], ["foo\n"]),
        (True, True, ["foo\r\n"], [[]], ["foo\n"]),
        (True, True, ["foo\nbar"], [[]], ["foo\nbar"]),
        (True, True, ["foo\r\nbar"], [[]], ["foo\nbar"]),
        (True, True, ["foo\rbar"], [[]], ["foo\nbar"]),
        (True, True, ["foo\n\n"], [[]], ["foo\n\n"]),
        (True, True, ["foo\n\r"], [[]], ["foo\n\n"]),
        (True, True, ["foo\n\r", "\n"], [[], []], ["foo\n\n"]),
        (True, True, ["foo\n\nbar"], [["foo\n\n"]], ["bar"]),
        (True, True, ["foo\r\n\r\nbar"], [["foo\n\n"]], ["bar"]),
        (True, True, ["foo\r\rbar"], [["foo\n\n"]], ["bar"]),
        (True, True, ["\nfoo"], [["\n"]], ["foo"]),
        (True, True, ["\r\nfoo"], [["\n"]], ["foo"]),
        (True, True, ["\rfoo"], [["\n"]], ["foo"]),
        (
            True,
            True,
            ["foo\nbar\n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            True,
            ["foo\nbar\n\n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n\n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            True,
            ["foo\nbar\n \n", "\nbaz\n\n\nquux"],
            [[], ["foo\nbar\n \n\n", "baz\n\n\n"]],
            ["quux"],
        ),
        (
            True,
            True,
            ["foo\n", "bar\n", "baz\n", "\n", "\n", "\n", "quux\n", "\n"],
            [[], [], [], [], [], [], ["foo\nbar\nbaz\n\n\n\n"], []],
            ["quux\n\n"],
        ),
    ],
)
def test_paragraph_splitter(
    subtests: SubTests,
    retain: bool,
    translate: bool,
    inputs: list[str],
    outputs: list[list[str]],
    endput: list[str],
) -> None:
    with subtests.test("str"):
        splitter: ParagraphSplitter[str] = ParagraphSplitter(
            retain=retain, translate=translate
        )
        for x, y in zip(inputs, outputs):
            assert splitter.split(x) == y
        splitter.close()
        assert splitter.getall() == endput
    with subtests.test("bytes"):
        bsplitter: ParagraphSplitter[bytes] = ParagraphSplitter(
            retain=retain, translate=translate
        )
        for x, y in zip(inputs, outputs):
            assert bsplitter.split(x.encode("utf-8")) == encode_list(y)
        bsplitter.close()
        assert bsplitter.getall() == encode_list(endput)
