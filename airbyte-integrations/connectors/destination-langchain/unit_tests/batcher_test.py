#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock

from destination_langchain.batcher import Batcher


class BatcherTestCase(unittest.TestCase):
    def test_add_single_item(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)

        # Act
        batcher.add(1)

        # Assert
        self.assertFalse(flush_handler_mock.called)

    def test_add_flushes_batch(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)

        # Act
        batcher.add(1)
        batcher.add(2)
        batcher.add(3)

        # Assert
        flush_handler_mock.assert_called_once_with([1, 2, 3])

    def test_flush_empty_buffer(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)

        # Act
        batcher.flush()

        # Assert
        self.assertFalse(flush_handler_mock.called)

    def test_flush_non_empty_buffer(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)
        batcher.add(1)
        batcher.add(2)

        # Act
        batcher.flush()

        # Assert
        flush_handler_mock.assert_called_once_with([1, 2])
        self.assertEqual(len(batcher.buffer), 0)

    def test_flush_if_necessary_flushes_batch(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)
        batcher.add(1)
        batcher.add(2)
        batcher.add(3)

        # Act
        batcher.add(4)
        batcher.add(5)

        # Assert
        flush_handler_mock.assert_called_once_with([1, 2, 3])
        self.assertEqual(len(batcher.buffer), 2)

    def test_flush_if_necessary_does_not_flush_incomplete_batch(self):
        # Arrange
        batch_size = 3
        flush_handler_mock = MagicMock()
        batcher = Batcher(batch_size, flush_handler_mock)
        batcher.add(1)

        # Act
        batcher.add(2)

        # Assert
        self.assertFalse(flush_handler_mock.called)
        self.assertEqual(len(batcher.buffer), 2)
