import sys
sys.path.append('util')

import unittest2

# Whatever is being tested
import trainingData


class TestNAIP(unittest2.TestCase):
    def setUp(self):
        pass

    def test_no_building(self):
        self.assertEqual(trainingData.no_building(27325, 49729), False)
        self.assertEqual(trainingData.no_building(27504, 49783), True)
        self.assertEqual(trainingData.no_building(27486, 49800), True)
        self.assertEqual(trainingData.no_building(27296, 49777), True)
        self.assertEqual(trainingData.no_building(27325, 49729), False)
        

if __name__=='__main__':
    unittest2.main()
