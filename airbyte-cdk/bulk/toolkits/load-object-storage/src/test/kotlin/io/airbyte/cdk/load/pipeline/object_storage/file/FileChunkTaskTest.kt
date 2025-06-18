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
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkTask
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkTask.Companion.COLUMN_NAME_AIRBYTE_FILE_PATH
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkTask.Companion.enrichRecordWithFilePath
import io.airbyte.cdk.load.pipline.object_storage.file.FileHandle
import io.airbyte.cdk.load.pipline.object_storage.file.FileHandleFactory
import io.airbyte.cdk.load.pipline.object_storage.file.UploadIdGenerator
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import java.io.FileInputStream
import java.nio.file.Path
import java.util.UUID
import kotlin.test.assertContains
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class FileChunkTaskTest<T> {
    @MockK(relaxed = true) lateinit var fileLoader: ObjectLoader

    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog

    @MockK(relaxed = true) lateinit var pathFactory: ObjectStoragePathFactory

    @MockK(relaxed = true) lateinit var fileHandleFactory: FileHandleFactory

    @MockK(relaxed = true) lateinit var uploadIdGenerator: UploadIdGenerator

    @MockK(relaxed = true)
    lateinit var inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>

    @MockK(relaxed = true)
    lateinit var partQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>

    @MockK(relaxed = true)
    lateinit var partitioner: ObjectLoaderFormattedPartPartitioner<StreamKey, T>

    private val partition = 1

    private val partSizeBytes = 100

    private lateinit var task: FileChunkTask<T>

    @BeforeEach
    fun setup() {
        every { fileLoader.partSizeBytes } returns partSizeBytes.toLong()

        task =
            FileChunkTask(
                fileLoader,
                catalog,
                pathFactory,
                fileHandleFactory,
                uploadIdGenerator,
                inputQueue,
                partQueue,
                partitioner,
                partition,
            )
    }

    @Test
    fun `forwards end of stream on output queue`() = runTest {
        val input =
            PipelineEndOfStream<StreamKey, DestinationRecordRaw>(Fixtures.unmappedDescriptor)
        task.handleEvent(input)

        val expected =
            PipelineEndOfStream<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>(
                Fixtures.unmappedDescriptor
            )
        coVerify { partQueue.broadcast(eq(expected)) }
    }

    @Test
    fun `drops pipeline heartbeats`() = runTest {
        val input = PipelineHeartbeat<StreamKey, DestinationRecordRaw>()
        task.handleEvent(input)

        coVerify(exactly = 0) { partQueue.broadcast(any()) }
        coVerify(exactly = 0) { partQueue.publish(any(), any()) }
    }

    @Test
    fun `chunks the referenced file into parts, emits them and deletes the local file`() = runTest {
        val key = StreamKey(Fixtures.unmappedDescriptor)
        val record = Fixtures.record()

        every { catalog.getStream(key.stream) } returns Fixtures.stream()

        val bytes1 = ByteArray(partSizeBytes)
        val bytes2 = ByteArray(partSizeBytes)
        val bytes3 = ByteArray(partSizeBytes - 1)

        // TODO: this leaks internals of FilePartIterator — factor out injectable factory as
        // necessary
        // mock the input stream so we emit 3 chunks
        val mockInputStream: FileInputStream = mockk {
            every { readNBytes(partSizeBytes) } returnsMany
                listOf(
                    bytes1,
                    bytes2,
                    bytes3,
                )
            every { close() } returns Unit
        }

        val mockFile =
            mockk<FileHandle> {
                every { inputStream() } returns mockInputStream
                every { delete() } returns true
            }
        every { fileHandleFactory.make(any()) } returns mockFile

        every { pathFactory.getFinalDirectory(any()) } returns "/final/path"

        val uploadId = "upload-id"
        every { uploadIdGenerator.generate() } returns uploadId

        val input =
            PipelineMessage(
                checkpointCounts = mapOf(CheckpointId("1") to CheckpointValue(2, 2)),
                key = key,
                value = record,
                postProcessingCallback = {},
                context =
                    PipelineContext(
                        mapOf(CheckpointId("1") to CheckpointValue(2, 2)),
                        record,
                    )
            )
        task.handleEvent(input)

        val expectedFinalPath =
            Path.of(
                    "/final/path",
                    record.fileReference?.sourceFileRelativePath,
                )
                .toString()

        // TODO: this leaks internals of FilePartIterator — factor out injectable factory as
        // necessary
        val internalPartFactory =
            PartFactory(
                key = expectedFinalPath,
                fileNumber = 0,
            )

        val expectedPart1 =
            ObjectLoaderPartFormatter.FormattedPart(internalPartFactory.nextPart(bytes1, false))
        val expectedPart2 =
            ObjectLoaderPartFormatter.FormattedPart(internalPartFactory.nextPart(bytes2, false))
        val expectedPart3 =
            ObjectLoaderPartFormatter.FormattedPart(internalPartFactory.nextPart(bytes3, true))

        val output = ObjectKey(Fixtures.unmappedDescriptor, expectedFinalPath, uploadId)

        val outputMessage1 =
            PipelineMessage(emptyMap(), output, expectedPart1, context = input.context)
        val outputMessage2 =
            PipelineMessage(emptyMap(), output, expectedPart2, context = input.context)
        val outputMessage3 =
            PipelineMessage(emptyMap(), output, expectedPart3, context = input.context)

        coVerify(exactly = 1) { partQueue.publish(outputMessage1, 0) }
        coVerify(exactly = 1) { partQueue.publish(outputMessage2, 0) }
        coVerify(exactly = 1) { partQueue.publish(outputMessage3, 0) }

        verify { mockInputStream.close() }
        verify { mockFile.delete() }
    }

    @Test
    fun `enrichRecordsWithFilePath updates the schema and the corresponding data field`() {
        val message = Fixtures.message()
        val schema = Fixtures.schema()
        val record = Fixtures.record(message, schema)

        val myFilePath = "proto://bucket/path/file"

        record.enrichRecordWithFilePath(myFilePath)

        assertEquals(
            FieldType(StringType, nullable = true),
            schema.properties[COLUMN_NAME_AIRBYTE_FILE_PATH]
        )
        assertContains(
            Jsons.serialize(record.asJsonRecord()),
            """"$COLUMN_NAME_AIRBYTE_FILE_PATH":"$myFilePath""""
        )
    }

    object Fixtures {
        val unmappedDescriptor =
            DestinationStream.Descriptor(namespace = "namespace-1", name = "name-1")

        val fileReference =
            AirbyteRecordMessageFileReference()
                .withFileSizeBytes(10)
                .withSourceFileRelativePath("/files/place")
                .withStagingFileUrl("/local/path")

        fun message() =
            AirbyteMessage()
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("""{"something": "has to give"}"""))
                        .withFileReference(fileReference)
                )

        fun schema() =
            ObjectType(
                properties =
                    LinkedHashMap(mapOf("something" to FieldType(StringType, nullable = true)))
            )

        fun stream(schema: ObjectType = schema()) =
            DestinationStream(
                unmappedNamespace = unmappedDescriptor.namespace,
                unmappedName = unmappedDescriptor.name,
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 3,
                schema = schema,
                includeFiles = true,
                namespaceMapper = NamespaceMapper()
            )

        fun record(
            message: AirbyteMessage = message(),
            schema: ObjectType = schema(),
            stream: DestinationStream = stream(schema)
        ) =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(message),
                serializedSizeBytes = 0L,
                airbyteRawId = UUID.randomUUID(),
            )
    }
}
