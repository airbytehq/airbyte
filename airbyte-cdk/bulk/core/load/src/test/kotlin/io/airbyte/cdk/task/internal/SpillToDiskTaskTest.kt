/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.data.NullValue
import io.airbyte.cdk.file.MockTempFileProvider
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueSupplier
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.airbyte.cdk.state.FlushStrategy
import io.airbyte.cdk.state.MemoryManager
import io.airbyte.cdk.state.Reserved
import io.airbyte.cdk.task.MockTaskLauncher
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "SpillToDiskTaskTest",
            "MockDestinationConfiguration",
            "MockDestinationCatalog",
            "MockTempFileProvider",
            "MockTaskLauncher",
        ]
)
class SpillToDiskTaskTest {
    @Inject lateinit var memoryManager: MemoryManager
    @Inject lateinit var spillToDiskTaskFactory: DefaultSpillToDiskTaskFactory
    @Inject lateinit var mockTempFileProvider: MockTempFileProvider
    @Inject
    lateinit var queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>

    @Singleton
    @Primary
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockFlushStrategy : FlushStrategy {
        override suspend fun shouldFlush(
            stream: DestinationStream,
            rangeRead: Range<Long>,
            bytesProcessed: Long
        ): Boolean {
            return bytesProcessed >= 1024
        }
    }

    private suspend fun primeMessageQueue(): Long {
        val queue = queueSupplier.get(stream1.descriptor)
        val maxRecords = ((1024 * 1.5) / 8).toLong()
        var recordsWritten = 0L
        var bytesReserved = 0L
        while (recordsWritten < maxRecords) {
            val index = recordsWritten++
            bytesReserved++
            queue.publish(
                memoryManager.reserveBlocking(
                    1L,
                    StreamRecordWrapped(
                        index = index,
                        sizeBytes = 8,
                        record =
                            DestinationRecord(
                                stream = stream1.descriptor,
                                data = NullValue,
                                emittedAtMs = 0,
                                meta = null,
                                serialized = "test${index}"
                            )
                    )
                )
            )
        }
        queue.publish(memoryManager.reserveBlocking(0L, StreamCompleteWrapped(index = maxRecords)))
        return bytesReserved
    }

    @Test
    fun testSpillToDiskTask() = runTest {
        val availableMemory = memoryManager.remainingMemoryBytes
        val bytesReserved = primeMessageQueue()
        Assertions.assertEquals(availableMemory - bytesReserved, memoryManager.remainingMemoryBytes)

        val mockTaskLauncher = MockTaskLauncher()
        spillToDiskTaskFactory.make(mockTaskLauncher, stream1).execute()
        Assertions.assertEquals(1, mockTaskLauncher.spilledFiles.size)
        spillToDiskTaskFactory.make(mockTaskLauncher, stream1).execute()
        Assertions.assertEquals(2, mockTaskLauncher.spilledFiles.size)

        Assertions.assertEquals(1024, mockTaskLauncher.spilledFiles[0].batch.totalSizeBytes)
        Assertions.assertEquals(512, mockTaskLauncher.spilledFiles[1].batch.totalSizeBytes)

        val env1 = mockTaskLauncher.spilledFiles[0]
        val env2 = mockTaskLauncher.spilledFiles[1]
        Assertions.assertEquals(1024, env1.batch.totalSizeBytes)
        Assertions.assertEquals(512, env2.batch.totalSizeBytes)

        val file1 = env1.batch.localFile as MockTempFileProvider.MockLocalFile
        val file2 = env2.batch.localFile as MockTempFileProvider.MockLocalFile
        Assertions.assertTrue(file1.writersCreated[0].isClosed)
        Assertions.assertTrue(file2.writersCreated[0].isClosed)

        val expectedLinesFirst = (0 until 1024 / 8).flatMap { listOf("test$it", "\n") }
        val expectedLinesSecond = (1024 / 8 until 1536 / 8).flatMap { listOf("test$it", "\n") }

        Assertions.assertEquals(expectedLinesFirst, file1.writtenLines)
        Assertions.assertEquals(expectedLinesSecond, file2.writtenLines)

        Assertions.assertEquals(availableMemory, memoryManager.remainingMemoryBytes)
    }
}
