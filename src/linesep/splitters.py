from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator
from dataclasses import dataclass
import re
from typing import AnyStr, Generic, Optional


class Splitter(ABC, Generic[AnyStr]):
    """
    .. versionadded:: 0.4.0

    Abstract base class for all splitters.  The abstract methods are an
    implementation detail; this class is exported only for `isinstance()` and
    typing purposes and should not be subclassed by users.
    """

    def __init__(self) -> None:
        #: The output queue
        self._items: deque[AnyStr] = deque()
        #: The buffer of unsplit input data
        self._buff: Optional[AnyStr] = None
        #: A "hold space" for holding intermediate states of compound output
        #: items
        self._hold: Optional[AnyStr] = None
        #: Whether `close()` has been called
        self._closed: bool = False
        #: Whether we've handled the first split segment yet
        self._first: bool = True

    @abstractmethod
    def _find_separator(self, data: AnyStr) -> Optional[tuple[int, int]]:
        """
        Find the first occurrence of a separator in ``data`` and return the
        separator's starting and ending indices; if no separator is found,
        return `None`.
        """
        ...

    @abstractmethod
    def _handle_segment(
        self, item: AnyStr, first: bool = False, last: bool = False
    ) -> None:
        """
        Process split segment ``item``.

        :param bool first: Whether this is the first segment in the data stream
        :param bool last: Whether this is the last segment in the data stream
        """
        ...

    @abstractmethod
    def _handle_separator(self, item: AnyStr) -> None:
        """Process split separator ``item``"""
        ...

    def _output(self, item: AnyStr) -> None:
        """Append ``item`` to the output queue"""
        self._items.append(item)

    def _split(self) -> None:
        """Split up the current contents of `_buff`"""
        while self._buff:
            span = self._find_separator(self._buff)
            if span is None:
                break
            start, end = span
            self._handle_segment(self._buff[:start], first=self._first)
            self._first = False
            self._handle_separator(self._buff[start:end])
            self._buff = self._buff[end:]
        if self._closed and self._buff is not None:
            self._handle_segment(self._buff, first=self._first, last=True)
            self._buff = None

    def feed(self, data: AnyStr) -> None:
        """
        Split input ``data``.  Any segments or separators extracted can
        afterwards be retrieved by calling `get()` or `getall()`.

        :raises SplitterClosedError:
            if `close()` has already been called on this splitter
        """
        if self._closed:
            raise SplitterClosedError("Cannot feed data to closed splitter")
        if self._buff is None:
            self._buff = data
        else:
            self._buff += data
        self._split()

    def get(self) -> AnyStr:
        """
        Retrieve the next unfetched item that has been split from the input.

        :raises SplitterEmptyError: if there are no items currently available
        """
        try:
            return self._items.popleft()
        except IndexError:
            raise SplitterEmptyError("No items available in splitter")

    @property
    def nonempty(self) -> bool:
        """Whether a subsequent call to `get()` would return an item"""
        return bool(self._items)

    def getall(self) -> list[AnyStr]:
        """Retrieve all unfetched items that have been split from the input"""
        items = list(self._items)
        self._items.clear()
        return items

    def split(self, data: AnyStr, final: bool = False) -> list[AnyStr]:
        """
        Split input ``data`` and return all items thus extracted.  Set
        ``final`` to `True` if this is the last chunk of input.

        Note that, if a previous call to `feed()` was not followed by enough
        calls to `get()` to retrieve all items, any items left over from the
        previous round of input will be prepended to the list returned by this
        method.

        :raises SplitterClosedError:
            if `close()` has already been called on this splitter
        """
        self.feed(data)
        if final:
            self.close()
        return self.getall()

    def close(self) -> None:
        """
        Indicate to the splitter that the end of input has been reached.  No
        further calls to `feed()` or `split()` may be made after calling this
        method unless `reset()` or `setstate()` is called in between.

        Depending on the internal state, calling this method may cause more
        segments or separators to be split from unprocessed input; be sure to
        fetch them with `get()` or `getall()`.
        """
        self._closed = True
        if self._buff is not None:
            self._split()

    @property
    def closed(self) -> bool:
        """Whether `close()` has been called on this splitter"""
        return self._closed

    def reset(self) -> None:
        """
        Reset the splitter to its initial state, as though a new instance with
        the same parameters were constructed
        """
        self._items.clear()
        self._buff = None
        self._hold = None
        self._closed = False
        self._first = True

    def getstate(self) -> SplitterState[AnyStr]:
        """Retrieve a representation of the splitter's current state"""
        return SplitterState(
            items=list(self._items),
            buff=self._buff,
            hold=self._hold,
            closed=self._closed,
            first=self._first,
        )

    def setstate(self, state: SplitterState[AnyStr]) -> None:
        """
        Restore the state of the splitter to the what it was when the
        corresponding `getstate()` call was made
        """
        self._items.clear()
        self._items.extend(state.items)
        self._buff = state.buff
        self._hold = state.hold
        self._closed = state.closed
        self._first = state.first

    def itersplit(self, iterable: Iterable[AnyStr]) -> Iterator[AnyStr]:
        """
        Feed each element of ``iterable`` as input to the splitter and yield
        each item produced.

        None of the splitter's other methods should be called while iterating
        over the yielded values.

        The splitter's state is saved & reset before processing the iterable,
        and the saved state is restored at the end.  If you break out of the
        resulting iterator early, the splitter will be in an undefined state
        unless & until you reset it.
        """
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
        """Like `itersplit()`, but for asynchronous iterators"""
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
    """
    .. versionadded:: 0.4.0

    A splitter that uses a single, fixed string as the separator
    """

    def __init__(self, separator: AnyStr, retain: bool = False) -> None:
        """
        :param AnyStr separator: The string to split the input on
        :param bool retain:
            Whether to include the separators in split items (`True`) or
            discard them (`False`, default)
        :raises ValueError: if ``separator`` is an empty string
        """
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
    """
    .. versionadded:: 0.4.0

    A splitter that splits segments terminated by a given string
    """

    def _handle_segment(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if not last or item:
            if self._retain and not last:
                assert self._hold is None
                self._hold = item
            else:
                self._output(item)

    def _handle_separator(self, item: AnyStr) -> None:
        if self._retain:
            assert self._hold is not None
            self._output(self._hold + item)
            self._hold = None


class SeparatedSplitter(ConstantSplitter[AnyStr]):
    """
    .. versionadded:: 0.4.0

    A splitter that splits segments separated by a given string.

    Note that, when ``retain`` is true, separators are returned as separate
    items, alternating with segments (unlike `TerminatedSplitter` and
    `PrecededSplitter`, where separators are appended/prepended to the
    segments).  In a list returned by `split()` or `getall()`, the segments
    will be the items at the even indices (starting at 0), and the separators
    will be at the odd indices (assuming you're calling `get()` the right
    amount of times and not leaving any output unfetched).
    """

    def _handle_segment(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        self._output(item)

    def _handle_separator(self, item: AnyStr) -> None:
        if self._retain:
            self._output(item)


class PrecededSplitter(ConstantSplitter[AnyStr]):
    """
    .. versionadded:: 0.4.0

    A splitter that splits segments preceded by a given string
    """

    def _handle_segment(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if first:
            if item:
                self._output(item)
        elif self._retain:
            assert self._hold is not None
            self._output(self._hold + item)
            self._hold = None
        else:
            self._output(item)

    def _handle_separator(self, item: AnyStr) -> None:
        if self._retain:
            assert self._hold is None
            self._hold = item


class UniversalNewlineSplitter(Splitter[AnyStr]):
    """
    .. versionadded:: 0.4.0

    A splitter that splits on the ASCII newline sequences ``"\\n"``,
    ``"\\r\\n"``, and ``"\\r"``.
    """

    def __init__(self, retain: bool = False, translate: bool = True) -> None:
        """
        :param bool retain:
            Whether to include the newlines in split items (`True`) or discard
            them (`False`, default)
        :param bool translate:
            Whether to convert all retained newlines to ``"\\n"`` (`True`,
            default) or leave them as-is (`False`)
        """
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

    def _handle_segment(
        self, item: AnyStr, first: bool = False, last: bool = False  # noqa: U100
    ) -> None:
        if not last or item:
            if self._retain and not last:
                assert self._hold is None
                self._hold = item
            else:
                self._output(item)

    def _handle_separator(self, item: AnyStr) -> None:
        if self._retain:
            if self._translate:
                assert self._strs is not None
                item = self._strs.LF
            assert self._hold is not None
            self._output(self._hold + item)
            self._hold = None


def get_newline_splitter(
    newline: Optional[str] = None, retain: bool = False
) -> Splitter[str]:
    """
    .. versionadded:: 0.4.0

    Return a splitter for splitting on newlines following the same rules as the
    ``newline`` option to `open()`.

    Specifically:

    - If ``newline`` is `None`, a splitter that splits on all ASCII newlines
      and converts them to ``"\\n"`` is returned.
    - If ``newline`` is ``""`` (the empty string), a splitter that splits on
      all ASCII newlines and leaves them as-is is returned.
    - If ``newline`` is ``"\\n"``, ``"\\r\\n"``, or ``"\\r"``, a splitter that
      splits on the given string is returned.
    - If ``newline`` is any other value, a `ValueError` is raised.

    Note that this function is limited to splitting on `str`\\s and does not
    support `bytes`.

    :param bool retain:
        Whether the returned splitter should include the newlines in split
        items (`True`) or discard them (`False`, default)
    """
    if newline is None:
        return UniversalNewlineSplitter(retain=retain, translate=True)
    elif newline == "":
        return UniversalNewlineSplitter(retain=retain, translate=False)
    elif newline in ("\n", "\r\n", "\r"):
        return TerminatedSplitter(newline, retain=retain)
    else:
        raise ValueError(f"Invalid 'newline' value: {newline!r}")


class SplitterClosedError(ValueError):
    """
    .. versionadded:: 0.4.0

    Raised when `~Splitter.feed()` or `~Splitter.split()` is called on a
    splitter after its `~Splitter.close()` method is called
    """

    pass


class SplitterEmptyError(Exception):
    """
    .. versionadded:: 0.4.0

    Raised when `~Splitter.get()` is called on a splitter that does not have any
    unfetched items to return
    """

    pass


@dataclass
class NewlineStrs(Generic[AnyStr]):
    regex: re.Pattern[AnyStr]
    CR: AnyStr
    LF: AnyStr


@dataclass(repr=False)
class SplitterState(Generic[AnyStr]):
    """
    .. versionadded:: 0.4.0

    A representation of the internal state of a splitter, returned by
    `~Splitter.getstate()`.  This can be passed to `~Splitter.setstate()` to
    restore the spitter's internal state to what it was previously.

    A given `SplitterState` should only be passed to the `~Splitter.setstate()`
    method of a splitter of the same class and with the same constructor
    arguments as the splitter that produced the `SplitterState`; otherwise, the
    behavior is undefined.

    Instances of this class should be treated as opaque objects and should not
    be inspected, nor should any observed property be relied upon to be the
    same in future library versions.
    """

    items: list[AnyStr]
    buff: Optional[AnyStr]
    hold: Optional[AnyStr]
    closed: bool
    first: bool
