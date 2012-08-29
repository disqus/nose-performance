from __future__ import absolute_import

import redis
import time

from noseperf.testcases import PerformanceTest


class RedisSampleTest(PerformanceTest):
    def setUp(self):
        self.client = redis.Redis()
        self.key = 'noseperf:hashtest'

    def tearDown(self):
        self.client.delete(self.key)

    def test_setting_lots_of_hashes(self):
        for n in xrange(2 ** 5):
            self.client.hset(self.key, str(n), time.time())

    def test_pipeline_hashes(self):
        with self.client.pipeline() as conn:
            for n in xrange(2 ** 5):
                conn.hset(self.key, str(n), time.time())
            conn.execute()
