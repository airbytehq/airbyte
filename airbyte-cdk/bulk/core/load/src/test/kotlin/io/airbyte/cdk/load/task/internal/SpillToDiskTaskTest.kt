/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.MockDestinationConfiguration
import io.airbyte.cdk.load.file.DefaultSpillFileProvider
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.DestinationRecordSerialized
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.DestinationStreamEventQueue
import io.airbyte.cdk.load.message.DestinationStreamQueueSupplier
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.StreamEndEvent
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.TimeWindowTrigger
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.MockTaskLauncher
import io.airbyte.cdk.load.task.implementor.FileAggregateMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.time.Clock
import kotlinx.coroutines.launch
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
        @MockK(relaxed = true) lateinit var fileAccumulatorFactory: FileAccumulatorFactory

        @MockK(relaxed = true) lateinit var flushStrategy: FlushStrategy

        @MockK(relaxed = true) lateinit var taskLauncher: DestinationTaskLauncher

        @MockK(relaxed = true) lateinit var timeWindow: TimeWindowTrigger

        @MockK(relaxed = true) lateinit var diskManager: ReservationManager

        @MockK(relaxed = true) lateinit var outputQueue: MultiProducerChannel<FileAggregateMessage>

        private lateinit var inputQueue: DestinationStreamEventQueue

        private lateinit var task: DefaultSpillToDiskTask

        @BeforeEach
        fun setup() {
            val acc =
                FileAccumulator(
                    mockk(),
                    mockk(),
                    timeWindow,
                )
            every { fileAccumulatorFactory.make() } returns acc
            inputQueue = DestinationStreamEventQueue()
            task =
                DefaultSpillToDiskTask(
                    fileAccumulatorFactory,
                    inputQueue,
                    outputQueue,
                    flushStrategy,
                    MockDestinationCatalogFactory.stream1.descriptor,
                    diskManager,
                    taskLauncher,
                    false,
                )
        }

        @Test
        fun `publishes 'spilled file' aggregates according to flush strategy on stream record`() =
            runTest {
                val recordMsg =
                    StreamRecordEvent(
                        3L,
                        2L,
                        DestinationRecordSerialized(
                            MockDestinationCatalogFactory.stream1.descriptor,
                            ""
                        )
                    )
                // flush strategy returns true, so we flush
                coEvery { flushStrategy.shouldFlush(any(), any(), any()) } returns true
                inputQueue.publish(Reserved(value = recordMsg))

                val job = launch {
                    task.execute()
                    coVerify(exactly = 1) { outputQueue.publish(any()) }
                }
                job.cancel()
            }

        @Test
        fun `publishes 'spilled file' aggregates on stream complete event`() = runTest {
            val completeMsg = StreamEndEvent(0L)
            inputQueue.publish(Reserved(value = completeMsg))

            val job = launch {
                task.execute()
                coVerify(exactly = 1) { outputQueue.publish(any()) }
            }
            job.cancel()
        }

        @Test
        fun `publishes 'spilled file' aggregates according to time window on stream flush event`() =
            runTest {
                // flush strategy returns false, so it won't flush
                coEvery { flushStrategy.shouldFlush(any(), any(), any()) } returns false
                every { timeWindow.isComplete() } returns true

                val flushMsg = StreamFlushEvent(101L)
                val recordMsg =
                    StreamRecordEvent(
                        3L,
                        2L,
                        DestinationRecordSerialized(
                            MockDestinationCatalogFactory.stream1.descriptor,
                            ""
                        )
                    )

                // must publish 1 record message so range isn't empty
                inputQueue.publish(Reserved(value = recordMsg))
                inputQueue.publish(Reserved(value = flushMsg))

                val job = launch {
                    task.execute()
                    coVerify(exactly = 1) { outputQueue.publish(any()) }
                }
                job.cancel()
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
        private lateinit var fileAccumulatorFactory: FileAccumulatorFactory
        private val clock: Clock = mockk(relaxed = true)
        private val flushWindowMs = 60000L

        private lateinit var queueSupplier:
            MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>
        private lateinit var spillFileProvider: SpillFileProvider
        private lateinit var outputQueue: MultiProducerChannel<FileAggregateMessage>

        @BeforeEach
        fun setup() {
            outputQueue = mockk(relaxed = true)
            spillFileProvider = DefaultSpillFileProvider(MockDestinationConfiguration())
            queueSupplier =
                DestinationStreamQueueSupplier(
                    MockDestinationCatalogFactory().make(),
                )
            fileAccumulatorFactory = FileAccumulatorFactory(flushWindowMs, spillFileProvider, clock)
            taskLauncher = MockTaskLauncher()
            memoryManager = ReservationManager(Fixtures.INITIAL_MEMORY_CAPACITY)
            diskManager = ReservationManager(Fixtures.INITIAL_DISK_CAPACITY)
            spillToDiskTaskFactory =
                DefaultSpillToDiskTaskFactory(
                    MockDestinationConfiguration(),
                    fileAccumulatorFactory,
                    queueSupplier,
                    MockFlushStrategy(),
                    diskManager,
                    outputQueue,
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

            val job = launch {
                spillToDiskTaskFactory
                    .make(taskLauncher, MockDestinationCatalogFactory.stream1.descriptor)
                    .execute()
                spillToDiskTaskFactory
                    .make(taskLauncher, MockDestinationCatalogFactory.stream1.descriptor)
                    .execute()

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
            }
            job.cancel()
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
                            payload =
                                DestinationRecordSerialized(
                                    MockDestinationCatalogFactory.stream1.descriptor,
                                    "",
                                ),
                        ),
                    ),
                )
            }
            queue.publish(
                memoryManager.reserve(
                    0L,
                    StreamEndEvent(index = maxRecords),
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
