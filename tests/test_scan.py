import sys
sys.path.append('util')

import unittest2
import scan


class testScan(unittest2.TestCase):
    def setUp(self):
        pass

    def test_getQuads(self):

        box1 = scan.getQuads([65536, 65171, 65900, 65536])
        box2 = scan.getQuads((27186, 49587, 27229, 49631))

        self.assertAlmostEqual(box1, [(65536, 65171, 65718.0, 65353.0), (65718.0, 65171, 65900, 65353.0), (65536, 65353.0, 65718.0, 65536), (65718.0, 65353.0, 65900, 65536)], places=1)
        self.assertAlmostEqual(box2, [(27186, 49587, 27207.0, 49609.0), (27207.0, 49587, 27229, 49609.0), (27186, 49609.0, 27207.0, 49631), (27207.0, 49609.0, 27229, 49631)], places=1)

if __name__ == '__main__':
    unittest2.main()
