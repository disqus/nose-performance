"""
noseperf.stacks
~~~~~~~~~~~~~~~

This code is part of the `Raven <https://github.com/getsentry/raven>`_ project.

It's nearly identical except that we don't extract local variables.

:copyright: (c) 2010 by the Sentry Team.
:license: BSD, see LICENSE for more details.
"""

import inspect
import re
import sys


_coding_re = re.compile(r'coding[:=]\s*([-\w.]+)')


def frames_after_module(frames, module):
    started = False
    last_mod = ''
    results = []
    for frame, lineno in list(frames)[::-1]:
        if not started:
            f_globals = getattr(frame, 'f_globals', {})
            module_name = _getitem_from_frame(f_globals, '__name__')
            if (last_mod and last_mod.startswith('unittest2')) \
                and not module_name.startswith('unittest2'):
                started = True
            else:
                last_mod = module_name
                continue
        results.append((frame, lineno))
    return results


def get_lines_from_file(filename, lineno, context_lines, loader=None, module_name=None):
    """
    Returns context_lines before and after lineno from file.
    Returns (pre_context_lineno, pre_context, context_line, post_context).
    """
    source = None
    if loader is not None and hasattr(loader, "get_source"):
        try:
            source = loader.get_source(module_name)
        except ImportError:
            # Traceback (most recent call last):
            #   File "/Users/dcramer/Development/django-sentry/sentry/client/handlers.py", line 31, in emit
            #     get_client().create_from_record(record, request=request)
            #   File "/Users/dcramer/Development/django-sentry/sentry/client/base.py", line 325, in create_from_record
            #     data['__sentry__']['frames'] = varmap(shorten, get_stack_info(stack))
            #   File "/Users/dcramer/Development/django-sentry/sentry/utils/stacks.py", line 112, in get_stack_info
            #     pre_context_lineno, pre_context, context_line, post_context = get_lines_from_file(filename, lineno, 7, loader, module_name)
            #   File "/Users/dcramer/Development/django-sentry/sentry/utils/stacks.py", line 24, in get_lines_from_file
            #     source = loader.get_source(module_name)
            #   File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/pkgutil.py", line 287, in get_source
            #     fullname = self._fix_name(fullname)
            #   File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/pkgutil.py", line 262, in _fix_name
            #     "module %s" % (self.fullname, fullname))
            # ImportError: Loader for module cProfile cannot handle module __main__
            source = None
        if source is not None:
            source = source.splitlines()

    if source is None:
        try:
            f = open(filename)
            try:
                source = f.readlines()
            finally:
                f.close()
        except (OSError, IOError):
            pass

    if source is None:
        return []

    encoding = 'ascii'
    for line in source[:2]:
        # File coding may be specified. Match pattern from PEP-263
        # (http://www.python.org/dev/peps/pep-0263/)
        match = _coding_re.search(line)
        if match:
            encoding = match.group(1)
            break
    source = [unicode(sline, encoding, 'replace') for sline in source]

    lower_bound = max(0, lineno - context_lines)
    upper_bound = min(lineno + context_lines + 1, len(source))

    try:
        return [(lineno + 1, source[lineno].strip('\n')) for lineno in xrange(lower_bound, upper_bound)]
    except IndexError:
        # the file may have changed since it was loaded into memory
        return []


def _getitem_from_frame(f_locals, key, default=None):
    """
    f_locals is not guaranteed to have .get(), but it will always
    support __getitem__. Even if it doesnt, we return ``default``.
    """
    try:
        return f_locals[key]
    except Exception:
        return default


def iter_stack_frames(frames=None):
    """
    Given an optional list of frames (defaults to current stack),
    iterates over all frames that do not contain the ``__traceback_hide__``
    local variable.
    """
    if not frames:
        frames = inspect.stack()[1:]

    for frame, lineno in ((f[0], f[2]) for f in frames):
        f_locals = getattr(frame, 'f_locals', {})
        if _getitem_from_frame(f_locals, '__traceback_hide__'):
            continue
        yield frame, lineno


def get_stack_info(frames):
    """
    Given a list of frames, returns a list of stack information
    dictionary objects that are JSON-ready.

    We have to be careful here as certain implementations of the
    _Frame class do not contain the nescesary data to lookup all
    of the information we want.
    """
    __traceback_hide__ = True  # NOQA

    results = []
    for frame_info in frames:
        # Old, terrible API
        if isinstance(frame_info, (list, tuple)):
            frame, lineno = frame_info

        else:
            frame = frame_info
            lineno = frame_info.f_lineno

        # Support hidden frames
        f_locals = getattr(frame, 'f_locals', {})
        if _getitem_from_frame(f_locals, '__traceback_hide__'):
            continue

        f_globals = getattr(frame, 'f_globals', {})
        loader = _getitem_from_frame(f_globals, '__loader__')
        module_name = _getitem_from_frame(f_globals, '__name__')

        f_code = getattr(frame, 'f_code', None)
        if f_code:
            abs_path = frame.f_code.co_filename
            function = frame.f_code.co_name
        else:
            abs_path = None
            function = None

        if lineno:
            lineno -= 1

        if lineno is not None and abs_path:
            context = get_lines_from_file(abs_path, lineno, 3, loader, module_name)
        else:
            context = []

        # Try to pull a relative file path
        # This changes /foo/site-packages/baz/bar.py into baz/bar.py
        try:
            base_filename = sys.modules[module_name.split('.', 1)[0]].__file__
            filename = abs_path.split(base_filename.rsplit('/', 2)[0], 1)[-1][1:]
        except:
            filename = abs_path

        if not filename:
            filename = abs_path

        frame_result = {
            'abs_path': abs_path,
            'filename': filename,
            'module': module_name,
            'function': function,
            'lineno': lineno + 1,
            'context': context,
        }
        results.append(frame_result)
    return results
