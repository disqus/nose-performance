"""
noseperf.wrappers.redis
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

import time
from noseperf.wrappers.base import Wrapper


class RedisPipelineWrapper(Wrapper):
    _perftype = 'redis'

    def __call__(self, func, pipeline, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        command_stack = pipeline.command_stack[:]

        start = time.time()
        try:
            return func(pipeline, *args, **kwargs)
        finally:
            end = time.time()

            data = {
                'name': 'pipeline',
                'args': repr(command_stack),
                'kwargs': repr({}),
                'start': start,
                'end': end,
            }

            self._record(data)


class RedisWrapper(Wrapper):
    _perftype = 'redis'

    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()

            data = {
                'name': args[1],
                'args': repr(args[2:]),
                'kwargs': repr(kwargs),
                'start': start,
                'end': end,
            }
            self._record(data)
