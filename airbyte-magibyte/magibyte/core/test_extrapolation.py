import unittest

from magibyte.core.extrapolation import extrapolate


class Test(unittest.TestCase):
    def test_extrapolate_const(self):
        self.assertEqual(extrapolate("abc", {}), "abc")

    def test_extrapolate_interpreted_const(self):
        self.assertEqual(extrapolate("{{ 1 }}", {}), "1")

    def test_extrapolate_interpreted_access_context(self):
        self.assertEqual(extrapolate("{{ context.abc }}", {'abc': 'def'}), "def")


if __name__ == '__main__':
    unittest.main()
