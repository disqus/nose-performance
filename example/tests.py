from noseperf.testcases import PerformanceTest

import math


class MySampleTest(PerformanceTest):
    def test_math_in_a_loop(self):
        for n in xrange(2 ** 24):
            math.sqrt(n)
