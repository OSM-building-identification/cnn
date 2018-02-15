import sys
sys.path.append('util')

import unittest2

# Whatever is being tested
import naip


class TestNAIP(unittest2.TestCase):
    def setUp(self):
        pass

    def test_tile2deg(self):
        x = naip.tile2deg(100, 100, 17)
        y = naip.tile2deg(-9999, -9999, 17)
        z = naip.tile2deg(-9999, 9999, 17)

        self.assertAlmostEqual(x[0], -179.72579, places=6)
        self.assertAlmostEqual(x[1], 85.02737824, places=6)

        self.assertAlmostEqual(y[0], -207.46307373, places=6)
        self.assertAlmostEqual(y[1], 86.93446581, places=6)

        self.assertAlmostEqual(z[0], -207.46307373, places=6)
        self.assertAlmostEqual(z[1], 82.01565745, places=6)

if __name__=='__main__':
    unittest2.main()
