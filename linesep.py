STARTER = -1
SEPARATOR = 0
TERMINATOR = 1

def readlines(fp, sep, mode=TERMINATOR, retain=True, size=512):
    if mode < 0:
        return _readlines_start(fp, sep, retain, size)
    elif mode == 0:
        return _readlines_sep(fp, sep, size)
    else:
        return _readlines_term(fp, sep, retain, size)

def _readlines_start(fp, sep, retain=True, size=512):
    # Omits empty leading entry
    entries = _readlines_sep(fp, sep, size=size)
    e = next(entries)
    if e:
        yield e
    for e in entries:
        if retain:
            e = sep + e
        yield e

def _readlines_sep(fp, sep, size=512):
    buff = ''
    for chunk in iter(lambda: fp.read(size), ''):
        buff += chunk
        lines = buff.split(sep)
        buff = lines.pop()
        for l in lines:
            yield l
    yield buff

def _readlines_term(fp, sep, retain=True, size=512):
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
