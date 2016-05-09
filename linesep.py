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
