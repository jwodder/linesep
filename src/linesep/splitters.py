from abc import ABC, abstractmethod
from collections import deque
from typing import AnyStr, Deque, Generic, List, Optional, Tuple


class AbstractSplitter(ABC, Generic[AnyStr]):
    def __init__(self) -> None:
        self._items: Deque[AnyStr] = deque()
        self._buff: Optional[AnyStr] = None
        self._closed: bool = False

    @abstractmethod
    def _find_separator(self, data: AnyStr) -> Optional[Tuple[int, int]]:
        ...

    @abstractmethod
    def _append_item(self, item: AnyStr, final: bool = False) -> None:
        ...

    @abstractmethod
    def _append_separator(self, item: AnyStr) -> None:
        ...

    def _append(self, item: AnyStr) -> None:
        self._items.append(item)

    def _suffix(self, item: AnyStr) -> None:
        # Append `item` to the last element of `_items`
        self._items.append(self._items.pop() + item)

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
            self._append_item(self._buff[:start])
            self._append_separator(self._buff[start:end])
            self._buff = self._buff[end:]
        if self._closed and self._buff is not None:
            self._append_item(self._buff, final=True)
            self._buff = None

    def get(self) -> AnyStr:
        try:
            return self._items.popleft()
        except IndexError:
            raise SplitterEmptyError("No items available in splitter")

    def getall(self) -> List[AnyStr]:
        items = list(self._items)
        self._items.clear()
        return items

    def split(self, data: AnyStr, final: bool = False) -> List[AnyStr]:
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

    def _find_separator(self, data: AnyStr) -> Optional[Tuple[int, int]]:
        try:
            i = data.index(self._separator)
        except ValueError:
            return None
        else:
            return (i, i + len(self._separator))


class TerminatedSplitter(ConstantSplitter[AnyStr]):
    def _append_item(self, item: AnyStr, final: bool = False) -> None:
        if not final or item:
            self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            self._suffix(item)


class SeparatedSplitter(ConstantSplitter[AnyStr]):
    def _append_item(self, item: AnyStr, final: bool = False) -> None:  # noqa: U100
        self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            self._append(item)


class PrecededSplitter(ConstantSplitter[AnyStr]):
    def __init__(self, separator: AnyStr, retain: bool = False) -> None:
        # <https://github.com/python/mypy/issues/12984>
        super().__init__(separator, retain)  # type: ignore[arg-type]
        self._first: bool = True
        self._itembuf: Optional[AnyStr] = None

    def _append_item(self, item: AnyStr, final: bool = False) -> None:  # noqa: U100
        if self._first:
            if item:
                self._append(item)
            self._first = False
        elif self._retain:
            assert self._itembuf is not None
            self._append(self._itembuf + item)
            self._itembuf = None
        else:
            self._append(item)

    def _append_separator(self, item: AnyStr) -> None:
        if self._retain:
            assert self._itembuf is None
            self._itembuf = item


class SplitterClosedError(ValueError):
    pass


class SplitterEmptyError(Exception):
    pass
