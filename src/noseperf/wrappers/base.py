"""
noseperf.wrappers.base
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

import inspect
import time
from noseperf.stacks import get_stack_info, iter_stack_frames, frames_after_module


class Wrapper(object):
    """Wraps Redis methods and logs the results """

    def __init__(self, data):
        self.data = data

    def _record(self, data):
        frames = frames_after_module(iter_stack_frames(inspect.stack()[2:]), 'unittest2')
        data['stacktrace'] = get_stack_info(frames)
        if 'type' not in data:
            data['type'] = self._perftype
        self.data.append(data)


class FunctionWrapper(Wrapper):
    _perfkey = None

    def __init__(self, perfkey=None, *args, **kwargs):
        super(FunctionWrapper, self).__init__(*args, **kwargs)
        self._perfkey = perfkey

    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()

            if getattr(func, 'im_class', None):
                arg_str = repr(args[1:])
            else:
                arg_str = repr(args)

            data = {
                'type': self._perfkey or func.__name__,
                'name': func.__name__,
                'args': arg_str,
                'kwargs': repr(kwargs),
                'start': start,
                'end': end,
            }

            self._record(data)
