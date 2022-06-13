from pathlib import Path
import re
import sys
from typing import AnyStr, IO, Iterator, List, Pattern, Union, cast
import pytest
from pytest_subtests import SubTests
from linesep import (
    read_preceded,
    read_separated,
    read_terminated,
    split_preceded,
    split_separated,
    split_terminated,
)

if sys.version_info[:2] >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

SCENARIOS = {
    "empty": {
        "text": "",
        "sep": "\n",
        "preceded": [],
        "terminated": [],
        "separated": [""],
        "preceded_retained": [],
        "terminated_retained": [],
        "separated_retained": [""],
    },
    "no_sep": {
        "text": "foo",
        "sep": "\n",
        "preceded": ["foo"],
        "terminated": ["foo"],
        "separated": ["foo"],
        "preceded_retained": ["foo"],
        "terminated_retained": ["foo"],
        "separated_retained": ["foo"],
    },
    "one_sep": {
        "text": "\n",
        "sep": "\n",
        "preceded": [""],
        "terminated": [""],
        "separated": ["", ""],
        "preceded_retained": ["\n"],
        "terminated_retained": ["\n"],
        "separated_retained": ["", "\n", ""],
    },
    "two_seps": {
        "text": "\n\n",
        "sep": "\n",
        "preceded": ["", ""],
        "terminated": ["", ""],
        "separated": ["", "", ""],
        "preceded_retained": ["\n", "\n"],
        "terminated_retained": ["\n", "\n"],
        "separated_retained": ["", "\n", "", "\n", ""],
    },
    "text_sep": {
        "text": "foo\n",
        "sep": "\n",
        "preceded": ["foo", ""],
        "preceded_retained": ["foo", "\n"],
        "separated": ["foo", ""],
        "separated_retained": ["foo", "\n", ""],
        "terminated": ["foo"],
        "terminated_retained": ["foo\n"],
    },
    "sep_text": {
        "text": "\nfoo",
        "sep": "\n",
        "preceded": ["foo"],
        "preceded_retained": ["\nfoo"],
        "separated": ["", "foo"],
        "separated_retained": ["", "\n", "foo"],
        "terminated": ["", "foo"],
        "terminated_retained": ["\n", "foo"],
    },
    "text_sep_text": {
        "text": "foo\nbar",
        "sep": "\n",
        "preceded": ["foo", "bar"],
        "preceded_retained": ["foo", "\nbar"],
        "separated": ["foo", "bar"],
        "separated_retained": ["foo", "\n", "bar"],
        "terminated": ["foo", "bar"],
        "terminated_retained": ["foo\n", "bar"],
    },
    "sep_text_sep": {
        "text": "\nfoo\n",
        "sep": "\n",
        "preceded": ["foo", ""],
        "preceded_retained": ["\nfoo", "\n"],
        "separated": ["", "foo", ""],
        "separated_retained": ["", "\n", "foo", "\n", ""],
        "terminated": ["", "foo"],
        "terminated_retained": ["\n", "foo\n"],
    },
    "sep_sep_text": {
        "text": "\n\nfoo",
        "sep": "\n",
        "preceded": ["", "foo"],
        "preceded_retained": ["\n", "\nfoo"],
        "separated": ["", "", "foo"],
        "separated_retained": ["", "\n", "", "\n", "foo"],
        "terminated": ["", "", "foo"],
        "terminated_retained": ["\n", "\n", "foo"],
    },
    "text_sep_sep": {
        "text": "foo\n\n",
        "sep": "\n",
        "preceded": ["foo", "", ""],
        "preceded_retained": ["foo", "\n", "\n"],
        "separated": ["foo", "", ""],
        "separated_retained": ["foo", "\n", "", "\n", ""],
        "terminated": ["foo", ""],
        "terminated_retained": ["foo\n", "\n"],
    },
    "regex_literal": {
        "text": "abca|bc",
        "sep": "a|b",
        "preceded": ["abc", "c"],
        "preceded_retained": ["abc", "a|bc"],
        "separated": ["abc", "c"],
        "separated_retained": ["abc", "a|b", "c"],
        "terminated": ["abc", "c"],
        "terminated_retained": ["abca|b", "c"],
    },
    "straddling_delim": {
        "text": "This test is intended to test splitting when the separator is"
        " a multicharacter delimiter that straddles the boundary"
        " between the 512-character chunks that the `read_*` functions"
        " divide their input into.  Unfortunately, I'm already bored"
        " of writing this test, and I still have 237 characters left"
        " to go.  Lorem ipsum dolor sit amet, consectetur adipisicing"
        " elit, sed do eiusmod tempor incididunt ut labore et dolore"
        " magna aliqua.  Ut enim ad minim veniam, quis nostrud"
        " exercitation ullamco Here it comes  --->  |\r\n|  <--- There"
        " should be a split right there; is there?",
        "sep": "\r\n",
        "preceded": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |",
            "|  <--- There should be a split right there; is there?",
        ],
        "preceded_retained": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |",
            "\r\n|  <--- There should be a split right there; is there?",
        ],
        "separated": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |",
            "|  <--- There should be a split right there; is there?",
        ],
        "separated_retained": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |",
            "\r\n",
            "|  <--- There should be a split right there; is there?",
        ],
        "terminated": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |",
            "|  <--- There should be a split right there; is there?",
        ],
        "terminated_retained": [
            "This test is intended to test splitting when the separator is a"
            " multicharacter delimiter that straddles the boundary between the"
            " 512-character chunks that the `read_*` functions divide their"
            " input into.  Unfortunately, I'm already bored of writing this"
            " test, and I still have 237 characters left to go.  Lorem ipsum"
            " dolor sit amet, consectetur adipisicing elit, sed do eiusmod"
            " tempor incididunt ut labore et dolore magna aliqua.  Ut enim ad"
            " minim veniam, quis nostrud exercitation ullamco Here it comes"
            "  --->  |\r\n",
            "|  <--- There should be a split right there; is there?",
        ],
    },
    "big_entry": {
        "text": "This test is intended to test splitting when a single entry"
        " is longer than the 512-character chunk size.  Lorem ipsum"
        " dolor sit amet, consectetur adipisicing elit, sed do"
        " eiusmod tempor incididunt ut labore et dolore magna aliqua."
        "  Ut enim ad minim veniam, quis nostrud exercitation ullamco"
        " laboris nisi ut aliquip ex ea commodo consequat.  Duis aute"
        " irure dolor in reprehenderit in voluptate velit esse cillum"
        " dolore eu fugiat nulla pariatur.  Excepteur sint occaecat"
        " cupidatat non proident, sunt in culpa qui officia|\r\n|"
        " deserunt mollit anim id est laborum.",
        "sep": "\r\n",
        "preceded": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|",
            "| deserunt mollit anim id est laborum.",
        ],
        "preceded_retained": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|",
            "\r\n| deserunt mollit anim id est laborum.",
        ],
        "separated": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|",
            "| deserunt mollit anim id est laborum.",
        ],
        "separated_retained": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|",
            "\r\n",
            "| deserunt mollit anim id est laborum.",
        ],
        "terminated": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|",
            "| deserunt mollit anim id est laborum.",
        ],
        "terminated_retained": [
            "This test is intended to test splitting when a single entry is"
            " longer than the 512-character chunk size.  Lorem ipsum dolor sit"
            " amet, consectetur adipisicing elit, sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua.  Ut enim ad minim"
            " veniam, quis nostrud exercitation ullamco laboris nisi ut"
            " aliquip ex ea commodo consequat.  Duis aute irure dolor in"
            " reprehenderit in voluptate velit esse cillum dolore eu fugiat"
            " nulla pariatur.  Excepteur sint occaecat cupidatat non proident,"
            " sunt in culpa qui officia|\r\n",
            "| deserunt mollit anim id est laborum.",
        ],
    },
    "empty_sep": {
        "text": "This is test text.",
        "sep": "",
        "preceded": [*"This is test text.", ""],
        "terminated": ["", *"This is test text."],
        "separated": ["", *"This is test text.", ""],
        "preceded_retained": [*"This is test text.", ""],
        "terminated_retained": ["", *"This is test text."],
        "separated_retained": [""]
        + sum([["", c] for c in "This is test text."], cast(List[str], []))
        + ["", ""],
    },
}


