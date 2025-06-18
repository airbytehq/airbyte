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
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.pipline.object_storage.file.ForwardFileRecordTask
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
import java.util.UUID
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ForwardFileRecordTaskTest {
    @MockK(relaxed = true) lateinit var fileLoader: ObjectLoader

    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog

    @MockK(relaxed = true)
    lateinit var inputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<String>>>

    @MockK(relaxed = true)
    lateinit var outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>

    private val partition = 1

    private val partSizeBytes = 100

    private lateinit var task: ForwardFileRecordTask<String>

    @BeforeEach
    fun setup() {
        every { fileLoader.partSizeBytes } returns partSizeBytes.toLong()

        task =
            ForwardFileRecordTask(
                inputQueue,
                outputQueue,
                partition,
            )
    }

    @Test
    fun `forwards end of stream`() = runTest {
        val input =
            PipelineEndOfStream<StreamKey, ObjectLoaderUploadCompleter.UploadResult<String>>(
                Fixtures.unmappedDescriptor
            )
        task.handleEvent(input)

        coVerify { outputQueue.publish(PipelineEndOfStream(input.stream), 0) }
    }

    @Test
    fun `drops heartbeat messages`() = runTest {
        val input = PipelineHeartbeat<StreamKey, ObjectLoaderUploadCompleter.UploadResult<String>>()
        task.handleEvent(input)

        coVerify(exactly = 0) { outputQueue.publish(any(), any()) }
    }

    @Test
    fun `does nothing if the remote object is null (this is an artifact of End of Stream)`() =
        runTest {
            val stream = Fixtures.stream()
            val key = StreamKey(stream.descriptor)
            val context =
                PipelineContext(
                    mapOf(CheckpointId("123") to CheckpointValue(14L, 14L)),
                    Fixtures.record(),
                )
            val result =
                ObjectLoaderUploadCompleter.UploadResult<String>(
                    state = BatchState.LOADED,
                    remoteObject = null
                )
            val input =
                PipelineMessage(
                    checkpointCounts = mapOf(),
                    key = key,
                    value = result,
                    context = context
                )
            task.handleEvent(input)

            coVerify(exactly = 0) { outputQueue.publish(any(), any()) }
        }

    @Test
    fun `extracts record and checkpoints and forwards them when present`() = runTest {
        val stream = Fixtures.stream()
        val key = StreamKey(stream.descriptor)
        val context =
            PipelineContext(
                mapOf(CheckpointId("123") to CheckpointValue(14L, 14L)),
                Fixtures.record(),
            )
        val result =
            ObjectLoaderUploadCompleter.UploadResult(
                state = BatchState.LOADED,
                remoteObject = "uploaded thing"
            )
        val input =
            PipelineMessage(
                checkpointCounts = mapOf(),
                key = key,
                value = result,
                context = context
            )
        task.handleEvent(input)

        val expectedOutput =
            PipelineMessage(
                context.parentCheckpointCounts!!,
                input.key,
                context.parentRecord!!,
            )

        coVerify(exactly = 1) { outputQueue.publish(expectedOutput, 0) }
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
                airbyteRawId = UUID.randomUUID(),
            )
    }
}
