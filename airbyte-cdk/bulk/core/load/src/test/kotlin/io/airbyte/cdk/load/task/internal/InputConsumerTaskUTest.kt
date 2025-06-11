/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.util.UUID
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

// TODO merge this class into InputConsumerTaskTest.
//   There are historical reasons that these are separate classes, but those
//   reasons are no longer true.
class InputConsumerTaskUTest {
    @MockK lateinit var catalog: DestinationCatalog
    @MockK lateinit var inputFlow: ReservingDeserializingInputFlow
    @MockK lateinit var checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>
    @MockK lateinit var syncManager: SyncManager
    @MockK lateinit var fileTransferQueue: MessageQueue<FileTransferQueueMessage>
    @MockK
    lateinit var recordQueueForPipeline:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>
    @MockK lateinit var partitioner: InputPartitioner
    @MockK lateinit var openStreamQueue: QueueWriter<DestinationStream>
    @MockK lateinit var pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter

    private val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
    private lateinit var dstream: DestinationStream

    private fun createTask() =
        InputConsumerTask(
            catalog,
            inputFlow,
            recordQueueForPipeline,
            partitioner,
            pipelineEventBookkeepingRouter
        )

    @BeforeEach
    fun setup() {
        dstream = mockk<DestinationStream>(relaxed = true)
        every { dstream.descriptor } returns streamDescriptor
        coEvery { catalog.streams } returns listOf(dstream)
        coEvery { fileTransferQueue.close() } returns Unit
        coEvery { recordQueueForPipeline.close() } returns Unit
        coEvery { openStreamQueue.close() } returns Unit
        coEvery { checkpointQueue.close() } returns Unit
    }

    @Test
    fun `input consumer publishes to the record queue`(): Unit = runTest {
        val inputConsumerTask = createTask()
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
                                stream = dstream,
                                message = mockk(relaxed = true),
                                serializedSizeBytes = 0L,
                                airbyteRawId = UUID.randomUUID()
                            )
                        )
                    )
                )
                val job = launch { inputConsumerTask.execute() }
                job.join()
                coVerify { recordQueueForPipeline.publish(any(), any()) }
            }
    }
}