class Splitter(Protocol):
    def __call__(
        self,
        s: AnyStr,
        sep: Union[AnyStr, Pattern[AnyStr]],
        retain: bool = False,
    ) -> List[AnyStr]:
        ...


class Reader(Protocol):
    def __call__(
        self,
        fp: IO[AnyStr],
        sep: Union[AnyStr, Pattern[AnyStr]],
        retain: bool = False,
        chunk_size: int = 512,
    ) -> Iterator[AnyStr]:
        ...


@pytest.mark.parametrize(
    "splitter,reader,text,sep,splitvals,retain",
    [
        pytest.param(
            splitter,
            reader,
            v["text"],
            v["sep"],
            v[f"{mode}{suffix}"],
            retain,
            id=f"{k}{suffix}",
        )
        for k, v in SCENARIOS.items()
        for splitter, reader, mode in [
            (split_separated, read_separated, "separated"),
            (split_terminated, read_terminated, "terminated"),
            (split_preceded, read_preceded, "preceded"),
        ]
        for retain, suffix in [(False, ""), (True, "_retained")]
    ],
)
def test_split(
    subtests: SubTests,
    splitter: Splitter,
    reader: Reader,
    text: str,
    sep: str,
    splitvals: List[str],
    retain: bool,
    tmp_path: Path,
) -> None:
    splitbytes = [e.encode("utf-8") for e in splitvals]
    with subtests.test("split-str"):
        assert splitter(text, sep, retain=retain) == splitvals
    with subtests.test("split-bytes"):
        assert (
            splitter(text.encode("utf-8"), sep.encode("utf-8"), retain=retain)
            == splitbytes
        )
    with subtests.test("read-str"):
        p = tmp_path / "text"
        with p.open("w", encoding="utf-8", newline="") as fp:
            fp.write(text)
        with p.open(encoding="utf-8", newline="") as fp:
            assert list(reader(fp, sep, retain=retain)) == splitvals
    with subtests.test("read-bytes"):
        p = tmp_path / "bytes"
        p.write_bytes(text.encode("utf-8"))
        with p.open("rb") as fp:
            assert list(reader(fp, sep.encode("utf-8"), retain=retain)) == splitbytes


