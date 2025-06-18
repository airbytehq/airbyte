/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.object_storage.file

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.file.RouteEventTask
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.util.UUID
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

private val airbyteRawId = UUID.randomUUID()

@ExtendWith(MockKExtension::class)
class RouteEventTaskTest {
    @MockK(relaxed = true) lateinit var fileLoader: ObjectLoader

    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog

    @MockK(relaxed = true)
    lateinit var inputQueue: Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>

    @MockK(relaxed = true)
    lateinit var fileQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>

    @MockK(relaxed = true)
    lateinit var recordQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>

    private val partition = 1

    private val partSizeBytes = 100

    private lateinit var task: RouteEventTask

    @BeforeEach
    fun setup() {
        every { fileLoader.partSizeBytes } returns partSizeBytes.toLong()

        task =
            RouteEventTask(
                catalog,
                inputQueue,
                fileQueue,
                recordQueue,
                partition,
            )
    }

    @Test
    fun `routes messages for streams with includes files to file queue and populates context`() =
        runTest {
            val stream = Fixtures.stream(includeFiles = true)
            val key = StreamKey(stream.descriptor)
            val record = Fixtures.record()
            val checkpoints = mapOf(CheckpointId("1") to CheckpointValue(2, 2))
            val releaseMemCallback: (suspend () -> Unit) = mockk(relaxed = true)

            val input =
                PipelineMessage(
                    checkpointCounts = checkpoints,
                    key = key,
                    value = record,
                    postProcessingCallback = releaseMemCallback,
                )
            every { catalog.getStream(key.stream) } returns stream

            task.handleEvent(input)

            val expectedContext =
                PipelineContext(
                    mapOf(CheckpointId("1") to CheckpointValue(2, 2)),
                    record,
                )

            val expected =
                PipelineMessage(
                    checkpointCounts = checkpoints,
                    key = key,
                    value = Fixtures.record(),
                    postProcessingCallback = releaseMemCallback,
                    context = expectedContext
                )

            coVerify { fileQueue.publish(expected, partition) }
            coVerify { releaseMemCallback() }
        }

    @Test
    fun `routes end of stream for streams with includes files to file queue`() = runTest {
        val stream = Fixtures.stream(includeFiles = true)
        val key = StreamKey(Fixtures.unmappedDescriptor)

        val input = PipelineEndOfStream<StreamKey, DestinationRecordRaw>(stream.descriptor)
        every { catalog.getStream(key.stream) } returns stream

        task.handleEvent(input)

        coVerify { fileQueue.publish(input, partition) }
    }

    @Test
    fun `routes messages for non-file streams to record queue`() = runTest {
        val stream = Fixtures.stream(includeFiles = false)
        val key = StreamKey(stream.descriptor)
        val record = Fixtures.record()
        val checkpoints = mapOf(CheckpointId("1") to CheckpointValue(2, 2))

        val input =
            PipelineMessage(
                checkpointCounts = checkpoints,
                key = key,
                value = record,
            )
        every { catalog.getStream(key.stream) } returns stream

        task.handleEvent(input)

        coVerify { recordQueue.publish(input, partition) }
    }

    @Test
    fun `routes end of stream for non-file streams to record queue`() = runTest {
        val stream = Fixtures.stream(includeFiles = false)
        val key = StreamKey(Fixtures.unmappedDescriptor)

        val input = PipelineEndOfStream<StreamKey, DestinationRecordRaw>(stream.descriptor)
        every { catalog.getStream(key.stream) } returns stream

        task.handleEvent(input)

        coVerify { recordQueue.publish(input, partition) }
    }

    @Test
    fun `broadcasts heartbeats to record queue`() = runTest {
        val input = PipelineHeartbeat<StreamKey, DestinationRecordRaw>()

        task.handleEvent(input)

        coVerify { recordQueue.broadcast(input) }
    }

    object Fixtures {
        val unmappedDescriptor = DestinationStream.Descriptor("namespace-1", "name-1")

        private fun message() =
            AirbyteMessage()
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("""{"something": "has to give"}"""))
                )

        private fun schema() =
            ObjectType(
                properties =
                    LinkedHashMap(mapOf("something" to FieldType(StringType, nullable = true)))
            )

        fun stream(includeFiles: Boolean = true, schema: ObjectType = schema()) =
            DestinationStream(
                unmappedNamespace = unmappedDescriptor.namespace,
                unmappedName = unmappedDescriptor.name,
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 3,
                schema = schema,
                includeFiles = includeFiles,
                namespaceMapper = NamespaceMapper()
            )

        fun record(message: AirbyteMessage = message(), stream: DestinationStream = stream()) =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(message),
                serializedSizeBytes = 0L,
                airbyteRawId = airbyteRawId,
            )
    }
}
