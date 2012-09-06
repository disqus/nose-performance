"""
noseperf.wrappers.django
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

import time
from noseperf.wrappers.base import Wrapper


class DjangoTemplateWrapper(Wrapper):
    _perftype = 'template'

    def __call__(self, func, template, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time.time()

        try:
            return func(template, *args, **kwargs)
        finally:
            end = time.time()
            self._record({
                'name': 'render',
                'args': [template.name],
                'start': start,
                'end': end,
            })


class DjangoCursorWrapper(Wrapper):
    _perftype = 'sql'

    def __init__(self, cursor, connection, *args, **kwargs):
        self.cursor = cursor
        self.connection = connection
        super(DjangoCursorWrapper, self).__init__(*args, **kwargs)

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

            # Save the data
            data = {
                'name': operation,
                'args': parameters,
                'start': start,
                'end': end,
            }
            self._record(data)

    def executemany(self, operation, parameters):
        __traceback_hide__ = True  # NOQA

        # The real cursor calls execute in executemany so nothing needs to be
        # recorded here.
        self.cursor.executemany(operation, parameters)


def patch_cursor(data):
    def patched_cursor(func, self):
        cursor = func(self)
        return DjangoCursorWrapper(cursor, self, data)
    return patched_cursor
