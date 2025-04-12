import unittest
from destination_ragie.config import RagieConfig

class TestRagieConfig(unittest.TestCase):
    def setUp(self):
        # Setup mock config
        # Example: Add the required field
        self.mock_config = RagieConfig(
            api_key="dummy_key",
            batch_size=100,
            content_fields=["field1", "field2"]
        )


    def test_batch_size(self):
        self.assertEqual(self.mock_config.batch_size, 100)

    def test_content_fields(self):
        self.assertEqual(self.mock_config.content_fields, ["field1", "field2"])

if __name__ == '__main__':
    unittest.main()
