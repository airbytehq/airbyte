/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_INDEX_NAME
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteProbeMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.mockk.mockk
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.MethodSource

class DestinationMessageTest {
    private val uuidGenerator = UUIDGenerator()

    private fun factory(
        isFileTransferEnabled: Boolean,
        requireCheckpointKey: Boolean = false,
        namespaceMapper: NamespaceMapper = NamespaceMapper()
    ) =
        DestinationMessageFactory(
            DestinationCatalog(
                listOf(
                    DestinationStream(
                        unmappedNamespace = descriptor.namespace,
                        unmappedName = descriptor.name,
                        Append,
                        ObjectTypeWithEmptySchema,
                        generationId = 42,
                        minimumGenerationId = 0,
                        syncId = 42,
                        namespaceMapper = namespaceMapper
                    )
                )
            ),
            isFileTransferEnabled,
            requireCheckpointIdOnRecordAndKeyOnState = requireCheckpointKey,
            namespaceMapper,
            uuidGenerator = uuidGenerator,
        )

    private fun convert(
        factory: DestinationMessageFactory,
        message: AirbyteMessage,
    ): DestinationMessage {
        val serialized = message.serializeToString()
        return factory.fromAirbyteProtocolMessage(
            // We have to set some stuff in additionalProperties, so force the protocol model back
            // to a serialized representation and back.
            // This avoids issues with e.g. `additionalProperties.put("foo", 12L)`:
            // working directly with that object, `additionalProperties["foo"]` returns `Long?`,
            // whereas converting to JSON yields `{"foo": 12}`, which then deserializes back out
            // as `Int?`.
            // Fortunately, the protocol models are (by definition) round-trippable through JSON.
            serialized.deserializeToClass(AirbyteMessage::class.java),
            serialized.length.toLong()
        )
    }

    @Test
    fun testThrowOnIncompleteStatus() {
        val e =
            assertThrows<ConfigErrorException> {
                convert(factory(isFileTransferEnabled = false), incompleteStatusMessage)
            }
        assertTrue(
            e.message!!.startsWith(
                "Received stream status INCOMPLETE message. This indicates a bug in the Airbyte platform. Original message:"
            ),
            "Exception message was wrong: ${e.message}",
        )
    }

    @Test
    fun testThrowOnFileIncompleteStatus() {
        val e =
            assertThrows<ConfigErrorException> {
                convert(factory(isFileTransferEnabled = true), incompleteStatusMessage)
            }
        assertTrue(
            e.message!!.startsWith(
                "Received stream status INCOMPLETE message. This indicates a bug in the Airbyte platform. Original message:"
            ),
            "Exception message was wrong: ${e.message}",
        )
    }

    @ParameterizedTest
    @MethodSource("roundTrippableMessages")
    fun testRoundTripRecord(message: AirbyteMessage) {
        val roundTripped = convert(factory(false), message).asProtocolMessage()
        Assertions.assertEquals(message, roundTripped)
    }

    @ParameterizedTest
    @MethodSource("roundTrippableFileMessages")
    fun testRoundTripFile(message: AirbyteMessage) {
        val roundTripped = convert(factory(true), message).asProtocolMessage()
        Assertions.assertEquals(message, roundTripped)
    }

