/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceAcquirer
import io.mockk.every
import io.mockk.mockk
import java.io.IOException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class CdcPartitionReaderResourceTest {
    private data class Position(val value: Long) : PartiallyOrdered<Position> {
        override fun compareTo(other: Position): Int = value.compareTo(other.value)
    }

    @Test
    fun testReleaseResourcesWhenOutputCloseFails() {
        val concurrencyResource = ConcurrencyResource(1)
        val bootstrap =
            mockk<GlobalFeedBootstrap> {
                every { dataChannelMedium } returns DataChannelMedium.STDIO
                every { dataChannelFormat } returns DataChannelFormat.JSONL
                every { outputConsumer } returns mockk(relaxed = true)
                every { streamRecordConsumers() } returns emptyMap()
            }
        val reader =
            CdcPartitionReader(
                ResourceAcquirer(listOf(concurrencyResource)),
                mockk<CdcPartitionReaderDebeziumOperations<Position>>(),
                Position(1),
                emptyMap(),
                DebeziumOffset(emptyMap()),
                null,
                false,
                bootstrap,
            )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources(),
        )
        Assertions.assertEquals(0, concurrencyResource.available)
        val failure = IOException("Broken pipe")
        reader.outputMessageRouter =
            mockk<OutputMessageRouter> {
                every { close() } throws failure
            }

        Assertions.assertSame(
            failure,
            Assertions.assertThrows(IOException::class.java) { reader.releaseResources() },
        )
        Assertions.assertEquals(1, concurrencyResource.available)
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources(),
        )
        reader.releaseResources()
        Assertions.assertEquals(1, concurrencyResource.available)
    }
}
