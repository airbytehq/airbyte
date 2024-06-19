import unittest
from unittest.mock import patch
import requests  # for mocking it
from destination_glide.glide import GlideBigTableRestStrategy, Column


class TestGlideBigTableRestStrategy(unittest.TestCase):

    api_host = 'https://test-api-host.com'
    api_key = 'test-api-key'
    api_path_root = '/test/api/path/root'
    table_id = 'test-table-id'

    def setUp(self):
        self.gbt = GlideBigTableRestStrategy()
        self.gbt.init(self.api_host, self.api_key,
                      self.api_path_root, self.table_id)

    @patch.object(requests, 'put')
    def test_prepare_table_valid(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {'data': 'test'}

        test_columns = [
            Column('test-str', 'string'),
            Column('test-num', 'number')
        ]
        self.gbt.prepare_table(test_columns)

        mock_put.assert_called_once()
        self.assertListEqual(mock_put.call_args[1]['json']['schema']['columns'], test_columns)

    @patch.object(requests, 'put')
    def test_prepare_table_invalid_col_type(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {'data': 'test'}

        with self.assertRaises(ValueError):
            self.gbt.prepare_table([
                Column('test-str', 'string'),
                Column('test-num', 'invalid-type')
            ])

    @patch.object(requests, 'post')
    def test_add_rows(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'data': 'test'}

        test_rows = [
            Column('strcol', "string"),
            Column('numcol', "number")
        ]
        self.gbt.add_rows(test_rows)

        mock_post.assert_called_once()
        assert mock_post.call_args[1]['json']['rows'] == test_rows


if __name__ == '__main__':
    unittest.main()
