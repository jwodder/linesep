from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator
from dataclasses import dataclass
import re
from typing import AnyStr, Generic, Optional


class Splitter(ABC, Generic[AnyStr]):
    def __init__(self) -> None:
        self._items: deque[AnyStr] = deque()
        self._buff: Optional[AnyStr] = None
        self._hold: Optional[AnyStr] = None
        self._closed: bool = False
        self._first: bool = True

    @abstractmethod
    def _find_separator(self, data: AnyStr) -> Optional[tuple[int, int]]:
        ...

    @abstractmethod
    def _append_item(
        self, item: AnyStr, first: bool = False, last: bool = False
    ) -> None:
        ...

    @abstractmethod
    def _append_separator(self, item: AnyStr) -> None:
        ...

    def _append(self, item: AnyStr) -> None:
        self._items.append(item)

    def feed(self, data: AnyStr) -> None:
        if self._closed:
            raise SplitterClosedError("Cannot feed data to closed splitter")
        if self._buff is None:
            self._buff = data
        else:
            self._buff += data
        self._split()

    def close(self) -> None:
        self._closed = True
        if self._buff is not None:
            self._split()

    def _split(self) -> None:
        while self._buff:
            span = self._find_separator(self._buff)
            if span is None:
                break
            start, end = span
            self._append_item(self._buff[:start], first=self._first)
            self._first = False
            self._append_separator(self._buff[start:end])
            self._buff = self._buff[end:]
        if self._closed and self._buff is not None:
            self._append_item(self._buff, first=self._first, last=True)
            self._buff = None

    def get(self) -> AnyStr:
        try:
            return self._items.popleft()
        except IndexError:
            raise SplitterEmptyError("No items available in splitter")

    def getall(self) -> list[AnyStr]:
        items = list(self._items)
        self._items.clear()
        return items

    def split(self, data: AnyStr, final: bool = False) -> list[AnyStr]:
        self.feed(data)
        if final:
            self.close()
        return self.getall()

    @property
    def nonempty(self) -> bool:
        return bool(self._items)

    @property
    def closed(self) -> bool:
        return self._closed

    def reset(self) -> None:
        self._items.clear()
        self._buff = None
        self._hold = None
        self._closed = False
        self._first = True

    def getstate(self) -> SplitterState[AnyStr]:
        return SplitterState(
            items=list(self._items),
            buff=self._buff,
            hold=self._hold,
            closed=self._closed,
            first=self._first,
        )

    def setstate(self, state: SplitterState[AnyStr]) -> None:
        self._items.clear()
        self._items.extend(state.items)
        self._buff = state.buff
        self._hold = state.hold
        self._closed = state.closed
        self._first = state.first

    def itersplit(self, iterable: Iterable[AnyStr]) -> Iterator[AnyStr]:
        st = self.getstate()
        self.reset()
        try:
            for s in iterable:
                yield from self.split(s)
            self.close()
            yield from self.getall()
        finally:
            self.setstate(st)

    async def aitersplit(
        self, aiterable: AsyncIterable[AnyStr]
    ) -> AsyncIterator[AnyStr]:
        st = self.getstate()
        self.reset()
        try:
            async for s in aiterable:
                for t in self.split(s):
                    yield t
            self.close()
            for t in self.getall():
                yield t
        finally:
            self.setstate(st)


class ConstantSplitter(Splitter[AnyStr]):
    def __init__(self, separator: AnyStr, retain: bool = False) -> None:
        if not separator:
            raise ValueError("Separator cannot be empty")
        super().__init__()
        self._separator: AnyStr = separator
        self._retain: bool = retain

    def _find_separator(self, data: AnyStr) -> Optional[tuple[int, int]]:
        try:
            i = data.index(self._separator)
        except ValueError:
            return None
        else:
            return (i, i + len(self._separator))


class TerminatedSplitter(ConstantSplitter[AnyStr]):
    def _append_item(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if not last or item:
            if self._retain and not last:
                assert self._hold is None
                self._hold = item
            else:
                self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            assert self._hold is not None
            self._append(self._hold + item)
            self._hold = None


class SeparatedSplitter(ConstantSplitter[AnyStr]):
    def _append_item(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            self._append(item)


class PrecededSplitter(ConstantSplitter[AnyStr]):
    def _append_item(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if first:
            if item:
                self._append(item)
        elif self._retain:
            assert self._hold is not None
            self._append(self._hold + item)
            self._hold = None
        else:
            self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            assert self._hold is None
            self._hold = item


class UniversalNewlineSplitter(Splitter[AnyStr]):
    def __init__(self, retain: bool = False, translate: bool = True) -> None:
        super().__init__()
        self._retain = retain
        self._translate = translate
        self._strs: Optional[NewlineStrs[AnyStr]] = None

    def _find_separator(self, data: AnyStr) -> Optional[tuple[int, int]]:
        if self._strs is None:
            if isinstance(data, str):
                self._strs = NewlineStrs(
                    regex=re.compile(r"\r\n?|\n"), CR="\r", LF="\n"
                )
            else:
                self._strs = NewlineStrs(
                    regex=re.compile(rb"\r\n?|\n"), CR=b"\r", LF=b"\n"
                )
        m = self._strs.regex.search(data)
        if m and not (
            m.group() == self._strs.CR and m.end() == len(data) and not self.closed
        ):
            return m.span()
        else:
            return None

    def _append_item(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if not last or item:
            if self._retain and not last:
                assert self._hold is None
                self._hold = item
            else:
                self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            if self._translate:
                assert self._strs is not None
                item = self._strs.LF
            assert self._hold is not None
            self._append(self._hold + item)
            self._hold = None


def get_newline_splitter(
    newline: Optional[str] = None, retain: bool = False
) -> Splitter[str]:
    if newline is None:
        return UniversalNewlineSplitter(retain=retain, translate=True)
    elif newline == "":
        return UniversalNewlineSplitter(retain=retain, translate=False)
    elif newline in ("\n", "\r\n", "\r"):
        return TerminatedSplitter(newline, retain=retain)
    else:
        raise ValueError(f"Invalid 'newline' value: {newline!r}")


class SplitterClosedError(ValueError):
    pass


class SplitterEmptyError(Exception):
    pass


@dataclass
class NewlineStrs(Generic[AnyStr]):
    regex: re.Pattern[AnyStr]
    CR: AnyStr
    LF: AnyStr


@dataclass(repr=False)
class SplitterState(Generic[AnyStr]):
    items: list[AnyStr]
    buff: Optional[AnyStr]
    hold: Optional[AnyStr]
    closed: bool
    first: bool
