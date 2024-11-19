/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.MockTaskLauncher
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.coVerify
import io.mockk.mockk
import jakarta.inject.Inject
import java.nio.file.Files
import kotlin.io.path.outputStream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "MockDestinationCatalog",
        ]
)
class ProcessRecordsTaskTest {
    private lateinit var diskManager: ReservationManager
    private lateinit var processRecordsTaskFactory: DefaultProcessRecordsTaskFactory
    private lateinit var launcher: MockTaskLauncher
    @Inject lateinit var syncManager: SyncManager

    @BeforeEach
    fun setup() {
        diskManager = mockk(relaxed = true)
        launcher = MockTaskLauncher()
        processRecordsTaskFactory =
            DefaultProcessRecordsTaskFactory(
                MockDeserializer(),
                syncManager,
                diskManager,
            )
    }

    class MockBatch(
        override val state: Batch.State,
        val reportedByteSize: Long,
        val recordCount: Long,
        val pmChecksum: Long,
    ) : Batch

    class MockStreamLoader : StreamLoader {
        override val stream: DestinationStream = MockDestinationCatalogFactory.stream1

        data class SumAndCount(val sum: Long = 0, val count: Long = 0)

        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long
        ): Batch {
            // Do a simple sum of the record values and count
            // To demonstrate that the primed data was actually processed
            val (sum, count) =
                records.asSequence().fold(SumAndCount()) { acc, record ->
                    SumAndCount(acc.sum + (record.data as IntegerValue).value, acc.count + 1)
                }
            return MockBatch(
                state = Batch.State.COMPLETE,
                reportedByteSize = totalSizeBytes,
                recordCount = count,
                pmChecksum = sum
            )
        }

        override suspend fun processFile(file: DestinationFile): Batch {
            return MockBatch(
                state = Batch.State.COMPLETE,
                reportedByteSize = file.fileMessage.bytes ?: 0,
                recordCount = 1,
                pmChecksum = 1
            )
        }
    }

    class MockDeserializer : Deserializer<DestinationMessage> {
        override fun deserialize(serialized: String): DestinationMessage {
            return DestinationRecord(
                stream = MockDestinationCatalogFactory.stream1.descriptor,
                data = IntegerValue(serialized.toLong()),
                emittedAtMs = 0L,
                meta = null,
                serialized = serialized,
            )
        }
    }

    @Test
    fun testProcessRecordsTask() = runTest {
        val byteSize = 999L
        val recordCount = 1024L

        val mockFile = Files.createTempFile("test", ".jsonl")
        val file =
            SpilledRawMessagesLocalFile(
                localFile = mockFile,
                totalSizeBytes = byteSize,
                indexRange = Range.closed(0, recordCount)
            )
        val task =
            processRecordsTaskFactory.make(
                taskLauncher = launcher,
                stream = MockDestinationCatalogFactory.stream1.descriptor,
                file = file
            )
        mockFile.outputStream().use { outputStream ->
            (0 until recordCount).forEach { outputStream.write("$it\n") }
        }

        syncManager.registerStartedStreamLoader(MockStreamLoader())
        task.execute()

        Assertions.assertEquals(1, launcher.batchEnvelopes.size)
        val batch = launcher.batchEnvelopes[0].batch as MockBatch
        Assertions.assertEquals(Batch.State.COMPLETE, batch.state)
        Assertions.assertEquals(999, batch.reportedByteSize)
        Assertions.assertEquals(recordCount, batch.recordCount)
        Assertions.assertEquals((0 until recordCount).sum(), batch.pmChecksum)
        Assertions.assertFalse(Files.exists(mockFile), "ensure task deleted file")
        coVerify { diskManager.release(byteSize) }
    }
}
