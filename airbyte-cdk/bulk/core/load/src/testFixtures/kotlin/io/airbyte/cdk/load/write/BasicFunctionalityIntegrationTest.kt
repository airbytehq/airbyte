/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationStreamComplete
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

abstract class BasicFunctionalityIntegrationTest(
    /** The config to pass into the connector, as a serialized JSON blob */
    val configContents: String,
    val configSpecClass: Class<out ConfigurationSpecification>,
    dataDumper: DestinationDataDumper,
    destinationCleaner: DestinationCleaner,
    recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    nameMapper: NameMapper = NoopNameMapper,
    /**
     * Whether to actually verify that the connector wrote data to the destination. This should only
     * ever be disabled for test destinations (dev-null, etc.).
     */
    val verifyDataWriting: Boolean = true,
) : IntegrationTest(dataDumper, destinationCleaner, recordMangler, nameMapper) {
    val parsedConfig = ValidatedJsonUtils.parseOne(configSpecClass, configContents)

    @Test
    open fun testBasicWrite() {
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val messages =
            runSync(
                configContents,
                stream,
                listOf(
                    DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream",
                        data = """{"id": 5678}""",
                        emittedAtMs = 1234,
                        changes =
                            listOf(
                                DestinationRecord.Change(
                                    field = "foo",
                                    change = AirbyteRecordMessageMetaChange.Change.NULLED,
                                    reason =
                                        AirbyteRecordMessageMetaChange.Reason
                                            .SOURCE_FIELD_SIZE_LIMITATION
                                )
                            )
                    ),
                    StreamCheckpoint(
                        streamName = "test_stream",
                        streamNamespace = randomizedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    )
                )
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll(
            {
                assertEquals(
                    1,
                    stateMessages.size,
                    "Expected to receive exactly one state message, got ${stateMessages.size} ($stateMessages)"
                )
                assertEquals(
                    StreamCheckpoint(
                            streamName = "test_stream",
                            streamNamespace = randomizedNamespace,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 1,
                            destinationRecordCount = 1,
                        )
                        .asProtocolMessage(),
                    stateMessages.first()
                )
            },
            {
                if (verifyDataWriting) {
                    dumpAndDiffRecords(
                        ValidatedJsonUtils.parseOne(configSpecClass, configContents),
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to 5678),
                                airbyteMeta =
                                    OutputRecord.Meta(
                                        changes =
                                            listOf(
                                                DestinationRecord.Change(
                                                    field = "foo",
                                                    change =
                                                        AirbyteRecordMessageMetaChange.Change
                                                            .NULLED,
                                                    reason =
                                                        AirbyteRecordMessageMetaChange.Reason
                                                            .SOURCE_FIELD_SIZE_LIMITATION
                                                )
                                            ),
                                        syncId = 42
                                    )
                            )
                        ),
                        stream,
                        primaryKey = listOf(listOf("id")),
                        cursor = null,
                    )
                }
            },
        )
    }

    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/10413")
    @Test
    open fun testMidSyncCheckpointingStreamState() =
        runBlocking(Dispatchers.IO) {
            fun makeStream(name: String) =
                DestinationStream(
                    DestinationStream.Descriptor(randomizedNamespace, name),
                    Append,
                    ObjectType(linkedMapOf("id" to intType)),
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 42,
                )
            val destination =
                destinationProcessFactory.createDestinationProcess(
                    "write",
                    configContents,
                    DestinationCatalog(
                            listOf(
                                makeStream("test_stream1"),
                                makeStream("test_stream2"),
                            )
                        )
                        .asProtocolObject(),
                )
            launch { destination.run() }

            // Send one record+state to each stream
            destination.sendMessages(
                DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream1",
                        data = """{"id": 12}""",
                        emittedAtMs = 1234,
                    )
                    .asProtocolMessage(),
                StreamCheckpoint(
                        streamNamespace = randomizedNamespace,
                        streamName = "test_stream1",
                        blob = """{"foo": "bar1"}""",
                        sourceRecordCount = 1
                    )
                    .asProtocolMessage(),
                DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream2",
                        data = """{"id": 34}""",
                        emittedAtMs = 1234,
                    )
                    .asProtocolMessage(),
                StreamCheckpoint(
                        streamNamespace = randomizedNamespace,
                        streamName = "test_stream2",
                        blob = """{"foo": "bar2"}""",
                        sourceRecordCount = 1
                    )
                    .asProtocolMessage()
            )
            // Send records to stream1 until we get a state message back.
            // Generally, we expect that that state message will belong to stream1.
            val stateMessages: List<AirbyteStateMessage>
            var i = 0
            while (true) {
                // limit ourselves to 2M messages, which should be enough to force a flush
                if (i < 2_000_000) {
                    destination.sendMessage(
                        DestinationRecord(
                                namespace = randomizedNamespace,
                                name = "test_stream1",
                                data = """{"id": 56}""",
                                emittedAtMs = 1234,
                            )
                            .asProtocolMessage()
                    )
                    i++
                } else {
                    delay(1000)
                }
                val returnedMessages = destination.readMessages()
                if (returnedMessages.any { it.type == AirbyteMessage.Type.STATE }) {
                    stateMessages =
                        returnedMessages
                            .filter { it.type == AirbyteMessage.Type.STATE }
                            .map { it.state }
                    break
                }
            }

            // for each state message, verify that it's a valid state,
            // and that we actually wrote the data
            stateMessages.forEach { stateMessage ->
                val streamName = stateMessage.stream.streamDescriptor.name
                val streamNamespace = stateMessage.stream.streamDescriptor.namespace
                // basic state message checks - this is mostly just exercising the CDK itself,
                // but is cheap and easy to do.
                assertAll(
                    { assertEquals(randomizedNamespace, streamNamespace) },
                    {
                        assertTrue(
                            streamName == "test_stream1" || streamName == "test_stream2",
                            "Expected stream name to be test_stream1 or test_stream2, got $streamName"
                        )
                    },
                    {
                        assertEquals(
                            1.0,
                            stateMessage.destinationStats.recordCount,
                            "Expected destination stats to show 1 record"
                        )
                    },
                    {
                        when (streamName) {
                            "test_stream1" -> {
                                assertEquals(
                                    Jsons.readTree("""{"foo": "bar1"}"""),
                                    stateMessage.stream.streamState,
                                )
                            }
                            "test_stream2" -> {
                                assertEquals(
                                    Jsons.readTree("""{"foo": "bar2"}"""),
                                    stateMessage.stream.streamState
                                )
                            }
                            else ->
                                throw IllegalStateException("Unexpected stream name: $streamName")
                        }
                    }
                )
                if (verifyDataWriting) {
                    val records = dataDumper.dumpRecords(parsedConfig, makeStream(streamName))
                    val expectedId =
                        when (streamName) {
                            "test_stream1" -> 12
                            "test_stream2" -> 34
                            else ->
                                throw IllegalStateException("Unexpected stream name: $streamName")
                        }
                    val expectedRecord =
                        recordMangler.mapRecord(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to expectedId),
                                airbyteMeta = OutputRecord.Meta(changes = listOf(), syncId = 42)
                            )
                        )

                    assertTrue(
                        records.any { actualRecord -> expectedRecord.data == actualRecord.data },
                        "Expected the first record to be present in the dumped records."
                    )
                }
            }

            destination.sendMessages(
                DestinationStreamComplete(
                        DestinationStream.Descriptor(randomizedNamespace, "test_stream1"),
                        System.currentTimeMillis()
                    )
                    .asProtocolMessage(),
                DestinationStreamComplete(
                        DestinationStream.Descriptor(randomizedNamespace, "test_stream2"),
                        System.currentTimeMillis()
                    )
                    .asProtocolMessage()
            )
            destination.shutdown()
        }

    @Test
    open fun testNamespaces() {
        assumeTrue(verifyDataWriting)
        fun makeStream(namespace: String) =
            DestinationStream(
                DestinationStream.Descriptor(namespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val stream1 = makeStream(randomizedNamespace + "_1")
        val stream2 = makeStream(randomizedNamespace + "_2")
        runSync(
            configContents,
            DestinationCatalog(
                listOf(
                    stream1,
                    stream2,
                )
            ),
            listOf(
                DestinationRecord(
                    namespace = stream1.descriptor.namespace,
                    name = stream1.descriptor.name,
                    data = """{"id": 1234}""",
                    emittedAtMs = 1234,
                ),
                DestinationRecord(
                    namespace = stream2.descriptor.namespace,
                    name = stream2.descriptor.name,
                    data = """{"id": 5678}""",
                    emittedAtMs = 1234,
                ),
            )
        )
        assertAll(
            {
                dumpAndDiffRecords(
                    parsedConfig,
                    listOf(
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 0,
                            data = mapOf("id" to 1234),
                            airbyteMeta = OutputRecord.Meta(changes = listOf(), syncId = 42)
                        )
                    ),
                    stream1,
                    listOf(listOf("id")),
                    cursor = null
                )
            },
            {
                dumpAndDiffRecords(
                    parsedConfig,
                    listOf(
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 0,
                            data = mapOf("id" to 5678),
                            airbyteMeta = OutputRecord.Meta(changes = listOf(), syncId = 42)
                        )
                    ),
                    stream2,
                    listOf(listOf("id")),
                    cursor = null
                )
            }
        )
    }

    @Test
    open fun testFunkyStreamAndColumnNames() {
        assumeTrue(verifyDataWriting)
        fun makeStream(
            name: String,
            schema: LinkedHashMap<String, FieldType> = linkedMapOf("id" to intType),
        ) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, name),
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        // Catalog with some weird schemas
        val catalog =
            DestinationCatalog(
                listOf(
                    makeStream("streamWithCamelCase"),
                    makeStream("stream_with_underscores"),
                    makeStream("STREAM_WITH_ALL_CAPS"),
                    makeStream("CapitalCase"),
                    makeStream(
                        "stream_with_edge_case_field_names",
                        linkedMapOf(
                            "id" to intType,
                            "fieldWithCamelCase" to intType,
                            "field_with_underscore" to intType,
                            "FIELD_WITH_ALL_CAPS" to intType,
                            "field_with_spécial_character" to intType,
                            // "order" is a reserved word in many sql engines
                            "order" to intType,
                            "ProperCase" to intType,
                        )
                    ),
                    // this is apparently trying to test for reserved words?
                    // https://github.com/airbytehq/airbyte/pull/1753
                    makeStream("groups", linkedMapOf("id" to intType, "authorization" to intType)),
                )
            )
        // For each stream, generate a record containing every field in the schema
        val messages =
            catalog.streams.map {
                DestinationRecord(
                    it.descriptor,
                    ObjectValue(
                        (it.schema as ObjectType).properties.mapValuesTo(linkedMapOf()) {
                            IntegerValue(42)
                        }
                    ),
                    1234,
                    meta = null,
                    serialized = "",
                )
            }
        runSync(configContents, catalog, messages)
        assertAll(
            catalog.streams.map { stream ->
                {
                    dumpAndDiffRecords(
                        parsedConfig,
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data =
                                    (stream.schema as ObjectType).properties.mapValuesTo(
                                        linkedMapOf()
                                    ) { 42 },
                                airbyteMeta = OutputRecord.Meta(changes = null, syncId = 42)
                            )
                        ),
                        stream,
                        primaryKey = listOf(listOf("id")),
                        cursor = null,
                    )
                }
            }
        )
    }

    companion object {
        private val intType = FieldType(IntegerType, nullable = true)
    }
}
