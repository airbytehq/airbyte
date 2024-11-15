/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordWrapped
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamRecordCompleteWrapped
import io.airbyte.cdk.load.message.StreamRecordWrapped
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.MockTaskLauncher
import io.airbyte.cdk.load.util.lineSequence
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.io.path.inputStream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
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
    private lateinit var memoryManager: ReservationManager
    private lateinit var diskManager: ReservationManager
    private lateinit var spillToDiskTaskFactory: DefaultSpillToDiskTaskFactory
    @Inject
    lateinit var queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>
    @Inject
    lateinit var spillFileProvider: SpillFileProvider

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
        val queue = queueSupplier.get(MockDestinationCatalogFactory.stream1.descriptor)
        val maxRecords = ((1024 * 1.5) / 8).toLong()
        var recordsWritten = 0L
        while (recordsWritten < maxRecords) {
            val index = recordsWritten++
            queue.publish(
                memoryManager.reserve(
                    Fixtures.MEMORY_RESERVATION_SIZE_BYTES,
                    StreamRecordWrapped(
                        index = index,
                        sizeBytes = Fixtures.SERIALIZED_SIZE_BYTES,
                        record =
                            DestinationRecord(
                                stream = MockDestinationCatalogFactory.stream1.descriptor,
                                data = NullValue,
                                emittedAtMs = 0,
                                meta = null,
                                serialized = "test${index}"
                            )
                    )
                )
            )
        }
        queue.publish(memoryManager.reserve(0L, StreamRecordCompleteWrapped(index = maxRecords)))
        return recordsWritten
    }

    @BeforeEach
    fun setup() {
        memoryManager = ReservationManager(Fixtures.INITIAL_MEMORY_CAPACITY)
        diskManager = ReservationManager(Fixtures.INITIAL_DISK_CAPACITY)
        spillToDiskTaskFactory = DefaultSpillToDiskTaskFactory(
            spillFileProvider,
            queueSupplier,
            MockFlushStrategy(),
            diskManager,
        )
    }

    @Test
    fun testSpillToDiskTask() = runTest {
        val messageCount = primeMessageQueue()
        val bytesReservedMemory = Fixtures.MEMORY_RESERVATION_SIZE_BYTES * messageCount
        val bytesReservedDisk = Fixtures.SERIALIZED_SIZE_BYTES * messageCount

        // memory manager has reserved bytes for messages
        Assertions.assertEquals(Fixtures.INITIAL_MEMORY_CAPACITY - bytesReservedMemory, memoryManager.remainingCapacityBytes)
        // disk manager has not reserved any bytes
        Assertions.assertEquals(Fixtures.INITIAL_DISK_CAPACITY, diskManager.remainingCapacityBytes)

        val mockTaskLauncher = MockTaskLauncher()
        spillToDiskTaskFactory
            .make(mockTaskLauncher, MockDestinationCatalogFactory.stream1)
            .execute()
        Assertions.assertEquals(1, mockTaskLauncher.spilledFiles.size)
        spillToDiskTaskFactory
            .make(mockTaskLauncher, MockDestinationCatalogFactory.stream1)
            .execute()
        Assertions.assertEquals(2, mockTaskLauncher.spilledFiles.size)

        Assertions.assertEquals(1024, mockTaskLauncher.spilledFiles[0].totalSizeBytes)
        Assertions.assertEquals(512, mockTaskLauncher.spilledFiles[1].totalSizeBytes)

        val spilled1 = mockTaskLauncher.spilledFiles[0]
        val spilled2 = mockTaskLauncher.spilledFiles[1]
        Assertions.assertEquals(1024, spilled1.totalSizeBytes)
        Assertions.assertEquals(512, spilled2.totalSizeBytes)

        val file1 = spilled1.localFile
        val file2 = spilled2.localFile

        val expectedLinesFirst = (0 until 1024 / 8).flatMap { listOf("test$it") }
        val expectedLinesSecond = (1024 / 8 until 1536 / 8).flatMap { listOf("test$it") }

        Assertions.assertEquals(expectedLinesFirst, file1.inputStream().lineSequence().toList())
        Assertions.assertEquals(expectedLinesSecond, file2.inputStream().lineSequence().toList())

        // we have released all memory reservations
        Assertions.assertEquals(Fixtures.INITIAL_MEMORY_CAPACITY, memoryManager.remainingCapacityBytes)
        // we now have equivalent disk reservations
        Assertions.assertEquals(Fixtures.INITIAL_DISK_CAPACITY - bytesReservedDisk, diskManager.remainingCapacityBytes)

        file1.toFile().delete()
        file2.toFile().delete()
    }

    object Fixtures {
        const val INITIAL_DISK_CAPACITY = 100000L
        const val INITIAL_MEMORY_CAPACITY = 200000L

        const val SERIALIZED_SIZE_BYTES = 8L
        const val MEMORY_RESERVATION_SIZE_BYTES = 10L
    }
}
