import re

def join_pairs(iterable):
    while True:
        a = next(iterable)
        try:
            b = next(iterable)
        except StopIteration:
            yield a
            return
        else:
            yield a + b

def read_preceded(fp, sep, retain=True, size=512):
    """
    Read from a file-like object ``fp`` containing entries starting
    with/preceded by the string or compiled regex ``sep`` and return a
    generator of the entries.  An empty file will always produce an empty
    generator.

    If ``retain`` is `True`, each entry (except possibly the first) will have
    its leading delimiter prepended to it.  If ``sep`` is a compiled regex, the
    delimiter will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, leading delimiters will not be present in the
    output entries.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    # Omits empty leading entry
    entries = read_separated(fp, sep, retain=retain, size=size)
    e = next(entries)
    if e:
        yield e
    if retain:
        entries = join_pairs(entries)
    for e in entries:
        yield e

def read_separated(fp, sep, retain=True, size=512):
    """
    Read from a file-like object ``fp`` containing entries separated by the
    string or compiled regex ``sep`` and return a generator of the entries.  An
    empty file will always produce a generator with one element, the empty
    string.

    If ``retain`` is `True`, the separators will be included in the output: the
    generator will contain an odd number of elements, alternating between
    entries and separators, starting with a (possibly empty) entry.  If ``sep``
    is a compiled regex, the separator elements will be the strings matched by
    the regex; any capturing subgroups will be ignored.

    If ``retain`` is `False`, separators will not be present in the output.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    if not isinstance(sep, re.RegexObject):
        sep = re.compile(re.escape(sep))
    buff = ''
    for chunk in iter(lambda: fp.read(size), ''):
        buff += chunk
        lastend = 0
        for m in sep.finditer(buff):
            yield buff[lastend:m.start()]
            if retain:
                yield m.group()
            lastend = m.end()
        buff = buff[lastend:]
    yield buff

def read_terminated(fp, sep, retain=True, size=512):
    """
    Read from a file-like object ``fp`` containing entries terminated by the
    string or compiled regex ``sep`` and return a generator of the entries.  An
    empty file will always produce an empty generator.

    If ``retain`` is `True`, each entry (except possibly the last) will have
    its terminator appended to it.  If ``sep`` is a compiled regex, the
    terminator will be the string matched by the regex at that point; any
    capturing subgroups will be ignored.

    If ``retain`` is `False`, terminators will not be present in the output
    entries.

    ``size`` specifies how many bytes or characters to read from ``fp`` at a
    time.
    """
    # Omits empty trailing entry
    prev = None
    entries = read_separated(fp, sep, retain=retain, size=size)
    if retain:
        entries = join_pairs(entries)
    for e in entries:
        if prev is not None:
            yield prev
        prev = e
    if prev:
        yield prev
