/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.MockDestinationConfiguration
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.file.DefaultSpillFileProvider
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.DestinationStreamEventQueue
import io.airbyte.cdk.load.message.DestinationStreamQueueSupplier
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamCompleteEvent
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.TimeWindowTrigger
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.MockTaskLauncher
import io.airbyte.cdk.load.test.util.StubDestinationMessageFactory
import io.airbyte.cdk.load.util.lineSequence
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.time.Clock
import kotlin.io.path.inputStream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

class SpillToDiskTaskTest {
    /** Validates task delegates to dependencies as expected. Does not test dependency behavior. */
    @Nested
    @ExtendWith(MockKExtension::class)
    inner class UnitTests {
        @MockK(relaxed = true) lateinit var spillFileProvider: SpillFileProvider

        @MockK(relaxed = true) lateinit var flushStrategy: FlushStrategy

        @MockK(relaxed = true) lateinit var taskLauncher: DestinationTaskLauncher

        @MockK(relaxed = true) lateinit var timeWindow: TimeWindowTrigger

        @MockK(relaxed = true) lateinit var diskManager: ReservationManager

        private lateinit var inputQueue: DestinationStreamEventQueue

        private lateinit var task: DefaultSpillToDiskTask

        @BeforeEach
        fun setup() {
            inputQueue = DestinationStreamEventQueue()
            task =
                DefaultSpillToDiskTask(
                    spillFileProvider,
                    inputQueue,
                    flushStrategy,
                    MockDestinationCatalogFactory.stream1.descriptor,
                    taskLauncher,
                    diskManager,
                    timeWindow,
                )
        }


        @Test
        fun `publishes 'spilled file' aggregates according to time window on stream flush event`() =
            runTest {

//                val timeWindow = TimeWindowTrigger(Clock.systemUTC(), 0)
//            task =
//                DefaultSpillToDiskTask(
//                    spillFileProvider,
//                    inputQueue,
//                    flushStrategy,
//                    MockDestinationCatalogFactory.stream1.descriptor,
//                    taskLauncher,
//                    diskManager,
//                    timeWindow,
//                )

                // flush strategy returns false, so it won't flush
                coEvery { flushStrategy.shouldFlush(any(), any(), any()) } returns false
                coEvery { timeWindow.isComplete() } returns true

                val flushMsg = StreamFlushEvent(101L)
                val recordMsg =
                    StreamRecordEvent(
                        3L,
                        2L,
                        StubDestinationMessageFactory.makeRecord(
                            MockDestinationCatalogFactory.stream1,
                            "test 3",
                        ),
                    )

                // must publish 1 record message so range isn't empty
                inputQueue.publish(Reserved(value = recordMsg))
                inputQueue.publish(Reserved(value = flushMsg))

                task.execute()
                coVerify(exactly = 1) { taskLauncher.handleNewSpilledFile(any(), any()) }
            }

        @Test
        fun `publishes 'spilled file' aggregates according to flush strategy on stream record`() =
            runTest {
                val recordMsg =
                    StreamRecordEvent(
                        3L,
                        2L,
                        StubDestinationMessageFactory.makeRecord(
                            MockDestinationCatalogFactory.stream1,
                            "test 3",
                        ),
                    )
                // flush strategy returns true, so we flush
                coEvery { flushStrategy.shouldFlush(any(), any(), any()) } returns true
                inputQueue.publish(Reserved(value = recordMsg))

                task.execute()
                coVerify(exactly = 1) { taskLauncher.handleNewSpilledFile(any(), any()) }
            }

        @Test
        fun `publishes 'spilled file' aggregates on stream complete event`() = runTest {
            val completeMsg = StreamCompleteEvent(0L)
            inputQueue.publish(Reserved(value = completeMsg))

            task.execute()
            coVerify(exactly = 1) { taskLauncher.handleNewSpilledFile(any(), any()) }
        }

    }

