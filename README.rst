nose-performance
================

A performance testing plugin for Nose. It's primary goal is to monitor calls to network applications, such as
the database and memcache.

Integrates with `Zumanji <https://github.com/disqus/zumanji>`_ to report and archive results.

Usage
-----

Create some tests which inherit from ``PerformanceTest``::

    from noseperf.testcases import PerformanceTest

    class MyTest(PerformanceTest):
        def test_redis(self):
            client = Redis()
            for x in xrange(2 ** 16):
                client.add('test-%x' % x, '1')

Run your test suite with the ``--with-performance`` option::

    $ python runtests.py --with-performance example/

(We're using runtests.py because we inject django-nose to test our Django hooks)

Results are recorded to ``test_results/performance.json`` by default::

    $ ls -lh test_results
    total 2128
    -rw-r--r--  1 dcramer  staff   1.0M Aug 27 18:10 performance.json

See the included tests in ``example/`` and ``nosetests --help | grep performance`` for more information.

Test Cases
----------

The plugin will only collect tests which inherit from ``PerformanceTest``. Included are two simple test cases,
one for generic installs, and one for Django:

* noseperf.testcases.PerformanceTest
* noseperf.testcases.DjangoPerformanceTest

Captured Data
-------------

Currently the data captured includes hooks for the following:

- Redis
- Django ORM
- Django Cache
- Django Templates

About
-----

This plugin was originally created at DISQUS by `Zameer Manji <http://twitter.com/zmanji>`_ as an experiment in automating
testing for performance regressions.

Some of the hooks have been inspired by work done in various applications, such as Sentry and Django Debug Toolbar.