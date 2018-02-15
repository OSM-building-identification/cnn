import sys
sys.path.append('util')

import unittest2
import scan


class testScan(unittest2.TestCase):
    def setUp(self):
        pass

    def test_getQuads(self):
        x = [65536, 65171, 65900, 65536]
        box1 = scan.getQuads(x)
        #box2 = scan.getQuads()
        #box3 = scan.getQuads()

        self.assertAlmostEqual(box1[0], [(65536, 65171, 65718.0, 65353.0), (65718.0, 65171, 65900, 65353.0), (65536, 65353.0, 65718.0, 65536), (65718.0, 65353.0, 65900, 65536)], places=1)

if __name__ == '__main__':
    unittest2.main()
