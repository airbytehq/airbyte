/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.write.LoadStrategy
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class DataChannelBeanFactoryTest {
    @Test
    fun `pipeline input queue is initialized with numInputPartitions partitions`() {
        val queue =
            DataChannelBeanFactory()
                .pipelineInputQueue(
                    numInputPartitions = 2,
                )

        assertEquals(2, queue.partitions)
    }

    @Test
    fun `num input partitions taken from load strategy if file transfer not enabled`() {
        val loadStrategy: LoadStrategy = mockk(relaxed = true)
        every { loadStrategy.inputPartitions } returns 2
        val numInputPartitions =
            DataChannelBeanFactory()
                .numInputPartitions(
                    loadStrategy = loadStrategy,
                    isFileTransfer = false,
                    dataChannelMedium = DataChannelMedium.STDIO,
                    dataChannelSocketPaths = mockk(relaxed = true)
                )

        assertEquals(2, numInputPartitions)
    }

    @Test
    fun `num input partitions is 1 if file transfer enabled`() {
        val loadStrategy: LoadStrategy = mockk(relaxed = true)
        every { loadStrategy.inputPartitions } returns 2
        val numInputPartitions =
            DataChannelBeanFactory()
                .numInputPartitions(
                    loadStrategy = loadStrategy,
                    isFileTransfer = true,
                    dataChannelMedium = DataChannelMedium.STDIO,
                    dataChannelSocketPaths = mockk(relaxed = true)
                )

        assertEquals(1, numInputPartitions)
    }

    @Test
    fun `num input partitions is equal to the number of sockets if sockets enabled`() {
        val loadStrategy: LoadStrategy = mockk(relaxed = true)
        every { loadStrategy.inputPartitions } returns 2
        val numInputPartitions =
            DataChannelBeanFactory()
                .numInputPartitions(
                    loadStrategy = loadStrategy,
                    isFileTransfer = false,
                    dataChannelMedium = DataChannelMedium.SOCKET,
                    dataChannelSocketPaths = (0 until 3).map { "socket.$it" }
                )
        assertEquals(3, numInputPartitions)
    }

    @Test
    fun `num data channels is num_input_partitions if sockets enabled`() {
        val loadStrategy: LoadStrategy = mockk(relaxed = true)
        every { loadStrategy.inputPartitions } returns 2
        val numDataChannels =
            DataChannelBeanFactory()
                .numDataChannels(dataChannelMedium = DataChannelMedium.SOCKET, 3)
        assertEquals(3, numDataChannels)
    }

    @Test
    fun `num data channels always 1 for stdio`() {
        val numDataChannels =
            DataChannelBeanFactory()
                .numDataChannels(
                    dataChannelMedium = DataChannelMedium.STDIO,
                    numInputPartitions = 3
                )
        assertEquals(1, numDataChannels)
    }

    @Test
    fun `require checkpoint key for sockets`() {
        val checkpointKeyRequired =
            DataChannelBeanFactory().requireCheckpointIdOnRecord(DataChannelMedium.SOCKET)
        assertTrue(checkpointKeyRequired)
    }

    @Test
    fun `protobuf only allowed for sockets`() {
        assertThrows<IllegalStateException> {
            DataChannelBeanFactory()
                .dataChannelReader(
                    dataChannelFormat = DataChannelFormat.PROTOBUF,
                    dataChannelMedium = DataChannelMedium.STDIO,
                    destinationMessageFactory = mockk(relaxed = true),
                )
        }
    }
}