REGEX_SCENARIOS = {
    "regex01": {
        "text": "abca|bc",
        "sep": r"a|b",
        "preceded": ["", "c", "|", "c"],
        "preceded_retained": ["a", "bc", "a|", "bc"],
        "separated": ["", "", "c", "|", "c"],
        "separated_retained": ["", "a", "", "b", "c", "a", "|", "b", "c"],
        "terminated": ["", "", "c", "|", "c"],
        "terminated_retained": ["a", "b", "ca", "|b", "c"],
    },
    "regex_groups": {
        "text": "abca|bc",
        "sep": "(a)|(b)",
        "preceded": ["", "c", "|", "c"],
        "preceded_retained": ["a", "bc", "a|", "bc"],
        "separated": ["", "", "c", "|", "c"],
        "separated_retained": ["", "a", "", "b", "c", "a", "|", "b", "c"],
        "terminated": ["", "", "c", "|", "c"],
        "terminated_retained": ["a", "b", "ca", "|b", "c"],
    },
}


@pytest.mark.parametrize(
    "splitter,reader,text,sep,splitvals,retain",
    [
        pytest.param(
            splitter,
            reader,
            v["text"],
            v["sep"],
            v[f"{mode}{suffix}"],
            retain,
            id=f"{k}{suffix}",
        )
        for k, v in REGEX_SCENARIOS.items()
        for splitter, reader, mode in [
            (split_separated, read_separated, "separated"),
            (split_terminated, read_terminated, "terminated"),
            (split_preceded, read_preceded, "preceded"),
        ]
        for retain, suffix in [(False, ""), (True, "_retained")]
    ],
)
def test_split_regex(
    subtests: SubTests,
    splitter: Splitter,
    reader: Reader,
    text: str,
    sep: str,
    splitvals: List[str],
    retain: bool,
    tmp_path: Path,
) -> None:
    textrgx = re.compile(sep)
    bytesrgx = re.compile(sep.encode("utf-8"))
    splitbytes = [e.encode("utf-8") for e in splitvals]
    with subtests.test("split-str"):
        assert splitter(text, textrgx, retain=retain) == splitvals
    with subtests.test("split-bytes"):
        assert splitter(text.encode("utf-8"), bytesrgx, retain=retain) == splitbytes
    with subtests.test("read-str"):
        p = tmp_path / "text"
        with p.open("w", encoding="utf-8", newline="") as fp:
            fp.write(text)
        with p.open(encoding="utf-8", newline="") as fp:
            with pytest.deprecated_call():
                assert list(reader(fp, textrgx, retain=retain)) == splitvals
    with subtests.test("read-bytes"):
        p = tmp_path / "bytes"
        p.write_bytes(text.encode("utf-8"))
        with p.open("rb") as fp:
            with pytest.deprecated_call():
                assert list(reader(fp, bytesrgx, retain=retain)) == splitbytes
