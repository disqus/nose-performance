"""
noseperf.util
~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

from functools import wraps


def _dot_lookup(thing, comp, import_path):
    try:
        return getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(thing, comp)


def import_string(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    return thing


class PatchContext(object):
    def __init__(self, target, callback):
        target, attr = target.rsplit('.', 1)
        target = import_string(target)
        self.func = getattr(target, attr)
        self.target = target
        self.attr = attr
        self.callback = callback

    def __enter__(self):
        @wraps(getattr(self.target, self.attr))
        def wrapped(*args, **kwargs):
            __traceback_hide__ = True  # NOQA
            return self.callback(self.func, *args, **kwargs)

        setattr(self.target, self.attr, wrapped)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(self.target, self.attr, self.func)


def lsprof_to_dict(entry):
    "Takes a lsprof profile entry and turns it into a dict of useful values."
    d = {}
    d['callcount'] = entry.callcount
    d['reccallcount'] = entry.reccallcount
    d['totaltime'] = entry.totaltime
    d['inlinetime'] = entry.inlinetime
    if type(entry.code) == str:
        d['code'] = entry.code
        try:
            kind = entry.code.split(" ")[0]
            if kind is "method":
                d['name'] = entry.code.split(" ")[1][1:-1]
            elif kind is "built-in":
                d['name'] = entry.code.split(" ")[2][1:-1]
            else:
                raise IndexError
        except IndexError:
            d['name'] = entry.code
        d['file_name'] = None
    else:
        d['code'] = str(entry.code)
        d['file_name'] = entry.code.co_filename
        d['name'] = entry.code.co_name

    if hasattr(entry, 'calls'):
        calls = entry.calls or []
        d['calls'] = map(lsprof_to_dict, calls)

    return d

