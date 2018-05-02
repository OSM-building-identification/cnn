import sys
sys.path.append('util')
sys.path.append('classifier')

import unittest2
import scan


class testScan(unittest2.TestCase):
    def setUp(self):
        pass

    def test_getQuads(self):
        box1 = scan.getQuads([65536, 65171, 65900, 65536])
        self.assertAlmostEqual(box1, [(65536, 65171, 65718.0, 65353.0), (65718.0, 65171, 65900, 65353.0), (65536, 65353.0, 65718.0, 65536), (65718.0, 65353.0, 65900, 65536)], places=1)

if __name__ == '__main__':
    unittest2.main()
