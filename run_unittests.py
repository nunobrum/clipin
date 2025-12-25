import unittest

loader = unittest.defaultTestLoader.discover('tests')
result = unittest.TextTestRunner(verbosity=2).run(loader)
if not result.wasSuccessful():
    raise SystemExit(1)

