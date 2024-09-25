/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DefaultWriteConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.WriteConfiguration
import io.airbyte.cdk.data.NullValue
import io.airbyte.cdk.file.FileReader
import io.airbyte.cdk.file.FileWriter
import io.airbyte.cdk.file.LocalFile
import io.airbyte.cdk.file.TempFileProvider
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueReader
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.nio.file.Path
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["SpillToDiskTaskTest"])
class SpillToDiskTaskTest {
    @Inject lateinit var taskRunner: TaskRunner
    @Inject lateinit var spillToDiskTaskFactory: DefaultSpillToDiskTaskFactory
    @Inject lateinit var mockTempFileProvider: MockTempFileProvider

    @Singleton
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockTempFileProvider : TempFileProvider {
        data class MockFile(
            val path: Path,
            val lines: MutableList<String> = mutableListOf(),
            val isDeleted: Boolean = false,
        )
        private val tmpFileCounter = AtomicInteger(0)
        val writerClosed = AtomicBoolean(false)
        val mockFiles = mutableMapOf<String, MockFile>()
        override fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile {
            val path =
                Path.of(
                    directory.toString(),
                    "/${prefix}-${tmpFileCounter.getAndIncrement()}${suffix}"
                )
            return object : LocalFile {
                override fun toFileWriter(): FileWriter {
                    val mockFile = MockFile(path)
                    mockFiles[path.toString()] = mockFile

                    return object : FileWriter {
                        override fun write(str: String) {
                            mockFile.lines.add(str)
                        }

                        override fun close() {
                            writerClosed.set(true)
                        }
                    }
                }

                override fun toFileReader(): FileReader {
                    throw NotImplementedError()
                }

                override fun delete() {
                    throw NotImplementedError()
                }
            }
        }
    }

    // TODO: Migrate this to a common mock.
    class MockTaskLauncher(override val taskRunner: TaskRunner) : DestinationTaskLauncher {
        val spilledFiles = mutableListOf<BatchEnvelope<SpilledRawMessagesLocalFile>>()

        override suspend fun handleSetupComplete() {
            throw NotImplementedError()
        }

        override suspend fun handleStreamOpen(streamLoader: StreamLoader) {
            throw NotImplementedError()
        }

        override suspend fun handleNewSpilledFile(
            stream: DestinationStream,
            wrapped: BatchEnvelope<SpilledRawMessagesLocalFile>
        ) {
            spilledFiles.add(wrapped)
        }

        override suspend fun handleNewBatch(streamLoader: StreamLoader, wrapped: BatchEnvelope<*>) {
            throw NotImplementedError()
        }

        override suspend fun handleStreamClosed(stream: DestinationStream) {
            throw NotImplementedError()
        }

        override suspend fun handleTeardownComplete() {
            throw NotImplementedError()
        }

        override suspend fun start() {
            throw NotImplementedError()
        }
    }

    @Factory
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockDestinationTaskLauncherFactory {
        @Singleton
        fun mockDestinationTaskLauncher(taskRunner: TaskRunner): DestinationTaskLauncher {
            return MockTaskLauncher(taskRunner)
        }
    }

    @Singleton
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockWriteConfiguration : DefaultWriteConfiguration(), WriteConfiguration {
        override val recordBatchSizeBytes: Long = 1024L
        override val tmpFileDirectory: Path = Path.of("/tmp-test")
        override val firstStageTmpFilePrefix: String = "spilled"
        override val firstStageTmpFileSuffix: String = ".jsonl"
    }

    @Singleton
    @Requires(env = ["SpillToDiskTaskTest"])
    class MockQueueReader : MessageQueueReader<DestinationStream, DestinationRecordWrapped> {
        // Make enough records for a full batch + half a batch
        private val maxRecords = ((1024 * 1.5) / 8).toLong()
        private val recordsWritten = AtomicLong(0)
        override suspend fun readChunk(
            key: DestinationStream,
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
                                stream = stream1,
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
        Assertions.assertTrue(mockTempFileProvider.writerClosed.get())
        Assertions.assertEquals(2, mockTempFileProvider.mockFiles.size)

        val expectedLinesFirst = (0 until 1024 / 8).flatMap { listOf("test$it", "\n") }
        val expectedLinesSecond = (1024 / 8 until 1536 / 8).flatMap { listOf("test$it", "\n") }

        Assertions.assertEquals(
            expectedLinesFirst,
            mockTempFileProvider.mockFiles.values.first().lines
        )
        Assertions.assertEquals(
            expectedLinesSecond,
            mockTempFileProvider.mockFiles.values.last().lines
        )
    }
}
