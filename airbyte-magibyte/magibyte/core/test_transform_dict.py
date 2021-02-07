import unittest

from magibyte.core.transform_dict import TransformDict


class TestTransformDict(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(TransformDict({1: 1}), {1: 1})

    def test_transform(self):
        transform_dict = TransformDict({1: 1}, lambda x: x + 1)

        self.assertEqual(transform_dict, {1: 2})
        self.assertEqual(transform_dict[1], 2)
        self.assertEqual(transform_dict.get(1), 2)


if __name__ == '__main__':
    unittest.main()

