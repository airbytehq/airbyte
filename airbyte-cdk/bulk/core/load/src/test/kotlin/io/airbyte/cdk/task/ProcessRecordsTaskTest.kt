/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.data.IntegerValue
import io.airbyte.cdk.file.MockTempFileProvider
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.state.MockSyncManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.nio.file.Path
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "ProcessRecordsTaskTest",
            "MockDestinationCatalog",
            "MockSyncManager",
            "MockTaskLauncher",
        ]
)
class ProcessRecordsTaskTest {
    @Inject lateinit var processRecordsTaskFactory: DefaultProcessRecordsTaskFactory
    @Inject lateinit var launcher: MockTaskLauncher
    @Inject lateinit var syncManager: MockSyncManager

    class MockBatch(
        override val state: Batch.State,
        val reportedByteSize: Long,
        val recordCount: Long,
        val pmChecksum: Long,
    ) : Batch

    class MockStreamLoader : StreamLoader {
        override val stream: DestinationStream = stream1

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
    }

    @Singleton
    @Primary
    @Requires(env = ["ProcessRecordsTaskTest"])
    class MockDeserializer : Deserializer<DestinationMessage> {
        override fun deserialize(serialized: String): DestinationMessage {
            return DestinationRecord(
                stream = stream1.descriptor,
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

        val mockFile =
            MockTempFileProvider()
                .createTempFile(directory = Path.of("tmp/"), prefix = "test", suffix = ".json")
                as MockTempFileProvider.MockLocalFile
        val file =
            SpilledRawMessagesLocalFile(
                localFile = mockFile,
                totalSizeBytes = byteSize,
            )
        val task =
            processRecordsTaskFactory.make(
                taskLauncher = launcher,
                stream = stream1,
                fileEnvelope = BatchEnvelope(file, Range.closed(0, 1024))
            )
        mockFile.linesToRead = (0 until recordCount).map { "$it" }.toMutableList()

        syncManager.mockGetOrAwaitStreamLoader(MockStreamLoader())
        task.execute()

        Assertions.assertEquals(1, launcher.batchEnvelopes.size)
        val batch = launcher.batchEnvelopes[0].batch as MockBatch
        Assertions.assertEquals(Batch.State.COMPLETE, batch.state)
        Assertions.assertEquals(999, batch.reportedByteSize)
        Assertions.assertEquals(recordCount, batch.recordCount)
        Assertions.assertEquals((0 until recordCount).sum(), batch.pmChecksum)
    }
}
