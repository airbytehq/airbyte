/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class DestinationMessageQueueReaderTest {
    @Inject lateinit var queueReaderFactory: TestDestinationMessageQueueReaderFactory

    @Singleton
    class TestDestinationMessageQueueReaderFactory(val messageQueue: MockMessageQueue) {
        fun make(): DestinationMessageQueueReader {
            return DestinationMessageQueueReader(messageQueue)
        }
    }

    @Test
    fun testReading() = runTest {
        val channel1 = queueReaderFactory.messageQueue.getChannel(stream1)
        val records =
            (0 until 1000).map {
                DestinationRecord(
                    stream = stream1,
                    data = null,
                    emittedAtMs = it * 1000L,
                    serialized = "serialized:$it"
                )
            }
        records.forEachIndexed { index, record ->
            channel1.send(StreamRecordWrapped(index.toLong(), 2L, record))
        }
        channel1.send(StreamCompleteWrapped(1000L))

        val reader = queueReaderFactory.make()

        reader
            .readChunk(stream1, 1200)
            .map { (it as StreamRecordWrapped).record }
            .toList()
            .also {
                Assertions.assertEquals(600, it.size)
                Assertions.assertEquals(records.take(600), it)
            }

        reader.readChunk(stream1, 2000).toList().also { it ->
            Assertions.assertEquals(401, it.size)
            val actualRecords = it.take(400).map { (it as StreamRecordWrapped).record }
            Assertions.assertEquals(records.subList(600, 1000), actualRecords)
            Assertions.assertEquals(it.last(), StreamCompleteWrapped(1000L))
        }
    }

    @Test
    fun testReadingEmptyStreamBlocksUntilChannelFull() = runTest {
        val channel1 = queueReaderFactory.messageQueue.getChannel(stream1)
        val reader = queueReaderFactory.make()
        val checkpoint = Channel<Unit>(Channel.UNLIMITED)

        val job = launch {
            reader.readChunk(stream1, 1200).toList()
            checkpoint.send(Unit)
        }

        delay(100L)
        Assertions.assertNull(checkpoint.tryReceive().getOrNull())
        channel1.send(
            StreamRecordWrapped(0, 1200L, DestinationRecord(stream1, null, 0, "serialized:0"))
        )
        withTimeout(5000L) { job.join() }
    }

    @Test
    fun testReadingInsufficientStreamBlockesUntilEndOfStream() = runTest {
        val channel1 = queueReaderFactory.messageQueue.getChannel(stream1)
        val reader = queueReaderFactory.make()
        val checkpoint = Channel<Unit>(Channel.UNLIMITED)

        channel1.send(
            StreamRecordWrapped(0, 1199L, DestinationRecord(stream1, null, 0, "serialized:0"))
        )
        val job = launch {
            reader.readChunk(stream1, 1200).toList()
            checkpoint.send(Unit)
        }

        delay(100L)
        Assertions.assertNull(checkpoint.tryReceive().getOrNull())
        channel1.send(StreamCompleteWrapped(1))
        withTimeout(5000L) { job.join() }
    }
}
