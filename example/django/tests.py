from __future__ import absolute_import

from django.core.cache import cache
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from noseperf.testcases import DjangoPerformanceTest


class DjangoSampleTest(DjangoPerformanceTest):
    def test_create_a_bunch_of_users(self):
        for n in xrange(2 ** 5):
            User.objects.create(username='test-%d' % n, email='test-%d@example.com' % n)

    def test_use_the_cache(self):
        for n in xrange(2 ** 5):
            cache.set('test-%s' % (n - 1), n)
            cache.set('test-%s-%s' % (n, n - 1), cache.get('test-%s' % (n - 1)))

    def test_the_world(self):
        for n in xrange(2 ** 5):
            cache.set('test-%s' % n, n)
            User.objects.create(username='test-%d' % n, email='test-%d@example.com' % n)

    def test_render_templates(self):
        for n in xrange(2 ** 3):
            render_to_string('loop.html', {'range': xrange(2 ** 3)})
