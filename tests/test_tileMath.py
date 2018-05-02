import sys
sys.path.append('util')

import unittest2

# Whatever is being tested
import tileMath

class TestNAIP(unittest2.TestCase):
    def setUp(self):
        pass

    def test_tile2deg(self):
        x = tileMath.tile2deg(100, 100, 17)
        y = tileMath.tile2deg(-9999, -9999, 17)
        z = tileMath.tile2deg(-9999, 9999, 17)

        self.assertAlmostEqual(x[0], -179.72534179, places=6)
        self.assertAlmostEqual(x[1], 85.02737824, places=6)

        self.assertAlmostEqual(y[0], -207.46307373, places=6)
        self.assertAlmostEqual(y[1], 86.93446581, places=6)

        self.assertAlmostEqual(z[0], -207.46307373, places=6)
        self.assertAlmostEqual(z[1], 82.01565745, places=6)

    def test_deg2tile(self):
        x = tileMath.deg2tile(-179.72534179, 85.02737824, 17)
        y = tileMath.deg2tile(50, 50, 17)
        z = tileMath.deg2tile(-50, -50, 17)

        self.assertEqual(x[0], 100)
        self.assertEqual(x[1], 100)

        self.assertEqual(y[0], 83740)
        self.assertEqual(y[1], 44452)

        self.assertEqual(z[0], 47331)
        self.assertEqual(z[1], 86619)

if __name__=='__main__':
    unittest2.main()
