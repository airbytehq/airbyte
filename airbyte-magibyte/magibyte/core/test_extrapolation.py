import unittest

from magibyte.core.extrapolation import extrapolate


class Test(unittest.TestCase):
    def test_const(self):
        self.assertEqual(extrapolate("abc", {}), "abc")

    def test_not_string_const(self):
        self.assertEqual(extrapolate(True, {}), True)

    def test_1(self):
        self.assertEqual(extrapolate("{{ 1 }}", {}), "1")

    def test_var(self):
        self.assertEqual(extrapolate("{{ abc }}", {'abc': 'def'}), "def")

    def test_map(self):
        self.assertEqual(extrapolate("{{ abc.def }}", {'abc': {'def': 'ghi'}}), "ghi")

    def test_function(self):
        self.assertEqual(extrapolate("{{ abc.get('not_here', 'ghi') }}", {'abc': {}}), "ghi")

    def test_global_now_local(self):
        self.assertRegex(
            extrapolate("{{ now_local() }}", {}),
            "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\\.[0-9]{6}")

    def test_global_now_utc(self):
        self.assertRegex(
            extrapolate("{{ now_utc() }}", {}),
            "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\\.[0-9]{6}\\+00:00")


if __name__ == '__main__':
    unittest.main()
