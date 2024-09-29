/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.data.NullValue
import io.airbyte.cdk.file.MockTempFileProvider
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueReader
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.nio.file.Path
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "SpillToDiskTaskTest",
            "MockTempFileProvider",
            "MockTaskLauncher",
        ]
)
class SpillToDiskTaskTest {
    @Inject lateinit var taskRunner: TaskRunner
    @Inject lateinit var spillToDiskTaskFactory: DefaultSpillToDiskTaskFactory
    @Inject lateinit var mockTempFileProvider: MockTempFileProvider

    @Singleton
    @Primary
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockWriteConfiguration : DestinationConfiguration() {
        override val recordBatchSizeBytes: Long = 1024L
        override val tmpFileDirectory: Path = Path.of("/tmp-test")
        override val firstStageTmpFilePrefix: String = "spilled"
        override val firstStageTmpFileSuffix: String = ".jsonl"
    }

    @Singleton
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockQueueReader :
        MessageQueueReader<DestinationStream.Descriptor, DestinationRecordWrapped> {
        // Make enough records for a full batch + half a batch
        private val maxRecords = ((1024 * 1.5) / 8).toLong()
        private val recordsWritten = AtomicLong(0)
        override suspend fun readChunk(
            key: DestinationStream.Descriptor,
            maxBytes: Long
        ): Flow<DestinationRecordWrapped> = flow {
            var totalBytes = 0
            while (recordsWritten.get() < maxRecords) {
                val index = recordsWritten.getAndIncrement()
                emit(
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
                totalBytes += 8
                if (totalBytes >= maxBytes) {
                    return@flow
                }
            }
            emit(StreamCompleteWrapped(index = maxRecords))
        }
    }

    @Test
    fun testSpillToDiskTask() = runTest {
        val mockTaskLauncher = MockTaskLauncher(taskRunner)
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
    }
}
