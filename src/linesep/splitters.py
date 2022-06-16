from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import AnyStr, Generic, Optional


class AbstractSplitter(ABC, Generic[AnyStr]):
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


class ConstantSplitter(AbstractSplitter[AnyStr]):
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


class SplitterClosedError(ValueError):
    pass


class SplitterEmptyError(Exception):
    pass
