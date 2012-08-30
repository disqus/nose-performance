"""
noseperf.wrappers
~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

from datetime import datetime
import sys
import time
import logging

from noseperf.stacks import get_stack_info, iter_stack_frames


class RedisPipelineHook(object):
    """Wraps Redis methods and logs the results """

    logger = logging.getLogger(__name__)

    def __init__(self, data):
        self.data = data

    def __call__(self, func, pipeline, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        command_stack = pipeline.command_stack[:]

        retval = None
        start = time.time()
        try:
            retval = func(pipeline, *args, **kwargs)
            return retval
        finally:
            end = time.time()
            duration = end - start

            redis = {
                'command': 'pipeline',
                'actions': repr(command_stack),
                'kwargs': repr(kwargs),
                'time': datetime.now().isoformat(),
                'duration': duration,
                'stacktrace': _get_stack(),
                'value': repr(retval),
            }

            self.data.append(redis)


class PerformanceRedisWrapper(object):
    """Wraps Redis methods and logs the results """

    logger = logging.getLogger(__name__)

    def __init__(self, data):
        self.data = data

    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        redis = {}
        redis['command'] = args[1]
        redis['other_args'] = repr(args[2:])
        redis['kwargs'] = repr(kwargs)
        redis['time'] = datetime.now().isoformat()

        retval = None
        start = time.time()
        try:
            retval = func(*args, **kwargs)
            return retval
        finally:
            end = time.time()
            duration = end - start

            redis['duration'] = duration
            redis['stacktrace'] = _get_stack()
            redis['value'] = repr(retval)

            self.data.append(redis)


class PerformanceCacheWrapper(object):
    """Wraps a cache method and log the results"""

    def __init__(self, data, action):
        self.data = data
        self.action = action

    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        cache = {}
        cache['key'] = args[1]
        cache['other_args'] = repr(args[2:])
        cache['action'] = self.action
        cache['time'] = datetime.now().isoformat()

        retval = None
        start = time.time()
        try:
            retval = func(*args, **kwargs)
            return retval
        finally:
            end = time.time()

            duration = end - start

            cache['duration'] = duration
            cache['stacktrace'] = _get_stack()
            cache['value'] = repr(retval)

            self.data.append(cache)


class PerformanceCursorWrapper(object):
    """Wraps a cursor to profile and log database queries"""

    def __init__(self, cursor, data, connection):
        self.cursor = cursor
        self.data = data
        self.connection = connection

    def __getattr__(self, attr):
        __traceback_hide__ = True  # NOQA

        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        __traceback_hide__ = True  # NOQA

        return iter(self.cursor)

    def execute(self, operation, parameters=()):
        """
        Wraps execute method to record the query, execution duration and
        stackframe.
        """
        __traceback_hide__ = True  # NOQ

        # Time the exection of the query

        start = time.time()
        try:
            return self.cursor.execute(operation, parameters)
        finally:
            end = time.time()

            duration = end - start

            # Capture the stackframe of execution
            stacktrace = _get_stack()

            # Save the data
            sql = {}
            sql['query'] = operation
            sql['query_params'] = parameters
            sql['full_query'] = operation % tuple(parameters)
            sql['duration'] = duration
            sql['stacktrace'] = stacktrace
            sql['time'] = datetime.now().isoformat()
            self.data.append(sql)

    def executemany(self, operation, parameters):
        __traceback_hide__ = True  # NOQA

        # The real cursor calls execute in executemany so nothing needs to be
        # recorded here.
        self.cursor.executemany(operation, parameters)


def patch_cursor(data):
    def patched_cursor(func, self):
        cursor = func(self)
        return PerformanceCursorWrapper(cursor, data, self)
    return patched_cursor


# Util functions for stacks

def _get_stack():
    __traceback_hide__ = True  # NOQA

    return get_stack_info(iter_stack_frames())