    // Checkpoint messages aren't round-trippable.
    // We don't read in destinationStats (because we're the ones setting that field).
    @Test
    fun testStreamCheckpoint() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStreamState(blob1)
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty("id", 1234)
                )

        val parsedMessage = convert(factory(false), inputMessage) as StreamCheckpoint

        Assertions.assertEquals(
            // we represent the state message ID as a long, but jackson sees that 1234 can be Int,
            // and Int(1234) != Long(1234). (and additionalProperties is just a Map<String, Any?>)
            // So we just compare the serialized protocol messages.
            inputMessage
                .also { it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0) }
                .serializeToString(),
            parsedMessage
                .withDestinationStats(CheckpointMessage.Stats(3))
                .asProtocolMessage()
                .serializeToString()
        )
    }

    @Test
    fun testGlobalCheckpoint() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(blob1)
                                .withStreamStates(
                                    listOf(
                                        AirbyteStreamState()
                                            .withStreamDescriptor(descriptor.asProtocolObject())
                                            .withStreamState(blob2),
                                    ),
                                ),
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty("id", 1234)
                )

        val parsedMessage = convert(factory(false), inputMessage) as GlobalCheckpoint

        Assertions.assertEquals(
            inputMessage
                .also { it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0) }
                .serializeToString(),
            parsedMessage
                .withDestinationStats(CheckpointMessage.Stats(3))
                .asProtocolMessage()
                .serializeToString()
        )
    }

    @Test
    fun streamCheckpointWithKey() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStreamState(blob1)
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty(CHECKPOINT_INDEX_NAME, 1234)
                        .withAdditionalProperty(CHECKPOINT_ID_NAME, "PARTITION_ID")
                )

        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val parsedMessage = convert(factory, inputMessage) as StreamCheckpoint

        assertNotNull(parsedMessage.checkpointKey)
        assertEquals(parsedMessage.checkpointKey?.checkpointIndex!!.value, 1234)
        assertEquals(parsedMessage.checkpointKey?.checkpointId!!.value, "PARTITION_ID")
        assertEquals(
            inputMessage
                .also { it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0) }
                .serializeToString(),
            parsedMessage
                .withDestinationStats(CheckpointMessage.Stats(3))
                .asProtocolMessage()
                .serializeToString()
        )
    }

    @Test
    fun globalCheckpointWithKey() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(blob1)
                                .withStreamStates(
                                    listOf(
                                        AirbyteStreamState()
                                            .withStreamDescriptor(descriptor.asProtocolObject())
                                            .withStreamState(blob2),
                                    ),
                                ),
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty(CHECKPOINT_INDEX_NAME, 1234)
                        .withAdditionalProperty(CHECKPOINT_ID_NAME, "PARTITION_ID")
                )

        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val parsedMessage = convert(factory, inputMessage) as GlobalCheckpoint

        assertNotNull(parsedMessage.checkpointKey)
        assertEquals(parsedMessage.checkpointKey?.checkpointIndex!!.value, 1234)
        assertEquals(parsedMessage.checkpointKey?.checkpointId!!.value, "PARTITION_ID")
        assertEquals(
            inputMessage
                .also { it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0) }
                .serializeToString(),
            parsedMessage
                .withDestinationStats(CheckpointMessage.Stats(3))
                .asProtocolMessage()
                .serializeToString()
        )
    }

    @Test
    fun streamCheckpointThrowsIfRequiredKeyMissing() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStreamState(blob1)
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty(CHECKPOINT_ID_NAME, "PARTITION_ID")
                )

        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)

        Assertions.assertThrows(IllegalStateException::class.java) {
            convert(factory, inputMessage)
        }
    }

    @Test
    fun globalCheckpointThrowsIfRequiredKeyMissing() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(blob1)
                                .withStreamStates(
                                    listOf(
                                        AirbyteStreamState()
                                            .withStreamDescriptor(descriptor.asProtocolObject())
                                            .withStreamState(blob2),
                                    ),
                                ),
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty(CHECKPOINT_INDEX_NAME, 1234)
                )

        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)

        Assertions.assertThrows(IllegalStateException::class.java) {
            convert(factory, inputMessage)
        }
    }

    companion object {
        private val descriptor = DestinationStream.Descriptor("namespace", "name")
        private val blob1 = """{"foo": "bar"}""".deserializeToNode()
        private val blob2 = """{"foo": "bar"}""".deserializeToNode()
        private val incompleteStatusMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.TRACE)
                .withTrace(
                    AirbyteTraceMessage()
                        .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                        .withEmittedAt(1234.0)
                        .withStreamStatus(
                            AirbyteStreamStatusTraceMessage()
                                // Intentionally no "reasons" here - destinations never
                                // inspect that
                                // field, so it's not round-trippable
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStatus(
                                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE
                                )
                        )
                )

        @JvmStatic
        fun roundTrippableMessages(): List<Arguments> =
            listOf(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withStream("name")
                                .withNamespace("namespace")
                                .withEmittedAt(1234)
                                .withMeta(
                                    AirbyteRecordMessageMeta()
                                        .withChanges(
                                            listOf(
                                                AirbyteRecordMessageMetaChange()
                                                    .withField("foo")
                                                    .withReason(
                                                        AirbyteRecordMessageMetaChange.Reason
                                                            .DESTINATION_FIELD_SIZE_LIMITATION
                                                    )
                                                    .withChange(
                                                        AirbyteRecordMessageMetaChange.Change.NULLED
                                                    )
                                            )
                                        )
                                )
                                .withData(blob1)
                        ),
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                .withEmittedAt(1234.0)
                                .withStreamStatus(
                                    AirbyteStreamStatusTraceMessage()
                                        // Intentionally no "reasons" here - destinations never
                                        // inspect that
                                        // field, so it's not round-trippable
                                        .withStreamDescriptor(descriptor.asProtocolObject())
                                        .withStatus(
                                            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
                                                .COMPLETE
                                        )
                                )
                        ),
                )
                .map { Arguments.of(it) }

        @JvmStatic
        fun roundTrippableFileMessages(): List<Arguments> {
            val file =
                mapOf(
                    "file_url" to "file://foo/bar",
                    "file_relative_path" to "foo/bar",
                    "source_file_url" to "file://source/foo/bar",
                    "modified" to 123L,
                    "bytes" to 9001L,
                )

            return listOf(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withStream("name")
                                .withNamespace("namespace")
                                .withEmittedAt(1234)
                                .withAdditionalProperty("file", file)
                        ),
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                .withEmittedAt(1234.0)
                                .withStreamStatus(
                                    AirbyteStreamStatusTraceMessage()
                                        // Intentionally no "reasons" here - destinations never
                                        // inspect that
                                        // field, so it's not round-trippable
                                        .withStreamDescriptor(descriptor.asProtocolObject())
                                        .withStatus(
                                            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
                                                .COMPLETE
                                        )
                                )
                        ),
                )
                .map { Arguments.of(it) }
        }
    }

    @Test
    fun testNullStreamState() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState().withStreamDescriptor(descriptor.asProtocolObject())
                        )
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                )

        assertDoesNotThrow { convert(factory(false), inputMessage) as StreamCheckpoint }
    }

    @ParameterizedTest
    @CsvSource(
        "/files/test/1.pdf, /assets/test/1.pdf, 30",
        "/files/test/index.html, /html/test/1.html, 12580",
        "/files/cat.jpg, /cats/photos/1/lion.jpg, 999"
    )
    fun `a file reference can be parsed from a protocol message`(
        stagingFileUrl: String,
        sourceFileRelativePath: String,
        fileSizeBytes: Long,
    ) {
        val proto = AirbyteRecordMessageFileReference()
        proto.stagingFileUrl = stagingFileUrl
        proto.sourceFileRelativePath = sourceFileRelativePath
        proto.fileSizeBytes = fileSizeBytes

        val internal = FileReference.fromProtocol(proto)
        assertEquals(stagingFileUrl, internal.stagingFileUrl)
        assertEquals(sourceFileRelativePath, internal.sourceFileRelativePath)
        assertEquals(fileSizeBytes, internal.fileSizeBytes)
    }

    @ParameterizedTest
    @CsvSource(
        "/files/test/1.pdf, /assets/test/1.pdf, 30",
        "/files/test/index.html, /html/test/1.html, 12580",
        "/files/cat.jpg, /cats/photos/1/lion.jpg, 999"
    )
    fun `a destination record raw is initialized with a file reference if present on the protocol msg`(
        stagingFileUrl: String,
        sourceFileRelativePath: String,
        fileSizeBytes: Long,
    ) {
        val fileRefProto = AirbyteRecordMessageFileReference()
        fileRefProto.stagingFileUrl = stagingFileUrl
        fileRefProto.sourceFileRelativePath = sourceFileRelativePath
        fileRefProto.fileSizeBytes = fileSizeBytes

        val msg =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(AirbyteRecordMessage().withFileReference(fileRefProto))

        val internalRecord =
            DestinationRecordRaw(
                stream = mockk(relaxed = true),
                rawData = DestinationRecordJsonSource(msg),
                serializedSizeBytes = "serialized".length.toLong(),
                airbyteRawId = uuidGenerator.v7(),
            )

        assertEquals(stagingFileUrl, internalRecord.fileReference!!.stagingFileUrl)
        assertEquals(sourceFileRelativePath, internalRecord.fileReference!!.sourceFileRelativePath)
        assertEquals(fileSizeBytes, internalRecord.fileReference!!.fileSizeBytes)
    }

    @Test
    fun `a destination record raw is initialized with a null reference if not present on protocol msg`() {
        val msg =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(AirbyteRecordMessage().withFileReference(null))
        val internalRecord =
            DestinationRecordRaw(
                stream = mockk(relaxed = true),
                rawData = DestinationRecordJsonSource(msg),
                serializedSizeBytes = "serialized".length.toLong(),
                airbyteRawId = uuidGenerator.v7(),
            )

        assertNull(internalRecord.fileReference)
    }

    @Test
    fun `message factory throws if required checkpoint key missing from state`() {
        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStreamState(blob1)
                        )
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                )

        Assertions.assertThrows(IllegalStateException::class.java) {
            convert(factory, inputMessage)
        }
    }

    @Test
    fun `message factory throws if required checkpoint id missing from record`() {
        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream("name")
                        .withNamespace("namespace")
                        .withEmittedAt(1234)
                        .withData(blob1)
                        .withMeta(
                            AirbyteRecordMessageMeta()
                                .withChanges(
                                    listOf(
                                        AirbyteRecordMessageMetaChange()
                                            .withField("foo")
                                            .withReason(
                                                AirbyteRecordMessageMetaChange.Reason
                                                    .DESTINATION_FIELD_SIZE_LIMITATION
                                            )
                                            .withChange(
                                                AirbyteRecordMessageMetaChange.Change.NULLED
                                            )
                                    )
                                )
                        )
                )

        Assertions.assertThrows(IllegalStateException::class.java) {
            convert(factory, inputMessage)
        }
    }

    @Test
    fun `message factory creates record from protobuf`() {
        // Note: can't be a mock or `schemaInAirbyteProxyOrder` won't return the correct value
        val stream =
            DestinationStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = true),
                                "name" to FieldType(StringType, nullable = true)
                            )
                    ),
                namespaceMapper = NamespaceMapper()
            )
        val catalog = DestinationCatalog(streams = listOf(stream))

        val factory =
            DestinationMessageFactory(
                catalog = catalog,
                fileTransferEnabled = false,
                requireCheckpointIdOnRecordAndKeyOnState = true,
                namespaceMapper = NamespaceMapper(),
                uuidGenerator = uuidGenerator,
            )
        val inputMessage =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("name")
                        .setStreamNamespace("namespace")
                        .setEmittedAtMs(1234)
                        .addData(AirbyteValueProtobuf.newBuilder().setInteger(1))
                        .addData(AirbyteValueProtobuf.newBuilder().setString("test"))
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()

        val destinationRecord =
            factory.fromAirbyteProtobufMessage(inputMessage, 100L) as DestinationRecord

        assertEquals("name", destinationRecord.stream.descriptor.name)
        assertEquals("namespace", destinationRecord.stream.descriptor.namespace)
        assertEquals("checkpoint_id", destinationRecord.checkpointId?.value)
        assertEquals(100L, destinationRecord.serializedSizeBytes)
        assertEquals(
            1234,
            destinationRecord
                .asDestinationRecordRaw()
                .asEnrichedDestinationRecordAirbyteValue()
                .emittedAtMs
        )
        assertEquals(
            1,
            destinationRecord
                .asDestinationRecordRaw()
                .asEnrichedDestinationRecordAirbyteValue()
                .declaredFields["id"]
                ?.let { (it.abValue as IntegerValue).value.toInt() }
        )
        assertEquals(
            "test",
            destinationRecord
                .asDestinationRecordRaw()
                .asEnrichedDestinationRecordAirbyteValue()
                .declaredFields["name"]
                ?.let { (it.abValue as StringValue).value }
        )
    }

    @Test
    fun `message factory creates control message from protobuf-wrapped airbyte message`() {
        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val inputStateMessage =
            AirbyteMessageProtobuf.newBuilder()
                .setAirbyteProtocolMessage(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.STATE)
                        .withState(
                            AirbyteStateMessage()
                                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                                .withStream(
                                    AirbyteStreamState()
                                        .withStreamDescriptor(descriptor.asProtocolObject())
                                        .withStreamState(blob1)
                                )
                                .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                                .withAdditionalProperty(CHECKPOINT_INDEX_NAME, 1234)
                                .withAdditionalProperty(CHECKPOINT_ID_NAME, "PARTITION_ID")
                        )
                        .serializeToString()
                )
                .build()

        val streamCheckpoint =
            factory.fromAirbyteProtobufMessage(inputStateMessage, 100L) as StreamCheckpoint

        assertEquals("PARTITION_ID", streamCheckpoint.checkpointKey?.checkpointId?.value)
        assertEquals(1234, streamCheckpoint.checkpointKey?.checkpointIndex?.value)
        assertEquals(100L, streamCheckpoint.serializedSizeBytes)
        assertEquals(2L, streamCheckpoint.sourceStats?.recordCount)
        assertEquals(blob1, streamCheckpoint.asProtocolMessage().state.stream.streamState)
    }

    @Test
    fun `message factory creates heartbeat from protobuf heartbeat`() {
        val factory = factory(isFileTransferEnabled = false, requireCheckpointKey = true)
        val heartbeatMessage =
            AirbyteMessageProtobuf.newBuilder()
                .setProbe(AirbyteProbeMessageProtobuf.newBuilder().build())
                .build()
        val message = factory.fromAirbyteProtobufMessage(heartbeatMessage, 0L)
        Assertions.assertTrue(message is ProbeMessage)
    }

    @Test
    fun `message factory does not throw on global state message with stream state belonging to unrecognized stream`() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(blob1)
                                .withStreamStates(
                                    listOf(
                                        AirbyteStreamState()
                                            .withStreamDescriptor(
                                                StreamDescriptor()
                                                    .withNamespace("potato")
                                                    .withName("tomato")
                                            )
                                            .withStreamState(blob2),
                                    ),
                                ),
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                        .withAdditionalProperty("id", 1234)
                )

        val parsedMessage = convert(factory(false), inputMessage) as GlobalCheckpoint

        assertEquals(
            inputMessage
                .also { it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0) }
                .serializeToString(),
            parsedMessage
                .withDestinationStats(CheckpointMessage.Stats(3))
                .asProtocolMessage()
                .serializeToString()
        )
    }
}
