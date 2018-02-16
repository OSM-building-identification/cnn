import sys
sys.path.append('util')

import unittest2
import db

class TestQueryOSM(unittest2.TestCase):

    def test_queryosm(self):
        buildings = db.queryosm("SELECT ST_AsGeoJSON(geometry) FROM building_polygon where geometry && ST_MakeEnvelope(-105.1, 40, -105.0, 40.1, 4326) LIMIT 1")
        self.assertEqual(buildings, [[u'{"type":"Polygon","coordinates":[[[-105.026979261108,40.0016972661581],[-105.026865183405,40.0018020399478],[-105.02681631691,40.001770943087],[-105.026776754327,40.0018073205468],[-105.02665446236,40.0017292850282],[-105.026808354102,40.0015879661407],[-105.026979261108,40.0016972661581]]]}']])

if __name__=='__main__':
    unittest2.main()
