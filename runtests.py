#!/usr/bin/env python
import sys
from optparse import OptionParser


from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'TEST_NAME': 'sentry_tests.db',
            },
        },
        # HACK: this fixes our threaded runserver remote tests
        # DATABASE_NAME='test_sentry',
        TEST_DATABASE_NAME='sentry_tests.db',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'example',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
    )

from django_nose import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):
    if not test_args:
        test_args = ['example']

    kwargs.setdefault('interactive', False)

    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
