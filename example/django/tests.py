from __future__ import absolute_import

from django.contrib.auth.models import User
from noseperf.testcases import DjangoPerformanceTest


class DjangoSampleTest(DjangoPerformanceTest):
    def test_create_a_bunch_of_users(self):
        for n in xrange(2 ** 8):
            User.objects.create(username='test-%d' % n, email='test-%d@example.com' % n)
