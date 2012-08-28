nose-performance
================

A performance testing plugin for Nose.

Integrates with `Zumanji <https://github.com/disqus/zumanji>`_ to report and archive results.

Usage
-----

Run your test suite with the ``--with-performance`` option::

    $ python runtests.py --with-performance example/

(We're using runtests.py because we inject django-nose to test our Django hooks)

Results are recorded to ``test_results/performance.json`` by default::

    $ ls -lh test_results
    total 2128
    -rw-r--r--  1 dcramer  staff   1.0M Aug 27 18:10 performance.json

For more options, nosetests --help | grep performance

Captured Data
-------------

Currently the data captured includes hooks for the following:

- Redis
- Django ORM
- Django Cache

About
-----

This plugin was originally created at DISQUS by `Zameer Manji <http://twitter.com/zmanji>`_ as an experiment in automating
testing for performance regressions.