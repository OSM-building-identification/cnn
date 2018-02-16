import unittest2

# Import test modules here
import test_naip
import test_trainingData
import test_scan
import test_queryosm

loader = unittest2.TestLoader()
suite = unittest2.TestSuite()

# Add the imported modules to the test suite
suite.addTests(loader.loadTestsFromModule(test_naip))
suite.addTest(loader.loadTestsFromModule(test_trainingData))
suite.addTest(loader.loadTestsFromModule(test_scan))
suite.addTest(loader.loadTestsFromModule(test_queryosm))


runner = unittest2.TextTestRunner(verbosity=3)
result = runner.run(suite)
