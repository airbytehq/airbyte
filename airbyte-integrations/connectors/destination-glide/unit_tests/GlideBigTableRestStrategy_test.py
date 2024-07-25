from destination_glide.glide import GlideBigTableRestStrategy, Column
import requests  # for mocking it
import unittest
from unittest import skip
from unittest.mock import patch
import uuid


class TestGlideBigTableRestStrategy(unittest.TestCase):
    api_host = "https://test-api-host.com"
    api_key = "test-api-key"
    api_path_root = "test/api/path/root"
    table_id = ""
    table_name = ""
    stash_id = ""

    test_columns = [
        Column("test-str", "string"),
        Column("test-num", "number")
    ]

    def setUp(self):
        self.table_id = f"test-table-id-{str(uuid.uuid4())}"
        self.table_name = f"test-table-name-{str(uuid.uuid4())}"
        self.stash_id = f"stash-id-{str(uuid.uuid4())}"
        self.gbt = GlideBigTableRestStrategy()
        self.gbt.init(self.api_key, self.table_name, self.api_host, self.api_path_root)

    def mock_post_for_set_schema(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {
                "stashID": self.stash_id
            }
        }

    @patch.object(requests, "post")
    def test_set_schema_valid(self, mock_post):
        self.mock_post_for_set_schema(mock_post)

        test_columns = [
            Column("test-str", "string"),
            Column("test-num", "number")
        ]
        self.gbt.set_schema(test_columns)

        mock_post.assert_called_once()

    @patch.object(requests, "post")
    def test_set_schema_invalid_col_type(self, mock_post):
        self.mock_post_for_set_schema(mock_post)

        with self.assertRaises(ValueError):
            self.gbt.set_schema([
                Column("test-str", "string"),
                Column("test-num", "invalid-type")
            ])

    @patch.object(requests, "post")
    def test_add_rows(self, mock_post):
        self.mock_post_for_set_schema(mock_post)

        self.gbt.set_schema(self.test_columns)
        mock_post.reset_mock()
        test_rows = [
            {"test-str": "one", "test-num": 1},
            {"test-str": "two", "test-num": 2}
        ]
        self.gbt.add_rows(test_rows)

        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.kwargs["json"], test_rows)

    @patch.object(requests, "post")
    def test_add_rows_batching(self, mock_post):
        self.mock_post_for_set_schema(mock_post)

        self.gbt.set_schema(self.test_columns)

        mock_post.reset_mock()
        TEST_ROW_COUNT = 2001
        test_rows = list([
            {"test-str": f"one {i}", "test-num": i}
            for i in range(TEST_ROW_COUNT)
        ])

        self.gbt.add_rows(test_rows)

        self.assertEqual(5, mock_post.call_count)
        # validate that the last row is what we expect:
        self.assertEqual(mock_post.call_args.kwargs["json"],
                         [
            {"test-str": f"one {TEST_ROW_COUNT-1}", "test-num": TEST_ROW_COUNT-1}
        ])

    def test_commit_with_pre_existing_table(self):
        with patch.object(requests, "post") as mock_post:
            self.mock_post_for_set_schema(mock_post)
            self.gbt.set_schema(self.test_columns)
            test_rows = [
                {"test-str": "one", "test-num": 1},
                {"test-str": "two", "test-num": 2}
            ]
            mock_post.reset_mock()
            self.gbt.add_rows(test_rows)

            with patch.object(requests, "get") as mock_get:
                # mock the `GET /tables` response to include the table:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = {
                    "data": [
                        {
                            "name": self.table_name,
                            "id": self.table_id
                        }
                    ]
                }
                mock_post.reset_mock()
                with patch.object(requests, "put") as mock_put:
                    self.gbt.commit()
                    # it should have called put to overwrite a table and NOT called post
                    mock_put.assert_called_once()
                    self.assertEqual(
                        mock_put.call_args.kwargs["json"]["rows"]["$stashID"], self.stash_id)
                    # it should have NOT created a new table via post:
                    mock_post.assert_not_called()

    def test_commit_with_non_existing_table(self):
        # TODO: in a future version, we want to search for the table and if not found, create it. if found, update it (put).
        with patch.object(requests, "post") as mock_post:
            self.mock_post_for_set_schema(mock_post)
            self.gbt.set_schema(self.test_columns)
            test_rows = [
                {"test-str": "one", "test-num": 1},
                {"test-str": "two", "test-num": 2}
            ]
            mock_post.reset_mock()
            self.gbt.add_rows(test_rows)

            with patch.object(requests, "get") as mock_get:
                # mock the `GET /tables` response to include the table:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = {
                    "data": []
                }
                mock_post.reset_mock()
                with patch.object(requests, "put") as mock_put:
                    self.gbt.commit()
                    # it should not have tried to overwrite a table with put
                    mock_put.assert_not_called()
                    self.assertEqual(
                        mock_post.call_args.kwargs["json"]["rows"]["$stashID"], self.stash_id)
                    # it should have created a new table with post:
                    mock_put.assert_not_called()



if __name__ == '__main__':
    unittest.main()