    /**
     * Validates end to end behaviors including those of dependencies. Also exercises the factory.
     */
    @Nested
    inner class EndToEndTests {
        private lateinit var memoryManager: ReservationManager
        private lateinit var diskManager: ReservationManager
        private lateinit var spillToDiskTaskFactory: DefaultSpillToDiskTaskFactory
        private lateinit var taskLauncher: MockTaskLauncher
        private val clock: Clock = mockk(relaxed = true)
        private val flushWindowMs = 60000L

        private lateinit var queueSupplier:
            MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>
        private lateinit var spillFileProvider: SpillFileProvider

        @BeforeEach
        fun setup() {
            spillFileProvider = DefaultSpillFileProvider(MockDestinationConfiguration())
            queueSupplier =
                DestinationStreamQueueSupplier(
                    MockDestinationCatalogFactory().make(),
                )
            taskLauncher = MockTaskLauncher()
            memoryManager = ReservationManager(Fixtures.INITIAL_MEMORY_CAPACITY)
            diskManager = ReservationManager(Fixtures.INITIAL_DISK_CAPACITY)
            spillToDiskTaskFactory =
                DefaultSpillToDiskTaskFactory(
                    spillFileProvider,
                    queueSupplier,
                    MockFlushStrategy(),
                    diskManager,
                    clock,
                    flushWindowMs,
                )
        }

        @Test
        fun `writes aggregates to files and manages disk and memory reservations`() = runTest {
            val messageCount = primeMessageQueue()
            val bytesReservedMemory = Fixtures.MEMORY_RESERVATION_SIZE_BYTES * messageCount
            val bytesReservedDisk = Fixtures.SERIALIZED_SIZE_BYTES * messageCount

            // memory manager has reserved bytes for messages
            Assertions.assertEquals(
                Fixtures.INITIAL_MEMORY_CAPACITY - bytesReservedMemory,
                memoryManager.remainingCapacityBytes,
            )
            // disk manager has not reserved any bytes
            Assertions.assertEquals(
                Fixtures.INITIAL_DISK_CAPACITY,
                diskManager.remainingCapacityBytes,
            )

            spillToDiskTaskFactory
                .make(taskLauncher, MockDestinationCatalogFactory.stream1.descriptor)
                .execute()
            Assertions.assertEquals(1, taskLauncher.spilledFiles.size)
            spillToDiskTaskFactory
                .make(taskLauncher, MockDestinationCatalogFactory.stream1.descriptor)
                .execute()
            Assertions.assertEquals(2, taskLauncher.spilledFiles.size)

            Assertions.assertEquals(1024, taskLauncher.spilledFiles[0].totalSizeBytes)
            Assertions.assertEquals(512, taskLauncher.spilledFiles[1].totalSizeBytes)

            val spilled1 = taskLauncher.spilledFiles[0]
            val spilled2 = taskLauncher.spilledFiles[1]
            Assertions.assertEquals(1024, spilled1.totalSizeBytes)
            Assertions.assertEquals(512, spilled2.totalSizeBytes)

            val file1 = spilled1.localFile
            val file2 = spilled2.localFile

            val expectedLinesFirst = (0 until 1024 / 8).flatMap { listOf("test$it") }
            val expectedLinesSecond = (1024 / 8 until 1536 / 8).flatMap { listOf("test$it") }

            Assertions.assertEquals(
                expectedLinesFirst,
                file1.inputStream().lineSequence().toList(),
            )
            Assertions.assertEquals(
                expectedLinesSecond,
                file2.inputStream().lineSequence().toList(),
            )

            // we have released all memory reservations
            Assertions.assertEquals(
                Fixtures.INITIAL_MEMORY_CAPACITY,
                memoryManager.remainingCapacityBytes,
            )
            // we now have equivalent disk reservations
            Assertions.assertEquals(
                Fixtures.INITIAL_DISK_CAPACITY - bytesReservedDisk,
                diskManager.remainingCapacityBytes,
            )

            file1.toFile().delete()
            file2.toFile().delete()
        }

        inner class MockFlushStrategy : FlushStrategy {
            override suspend fun shouldFlush(
                stream: DestinationStream.Descriptor,
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
                        StreamRecordEvent(
                            index = index,
                            sizeBytes = Fixtures.SERIALIZED_SIZE_BYTES,
                            record =
                                DestinationRecord(
                                    stream = MockDestinationCatalogFactory.stream1.descriptor,
                                    data = NullValue,
                                    emittedAtMs = 0,
                                    meta = null,
                                    serialized = "test${index}",
                                ),
                        ),
                    ),
                )
            }
            queue.publish(
                memoryManager.reserve(
                    0L,
                    StreamCompleteEvent(index = maxRecords),
                ),
            )
            return recordsWritten
        }
    }

    object Fixtures {
        const val INITIAL_DISK_CAPACITY = 100000L
        const val INITIAL_MEMORY_CAPACITY = 200000L

        const val SERIALIZED_SIZE_BYTES = 8L
        const val MEMORY_RESERVATION_SIZE_BYTES = 10L
    }
}
