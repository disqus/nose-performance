from noseperf.testcases import PerformanceTest

import math
import redis
import time


class MySampleTest(PerformanceTest):
    def test_math_in_a_loop(self):
        for n in xrange(2 ** 8):
            math.sqrt(n)


class RedisSampleTest(PerformanceTest):
    def setUp(self):
        self.client = redis.Redis()
        self.key = 'noseperf:hashtest'

    def tearDown(self):
        self.client.delete(self.key)

    def test_setting_lots_of_hashes(self):
        for n in xrange(2 ** 8):
            self.client.hset(self.key, str(n), time.time())

    def test_pipeline_hashes(self):
        with self.client.pipeline() as conn:
            for n in xrange(2 ** 8):
                conn.hset(self.key, str(n), time.time())
            conn.execute()
