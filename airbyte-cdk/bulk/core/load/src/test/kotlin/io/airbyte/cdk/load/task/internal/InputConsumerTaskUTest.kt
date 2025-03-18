/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.implementor.FileTransferQueueMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class InputConsumerTaskUTest {
    @MockK lateinit var catalog: DestinationCatalog
    @MockK lateinit var inputFlow: ReservingDeserializingInputFlow
    @MockK
    lateinit var recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>
    @MockK lateinit var checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>
    @MockK lateinit var syncManager: SyncManager
    @MockK lateinit var destinationTaskLauncher: DestinationTaskLauncher
    @MockK lateinit var fileTransferQueue: MessageQueue<FileTransferQueueMessage>
    @MockK
    lateinit var recordQueueForPipeline:
        PartitionedQueue<Reserved<PipelineEvent<StreamKey, DestinationRecordRaw>>>
    @MockK lateinit var partitioner: InputPartitioner
    @MockK lateinit var openStreamQueue: QueueWriter<DestinationStream>

    private val stream = DestinationStream.Descriptor("namespace", "name")

    private fun createTask(loadPipeline: LoadPipeline?) =
        DefaultInputConsumerTask(
            catalog,
            inputFlow,
            recordQueueSupplier,
            checkpointQueue,
            syncManager,
            destinationTaskLauncher,
            fileTransferQueue,
            recordQueueForPipeline,
            loadPipeline,
            partitioner,
            openStreamQueue
        )

    @BeforeEach
    fun setup() {
        val dstream = mockk<DestinationStream>(relaxed = true)
        every { dstream.descriptor } returns stream
        coEvery { catalog.streams } returns listOf(dstream)
        coEvery { recordQueueSupplier.get(stream) } returns mockk(relaxed = true)
        coEvery { fileTransferQueue.close() } returns Unit
        coEvery { recordQueueForPipeline.close() } returns Unit
        coEvery { openStreamQueue.close() } returns Unit
        coEvery { checkpointQueue.close() } returns Unit
    }

    @Test
    fun `input consumer does not use the new path when there is no load pipeline`() = runTest {
        val inputConsumerTask = createTask(null)

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector: FlowCollector<Pair<Long, Reserved<DestinationMessage>>> = firstArg()
                collector.emit(
                    Pair(
                        0L,
                        Reserved(
                            null,
                            0,
                            DestinationRecord(
                                stream = stream,
                                message = mockk(relaxed = true),
                                serialized = "",
                                schema = ObjectTypeWithoutSchema
                            )
                        )
                    )
                )
                val job = launch { inputConsumerTask.execute() }
                job.join()
                coVerify { recordQueueSupplier.get(stream) }
                coVerify(exactly = 0) { recordQueueForPipeline.publish(any(), any()) }
            }
    }

    @Test
    fun `input consumer uses the new path when there is a load pipeline`(): Unit = runTest {
        val inputConsumerTask = createTask(mockk(relaxed = true))

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector: FlowCollector<Pair<Long, Reserved<DestinationMessage>>> = firstArg()
                collector.emit(
                    Pair(
                        0L,
                        Reserved(
                            null,
                            0,
                            DestinationRecord(
                                stream = stream,
                                message = mockk(relaxed = true),
                                serialized = "",
                                schema = ObjectTypeWithoutSchema
                            )
                        )
                    )
                )
                val job = launch { inputConsumerTask.execute() }
                job.join()
                coVerify(exactly = 0) { recordQueueSupplier.get(stream) }
                coVerify { recordQueueForPipeline.publish(any(), any()) }
            }
    }
}
