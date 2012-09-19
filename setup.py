"""
nose-performance
================

:copyright: (c) 2012 DISQUS
:license: Apache License 2.0, see LICENSE for more details.
"""

from setuptools import setup, find_packages

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

tests_require = [
    'psycopg2',
    'redis',
    'Django>=1.2',
]

install_requires = [
    'nose>=0.9',
    'simplejson',
    'unittest2',
]

setup(
    name='nose-performance',
    version='0.4.1',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/nose-performance',
    description='A plugin for Nose for running performance tests',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    # tests_require=tests_require,
    # test_suite='runtests.runtests',
    license='Apache License 2.0',
    include_package_data=True,
    entry_points={
       'nose.plugins.0.10': [
            'noseperf = noseperf.plugin:PerformancePlugin'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
