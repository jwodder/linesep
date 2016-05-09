from   itertools import tee
import re
import sys

if sys.version_info[0] == 2:
    from itertools import izip
else:
    izip = zip

def _pairwise(iterable):
    # from <https://docs.python.org/2.7/library/itertools.html#recipes>
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def read_begun(fp, sep, retain=True, size=512):
    # Omits empty leading entry
    entries = read_separated(fp, sep, retain=retain, size=size)
    e = next(entries)
    if e:
        yield e
    if retain:
        for a,b in _pairwise(entries):
            yield a+b
    else:
        for e in entries:
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
