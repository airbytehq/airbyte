from destination_glide.glide import GlideBigTableMutationsStrategy, Column
import requests
import unittest
from unittest.mock import patch

class TestGlideBigTableMutationsStrategy(unittest.TestCase):
    api_host = 'https://test-api-host.com'
    api_key = 'test-api-key'
    api_path_root = '/test/api/path/root'
    table_id = 'test-table-id'

    def setUp(self):
        self.gbt = GlideBigTableMutationsStrategy()
        self.gbt.init(self.api_host, self.api_key,
                      self.api_path_root, self.table_id)
                      
    @patch.object(requests, 'post')
    def test_prepare_table_valid(self, mock_post):
        mock_post.return_value.status_code = 200
        test_columns = [
            Column('id', 'string'),
            Column('name', 'string')
        ]
        self.gbt.prepare_table(test_columns)

    @patch.object(requests, 'post')
    def test_prepare_table_invalid_column(self, mock_post):
        mock_post.return_value.status_code = 200
        test_columns = [
            Column('id', 'string'),
            Column('this column wont be found', 'string')
        ]
        self.gbt.prepare_table(test_columns)

