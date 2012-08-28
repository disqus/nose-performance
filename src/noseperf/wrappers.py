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

    frames = []

    # set context = 1 to exclude this current frame
    frame = sys._getframe()

    while frame:
        frame_data = _get_frame_data(frame)
        frames.append(frame_data)
        frame = frame.f_back

    frames = filter(_filter_frame_data, frames)

    # Need to delete locals because we cannot get a good representation of them
    for frame in frames:
        del frame['locals']

    return frames


def _get_frame_data(frame):
    """
    Extracts Filename, Line Number, Function Name, Context from a frame
    """
    __traceback_hide__ = True  # NOQA

    ret = {}

    file_name = frame.f_code.co_filename
    ret['file_name'] = file_name
    ret['name'] = frame.f_globals.get('__name__')
    ret['locals'] = frame.f_locals
    ret['line_number'] = frame.f_lineno
    ret['function_name'] = frame.f_code.co_name
    ret['code'] = _get_lines_from_file(frame.f_code.co_filename, frame.f_lineno)
    return ret


def _filter_frame_data(frame_data):
    """
    This function determines if a frame should be removed from a stacktrace.

    This function removes frames that are apart of the performance suite and django.
    """
    __traceback_hide__ = True  # NOQA

    # If the frame is the current file
    if frame_data['name'] == '__main__':
        return False

    # If the frame contains a '__traceback_hide__' variable
    if frame_data['locals'].get('__traceback_hide__', False):
        return False

    # If the frame is in nose
    if frame_data['name'].partition('.')[0] == 'nose':
        return False

    # Remove the test runner
    # if frame_data['name'] == 'disqus.tests.runners':
    #     return False

    # Remove unittest and unittest2
    if frame_data['name'].partition('.')[0] == 'unittest' or frame_data['name'].partition('.')[0] == 'unittest2':
        return False

    return True


def _get_lines_from_file(filename, linenum, context=3):
    """
    Given the filename, and line number will return a dict with the content of
    the line and the context above and below it.
    """
    with open(filename) as f:
        try:
            source = f.readlines()
        except IOError:
            return []

    try:
        ret = []
        for i in xrange(linenum - context, linenum + context + 1):
            line = []
            line.append(i)
            chars = source[i - 1]
            line.append(chars)
            ret.append(line)
        return ret
    except IndexError:
        return []
