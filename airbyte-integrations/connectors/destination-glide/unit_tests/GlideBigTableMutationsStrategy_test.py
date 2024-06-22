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
    def test_set_schema_valid(self, mock_post):
        mock_post.return_value.status_code = 200
        test_columns = [
            Column('id', 'string'),
            Column('name', 'string')
        ]
        self.gbt.set_schema(test_columns)

    @patch.object(requests, 'post')
    def test_set_schema_invalid_column(self, mock_post):
        mock_post.return_value.status_code = 200
        test_columns = [
            Column('id', 'string'),
            Column('this column wont be found', 'string')
        ]
        self.gbt.set_schema(test_columns)
    
    @patch.object(requests, 'post')
    def test_add_rows(self, mock_post):
      test_columns = [
            Column('id', 'string'),
            Column('this column wont be found', 'string')
        ]
      
      mock_post.return_value.status_code = 200
      
      self.gbt.set_schema(test_columns)

      mock_post.reset_mock()
      test_data = [
          {
              'id': '1',
              'col2': 'test name'
          },
          {
              'id': '2',
              'col2': 'test name2'
          }
      ]
      self.gbt.add_rows(test_data)
      self.assertEqual(1, mock_post.call_count)

    @patch.object(requests, 'post')
    def test_add_rows_batch(self, mock_post):
      test_columns = [
            Column('strcol', 'string'),
            Column('numcol', 'number')   
        ]
      
      mock_post.return_value.status_code = 200
      
      self.gbt.set_schema(test_columns)

      mock_post.reset_mock()
      test_rows = list([{"strcol": f"{i}", "numcol": i} for i in range(1000)])
      self.gbt.add_rows(test_rows)

      self.assertEqual(10, mock_post.call_count)  

