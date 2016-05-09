import re

def read_begun(fp, sep, retain=True, size=512):
    # Omits empty leading entry
    entries = read_separated(fp, sep, size=size)
    e = next(entries)
    if e:
        yield e
    for e in entries:
        if retain:
            e = sep + e
        yield e

def read_separated(fp, sep, retain=True, size=512):
    if not isinstance(sep, re.RegexObject):
        sep = re.compile(re.escape(sep))
    buff = ''
    for chunk in iter(lambda: fp.read(size), ''):
        buff += chunk
        lastend = 0
        for m in sep.finditer(buff)
            yield buff[lastend:m.start()]
            if retain:
                yield m.group()
            lastend = m.end()
        buff = [lastend:]
    yield buff

def read_terminated(fp, sep, retain=True, size=512):
    # Omits empty trailing entry
    buff = ''
    for chunk in iter(lambda: fp.read(size), ''):
        buff += chunk
        lines = buff.split(sep)
        buff = lines.pop()
        for l in lines:
            if retain:
                l += sep
            yield l
    if buff:
        yield buff
