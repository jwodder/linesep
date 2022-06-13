from io import StringIO
from typing import List
import pytest
from linesep import ascii_splitlines, read_paragraphs, split_paragraphs


@pytest.mark.parametrize(
    "s,lines",
    [
        ("", []),
        ("foobar", ["foobar"]),
        ("foo\n", ["foo"]),
        ("foo\r", ["foo"]),
        ("foo\r\n", ["foo"]),
        ("foo\n\r", ["foo", ""]),
        ("foo\nbar", ["foo", "bar"]),
        ("foo\rbar", ["foo", "bar"]),
        ("foo\r\nbar", ["foo", "bar"]),
        ("foo\n\rbar", ["foo", "", "bar"]),
        ("foo\n\nbar", ["foo", "", "bar"]),
        ("foo\n\nbar\n", ["foo", "", "bar"]),
        (
            "Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029"
            "characters?",
            [
                "Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029"
                "characters?"
            ],
        ),
    ],
)
def test_ascii_splitlines(s: str, lines: List[str]) -> None:
    assert ascii_splitlines(s) == lines


@pytest.mark.parametrize(
    "s,lines",
    [
        ("", []),
        ("foobar", ["foobar"]),
        ("foo\n", ["foo\n"]),
        ("foo\r", ["foo\r"]),
        ("foo\r\n", ["foo\r\n"]),
        ("foo\n\r", ["foo\n", "\r"]),
        ("foo\nbar", ["foo\n", "bar"]),
        ("foo\rbar", ["foo\r", "bar"]),
        ("foo\r\nbar", ["foo\r\n", "bar"]),
        ("foo\n\rbar", ["foo\n", "\r", "bar"]),
        ("foo\n\nbar", ["foo\n", "\n", "bar"]),
        ("foo\n\nbar\n", ["foo\n", "\n", "bar\n"]),
        (
            "Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029"
            "characters?",
            [
                "Why\vare\fthere\x1Cso\x1Ddang\x1Emany\x85line\u2028separator\u2029"
                "characters?"
            ],
        ),
    ],
)
def test_ascii_splitlines_keepends(s: str, lines: List[str]) -> None:
    assert ascii_splitlines(s, keepends=True) == lines


TEXT_PARAGRAPHS = [
    ("", []),
    ("\n", ["\n"]),
    ("\n\n", ["\n\n"]),
    ("\n\n\n", ["\n\n\n"]),
    ("This is test text.", ["This is test text."]),
    ("This is test text.\n", ["This is test text.\n"]),
    ("This is test text.\n\n", ["This is test text.\n\n"]),
    ("This is test text.\n\n\n", ["This is test text.\n\n\n"]),
    (
        "This is test text.\nThis is a textual test.",
        ["This is test text.\nThis is a textual test."],
    ),
    (
        "This is test text.\r\nThis is a textual test.",
        ["This is test text.\r\nThis is a textual test."],
    ),
    (
        "This is test text.\n\nThis is a textual test.",
        ["This is test text.\n\n", "This is a textual test."],
    ),
    (
        "This is test text.\n\n\nThis is a textual test.",
        ["This is test text.\n\n\n", "This is a textual test."],
    ),
    ("\nThis is test text.", ["\n", "This is test text."]),
    ("\n\nThis is test text.", ["\n\n", "This is test text."]),
    ("\n\n\nThis is test text.", ["\n\n\n", "This is test text."]),
    (
        "This is test text.\r\n\r\nThis is a textual test.\r\r"
        "This is the text that tests.\n\n\n",
        [
            "This is test text.\r\n\r\n",
            "This is a textual test.\r\r",
            "This is the text that tests.\n\n\n",
        ],
    ),
    (
        "This is test text.\r\nThis is a textual test.\r"
        "This is the text that tests.\n\n"
        "Boy, that Lorem Ipsum guy really had the right\nidea.\n\n",
        [
            "This is test text.\r\nThis is a textual test.\r"
            "This is the text that tests.\n\n",
            "Boy, that Lorem Ipsum guy really had the right\nidea.\n\n",
        ],
    ),
    (
        "This is test text.\n\n \nThis is a textual test.\n",
        ["This is test text.\n\n", " \nThis is a textual test.\n"],
    ),
    (
        "This is test text.\n\n \n\nThis is a textual test.\n",
        ["This is test text.\n\n", " \n\n", "This is a textual test.\n"],
    ),
    (
        "This is test text.\n \n\nThis is a textual test.\n",
        ["This is test text.\n \n\n", "This is a textual test.\n"],
    ),
]


@pytest.mark.parametrize("txt,paras", TEXT_PARAGRAPHS)
def test_read_paragraphs(txt: str, paras: List[str]) -> None:
    assert list(read_paragraphs(StringIO(txt, newline=""))) == paras


@pytest.mark.parametrize("txt,paras", TEXT_PARAGRAPHS)
def test_split_paragraphs(txt: str, paras: List[str]) -> None:
    assert split_paragraphs(txt) == paras
