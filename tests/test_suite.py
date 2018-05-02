import unittest2

# Import test modules here
import test_tileMath
import test_trainingData
import test_scan

loader = unittest2.TestLoader()
suite = unittest2.TestSuite()

# Add the imported modules to the test suite
suite.addTests(loader.loadTestsFromModule(test_tileMath))
suite.addTest(loader.loadTestsFromModule(test_trainingData))
suite.addTest(loader.loadTestsFromModule(test_scan))


runner = unittest2.TextTestRunner(verbosity=3)
result = runner.run(suite)
