"""
noseperf.testcases
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

from unittest2 import TestCase


class PerformanceTest(TestCase):
    """
    A base class for performance tests.

    Nose can discover these classes and execute the tests. The performance
    plugin will then profile the tests and measure activity.
    """
    tags = ["performance"]
