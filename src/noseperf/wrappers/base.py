"""
noseperf.wrappers.base
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

import time
from noseperf.stacks import get_stack_info, iter_stack_frames


class Wrapper(object):
    """Wraps Redis methods and logs the results """

    def __init__(self, data):
        self.data = data

    def _record(self, data):
        data['stacktrace'] = get_stack_info(iter_stack_frames())

        self.data.append(data)


class FunctionWrapper(Wrapper):
    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()

            data = {
                'command': func.__name__,
                'args': repr(args),
                'kwargs': repr(kwargs),
                'start': start,
                'end': end,
            }

            self._record(data)