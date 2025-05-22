/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.write.LoadStrategy
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

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
                )

        assertEquals(1, numInputPartitions)
    }

    @Test
    fun `num input partitions is 1 if sockets enabled`() {
        val loadStrategy: LoadStrategy = mockk(relaxed = true)
        every { loadStrategy.inputPartitions } returns 2
        val numInputPartitions =
            DataChannelBeanFactory()
                .numInputPartitions(
                    loadStrategy = loadStrategy,
                    isFileTransfer = false,
                    dataChannelMedium = DataChannelMedium.SOCKETS,
                )
        assertEquals(1, numInputPartitions)
    }
}
