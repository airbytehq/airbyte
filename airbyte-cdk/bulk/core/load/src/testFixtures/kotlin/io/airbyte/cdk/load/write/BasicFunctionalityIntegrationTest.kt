/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.time.OffsetDateTime
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
    /**
     * Whether a stream schema from a newer sync is also applied to older records. For example, in
     * databases where we write records into a table, dropping a column from that table will also
     * drop that column from older records.
     *
     * In contrast, file-based destinations where each sync creates a new file do _not_ have
     * retroactive schemas: writing a new file without a column has no effect on older files.
     */
    val isStreamSchemaRetroactive: Boolean,
    val supportsDedup: Boolean,
    val stringifySchemalessObjects: Boolean,
    val promoteUnionToObject: Boolean,
    val preserveUndeclaredFields: Boolean,
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
                        data = """{"id": 5678, "undeclared": "asdf"}""",
                        emittedAtMs = 1234,
                        changes =
                            mutableListOf(
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
                                data =
                                    if (preserveUndeclaredFields) {
                                        mapOf("id" to 5678, "undeclared" to "asdf")
                                    } else {
                                        mapOf("id" to 5678)
                                    },
                                airbyteMeta =
                                    OutputRecord.Meta(
                                        changes =
                                            mutableListOf(
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
    open fun testMidSyncCheckpointingStreamState(): Unit =
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
            launch {
                try {
                    destination.run()
                } catch (e: DestinationUncleanExitException) {
                    // swallow exception - we'll kill the destination,
                    // so it's expected to exit uncleanly
                }
            }

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

            try {
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
                                    throw IllegalStateException(
                                        "Unexpected stream name: $streamName"
                                    )
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
                                    throw IllegalStateException(
                                        "Unexpected stream name: $streamName"
                                    )
                            }
                        val expectedRecord =
                            recordMangler.mapRecord(
                                OutputRecord(
                                    extractedAt = 1234,
                                    generationId = 0,
                                    data = mapOf("id" to expectedId),
                                    airbyteMeta = OutputRecord.Meta(syncId = 42)
                                )
                            )

                        assertTrue(
                            records.any { actualRecord ->
                                expectedRecord.data == actualRecord.data
                            },
                            "Expected the first record to be present in the dumped records.",
                        )
                    }
                }
            } finally {
                destination.kill()
            }
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
                            airbyteMeta = OutputRecord.Meta(syncId = 42)
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
                            airbyteMeta = OutputRecord.Meta(syncId = 42)
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
    @Disabled
    open fun testFunkyCharacters() {
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
        // Catalog with some weird schemas.
        // Every stream has an int `id`, and maybe some string fields.
        val catalog =
            DestinationCatalog(
                listOf(
                    makeStream("streamWithCamelCase"),
                    makeStream("stream_with_underscores"),
                    makeStream("STREAM_WITH_ALL_CAPS"),
                    makeStream("CapitalCase"),
                    makeStream(
                        "stream_with_edge_case_field_names_and_values",
                        linkedMapOf(
                            "id" to intType,
                            "fieldWithCamelCase" to stringType,
                            "field_with_underscore" to stringType,
                            "FIELD_WITH_ALL_CAPS" to stringType,
                            "field_with_spécial_character" to stringType,
                            // "order" is a reserved word in many sql engines
                            "order" to stringType,
                            "ProperCase" to stringType,
                        )
                    ),
                    // this is apparently trying to test for reserved words?
                    // https://github.com/airbytehq/airbyte/pull/1753
                    makeStream(
                        "groups",
                        linkedMapOf("id" to intType, "authorization" to stringType)
                    ),
                )
            )
        // For each stream, generate a record containing every field in the schema.
        // The id field is always 42, and the string fields are always "foo\nbar".
        val messages =
            catalog.streams.map { stream ->
                DestinationRecord(
                    stream.descriptor,
                    ObjectValue(
                        (stream.schema as ObjectType)
                            .properties
                            .mapValuesTo(linkedMapOf<String, AirbyteValue>()) {
                                StringValue("foo\nbar")
                            }
                            .also { it["id"] = IntegerValue(42) }
                    ),
                    emittedAtMs = 1234,
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
                                    (stream.schema as ObjectType)
                                        .properties
                                        .mapValuesTo(linkedMapOf<String, Any>()) { "foo\nbar" }
                                        .also { it["id"] = 42 },
                                airbyteMeta = OutputRecord.Meta(syncId = 42)
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

    @Test
    open fun testTruncateRefresh() {
        assumeTrue(verifyDataWriting)
        fun makeStream(generationId: Long, minimumGenerationId: Long, syncId: Long) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId,
                minimumGenerationId,
                syncId,
            )
        runSync(
            configContents,
            makeStream(generationId = 12, minimumGenerationId = 0, syncId = 42),
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234L,
                )
            )
        )
        val finalStream = makeStream(generationId = 13, minimumGenerationId = 13, syncId = 43)
        runSync(
            configContents,
            finalStream,
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "name": "second_value"}""",
                    emittedAtMs = 1234,
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 13,
                    data = mapOf("id" to 42, "name" to "second_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testAppend() {
        assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
            )
        runSync(
            configContents,
            makeStream(syncId = 42),
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234L,
                )
            )
        )
        val finalStream = makeStream(syncId = 43)
        runSync(
            configContents,
            finalStream,
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "name": "second_value"}""",
                    emittedAtMs = 1234,
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "name" to "first_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "name" to "second_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    /**
     * Intended to test for basic schema evolution. Runs two append syncs, where the second sync has
     * a few changes
     * * drop the `to_drop` column
     * * add a `to_add` column
     * * change the `to_change` column from int to string
     */
    @Test
    open fun testAppendSchemaEvolution() {
        assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long, schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
            )
        runSync(
            configContents,
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "to_change" to intType)
            ),
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "to_drop": "val1", "to_change": 42}""",
                    emittedAtMs = 1234L,
                )
            )
        )
        val finalStream =
            makeStream(
                syncId = 43,
                linkedMapOf("id" to intType, "to_change" to stringType, "to_add" to stringType)
            )
        runSync(
            configContents,
            finalStream,
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "to_change": "val2", "to_add": "val3"}""",
                    emittedAtMs = 1234,
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        if (isStreamSchemaRetroactive)
                        // the first sync's record has to_change modified to a string,
                        // and to_drop is gone completely
                        mapOf("id" to 42, "to_change" to "42")
                        else mapOf("id" to 42, "to_drop" to "val1", "to_change" to 42),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "to_change" to "val2", "to_add" to "val3"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testDedup() {
        assumeTrue(supportsDedup)
        fun makeStream(syncId: Long) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("id1"), listOf("id2")),
                        cursor = listOf("updated_at"),
                    ),
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id1" to intType,
                                "id2" to intType,
                                "updated_at" to timestamptzType,
                                "name" to stringType,
                                "_ab_cdc_deleted_at" to timestamptzType,
                            )
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = syncId,
            )
        fun makeRecord(data: String, extractedAt: Long) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                data,
                emittedAtMs = extractedAt,
            )

        val sync1Stream = makeStream(syncId = 42)
        runSync(
            configContents,
            sync1Stream,
            listOf(
                // emitted_at:1000 is equal to 1970-01-01 00:00:01Z.
                // This obviously makes no sense in relation to updated_at being in the year 2000,
                // but that's OK because (from destinations POV) updated_at has no relation to
                // extractedAt.
                makeRecord(
                    """{"id1": 1, "id2": 200, "updated_at": "2000-01-01T00:00:00Z", "name": "Alice1", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 1000,
                ),
                // Emit a second record for id=(1,200) with a different updated_at.
                makeRecord(
                    """{"id1": 1, "id2": 200, "updated_at": "2000-01-01T00:01:00Z", "name": "Alice2", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 1000,
                ),
                // Emit a record with no _ab_cdc_deleted_at field. CDC sources typically emit an
                // explicit null, but we should handle both cases.
                makeRecord(
                    """{"id1": 1, "id2": 201, "updated_at": "2000-01-01T00:02:00Z", "name": "Bob1"}""",
                    extractedAt = 1000,
                ),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // Alice has only the newer record, and Bob also exists
                OutputRecord(
                    extractedAt = 1000,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to 1,
                            "id2" to 200,
                            "updated_at" to OffsetDateTime.parse("2000-01-01T00:01:00Z"),
                            "name" to "Alice2",
                            "_ab_cdc_deleted_at" to null
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1000,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to 1,
                            "id2" to 201,
                            "updated_at" to OffsetDateTime.parse("2000-01-01T00:02:00Z"),
                            "name" to "Bob1"
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            sync1Stream,
            primaryKey = listOf(listOf("id1"), listOf("id2")),
            cursor = listOf("updated_at"),
        )

        val sync2Stream = makeStream(syncId = 43)
        runSync(
            configContents,
            sync2Stream,
            listOf(
                // Update both Alice and Bob
                makeRecord(
                    """{"id1": 1, "id2": 200, "updated_at": "2000-01-02T00:00:00Z", "name": "Alice3", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 2000,
                ),
                makeRecord(
                    """{"id1": 1, "id2": 201, "updated_at": "2000-01-02T00:00:00Z", "name": "Bob2"}""",
                    extractedAt = 2000,
                ),
                // And delete Bob. Again, T+D doesn't check the actual _value_ of deleted_at (i.e.
                // the fact that it's in the past is irrelevant). It only cares whether deleted_at
                // is non-null. So the destination should delete Bob.
                makeRecord(
                    """{"id1": 1, "id2": 201, "updated_at": "2000-01-02T00:01:00Z", "_ab_cdc_deleted_at": "1970-01-01T00:00:00Z"}""",
                    extractedAt = 2000,
                ),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // Alice still exists (and has been updated to the latest version), but Bob is gone
                OutputRecord(
                    extractedAt = 2000,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to 1,
                            "id2" to 200,
                            "updated_at" to OffsetDateTime.parse("2000-01-02T00:00:00Z"),
                            "name" to "Alice3",
                            "_ab_cdc_deleted_at" to null
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            sync2Stream,
            primaryKey = listOf(listOf("id1"), listOf("id2")),
            cursor = listOf("updated_at"),
        )
    }

    // TODO basic allTypes() test

    /**
     * Some types (object/array) are expected to contain other types. Verify that we handle them
     * correctly.
     *
     * In particular, verify behavior when they don't specify a schema for the values inside them.
     * (e.g. `{type: object}` (without an explicit `properties`) / `{type: array}` (without explicit
     * `items`). Some destinations can write those types directly; other destinations need to
     * serialize them to a JSON string first.
     */
    @Test
    open fun testContainerTypes() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "problematic_types"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to FieldType(IntegerType, nullable = true),
                        "schematized_object" to
                            FieldType(
                                ObjectType(
                                    linkedMapOf(
                                        "id" to FieldType(IntegerType, nullable = true),
                                        "name" to FieldType(StringType, nullable = true),
                                    )
                                ),
                                nullable = true,
                            ),
                        "empty_object" to FieldType(ObjectTypeWithEmptySchema, nullable = true),
                        "schemaless_object" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                        "schemaless_array" to FieldType(ArrayTypeWithoutSchema, nullable = true),
                    ),
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
        runSync(
            configContents,
            stream,
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 1,
                          "schematized_object": { "id": 1, "name": "Joe" },
                          "empty_object": {},
                          "schemaless_object": { "uuid": "38F52396-736D-4B23-B5B4-F504D8894B97", "probability": 1.5 },
                          "schemaless_array": [ 10, "foo", null, { "bar": "qua" } ]
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                ),
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 2,
                          "schematized_object": { "id": 2, "name": "Jane" },
                          "empty_object": {"extra": "stuff"},
                          "schemaless_object": { "address": { "street": "113 Hickey Rd", "zip": "37932" }, "flags": [ true, false, false ] },
                          "schemaless_array": []
                        }""".trimIndent(),
                    emittedAtMs = 1602637589200,
                ),
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 3,
                          "schematized_object": null,
                          "empty_object": null,
                          "schemaless_object": null,
                          "schemaless_array": null
                        }""".trimIndent(),
                    emittedAtMs = 1602637589300,
                ),
            )
        )

        val expectedRecords: List<OutputRecord> =
            listOf(
                OutputRecord(
                    extractedAt = 1602637589100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "schematized_object" to mapOf("id" to 1, "name" to "Joe"),
                            "empty_object" to emptyMap<String, Any?>(),
                            "schemaless_object" to
                                if (stringifySchemalessObjects) {
                                    """{"uuid":"38F52396-736D-4B23-B5B4-F504D8894B97","probability":1.5}"""
                                } else {
                                    mapOf(
                                        "uuid" to "38F52396-736D-4B23-B5B4-F504D8894B97",
                                        "probability" to 1.5
                                    )
                                },
                            "schemaless_array" to
                                if (stringifySchemalessObjects) {
                                    """[10,"foo",null,{"bar:"qua"}]"""
                                } else {
                                    listOf(10, "foo", null, mapOf("bar" to "qua"))
                                },
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1602637589200,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 2,
                            "schematized_object" to mapOf("id" to 2, "name" to "Jane"),
                            "empty_object" to
                                if (stringifySchemalessObjects) {
                                    """{"extra":"stuff"}"""
                                } else {
                                    mapOf("extra" to "stuff")
                                },
                            "schemaless_object" to
                                if (stringifySchemalessObjects) {
                                    """{"address":{"street":"113 Hickey Rd","zip":"37932"},"flags":[true,false,false]}"""
                                } else {
                                    mapOf(
                                        "address" to
                                            mapOf(
                                                "street" to "113 Hickey Rd",
                                                "zip" to "37932",
                                            ),
                                        "flags" to listOf(true, false, false)
                                    )
                                },
                            "schemaless_array" to
                                if (stringifySchemalessObjects) {
                                    "[]"
                                } else {
                                    emptyList<Any>()
                                },
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1602637589300,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 3,
                            "schematized_object" to null,
                            "empty_object" to null,
                            "schemaless_object" to null,
                            "schemaless_array" to null,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            )

        dumpAndDiffRecords(
            parsedConfig,
            expectedRecords,
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    /**
     * This test verifies that destinations handle unions correctly.
     *
     * Some destinations have poor native support for union types, and instead promote unions into
     * objects. For example, given a schema `Union(String, Integer)`, this field would be written
     * into the destination as either `{"string": "foo"}` or `{"integer": 42}`.
     */
    @Test
    open fun testUnions() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "problematic_types"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to FieldType(IntegerType, nullable = true),
                        // in jsonschema, there are two ways to achieve this:
                        // {type: [string, int]}
                        // {oneOf: [{type: string}, {type: int}]}
                        // Our AirbyteType treats them identically, so we don't need two test cases.
                        "combined_type" to
                            FieldType(UnionType(listOf(StringType, IntegerType)), nullable = true),
                        "union_of_objects_with_properties_identical" to
                            FieldType(
                                UnionType(
                                    listOf(
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        ),
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_overlapping" to
                            FieldType(
                                UnionType(
                                    listOf(
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        ),
                                        ObjectType(
                                            linkedMapOf(
                                                "name" to FieldType(StringType, nullable = true),
                                                "flagged" to
                                                    FieldType(BooleanType, nullable = true),
                                            )
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_nonoverlapping" to
                            FieldType(
                                UnionType(
                                    listOf(
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        ),
                                        ObjectType(
                                            linkedMapOf(
                                                "flagged" to
                                                    FieldType(BooleanType, nullable = true),
                                                "description" to
                                                    FieldType(StringType, nullable = true),
                                            )
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_contradicting" to
                            FieldType(
                                UnionType(
                                    listOf(
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        ),
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(StringType, nullable = true),
                                                "name" to FieldType(StringType, nullable = true),
                                            )
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                    ),
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
        runSync(
            configContents,
            stream,
            listOf(
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 1,
                          "combined_type": "string1",
                          "union_of_objects_with_properties_identical": { "id": 10, "name": "Joe" },
                          "union_of_objects_with_properties_overlapping": { "id": 20, "name": "Jane", "flagged": true },
                          "union_of_objects_with_properties_contradicting": { "id": 1, "name": "Jenny" },
                          "union_of_objects_with_properties_nonoverlapping": { "id": 30, "name": "Phil", "flagged": false, "description":"Very Phil" }
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                ),
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 2,
                          "combined_type": 20,
                          "union_of_objects_with_properties_identical": {},
                          "union_of_objects_with_properties_overlapping": {},
                          "union_of_objects_with_properties_nonoverlapping": {},
                          "union_of_objects_with_properties_contradicting": { "id": "seal-one-hippity", "name": "James" }
                        }""".trimIndent(),
                    emittedAtMs = 1602637589200,
                ),
                DestinationRecord(
                    randomizedNamespace,
                    "problematic_types",
                    """
                        {
                          "id": 3,
                          "combined_type": null,
                          "union_of_objects_with_properties_identical": null,
                          "union_of_objects_with_properties_overlapping": null,
                          "union_of_objects_with_properties_nonoverlapping": null,
                          "union_of_objects_with_properties_contradicting": null
                        }""".trimIndent(),
                    emittedAtMs = 1602637589300,
                ),
            )
        )

        fun maybePromote(typeName: String, value: Any?) =
            if (promoteUnionToObject) {
                mapOf(
                    "type" to typeName,
                    typeName to value,
                )
            } else {
                value
            }
        val expectedRecords: List<OutputRecord> =
            listOf(
                OutputRecord(
                    extractedAt = 1602637589100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "combined_type" to maybePromote("string", "string1"),
                            "union_of_objects_with_properties_identical" to
                                maybePromote("object", mapOf("id" to 10, "name" to "Joe")),
                            "union_of_objects_with_properties_overlapping" to
                                maybePromote(
                                    "object",
                                    mapOf("id" to 20, "name" to "Jane", "flagged" to true)
                                ),
                            "union_of_objects_with_properties_contradicting" to
                                maybePromote("object", mapOf("id" to 1, "name" to "Jenny")),
                            "union_of_objects_with_properties_nonoverlapping" to
                                maybePromote(
                                    "object",
                                    mapOf(
                                        "id" to 30,
                                        "name" to "Phil",
                                        "flagged" to false,
                                        "description" to "Very Phil",
                                    )
                                ),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1602637589200,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 2,
                            "combined_type" to maybePromote("integer", 20),
                            "union_of_objects_with_properties_identical" to
                                maybePromote("object", emptyMap<String, Any?>()),
                            "union_of_objects_with_properties_nonoverlapping" to
                                maybePromote("object", emptyMap<String, Any?>()),
                            "union_of_objects_with_properties_overlapping" to
                                maybePromote("object", emptyMap<String, Any?>()),
                            "union_of_objects_with_properties_contradicting" to
                                maybePromote(
                                    "object",
                                    mapOf("id" to "seal-one-hippity", "name" to "James")
                                ),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1602637589300,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 3,
                            "combined_type" to null,
                            "union_of_objects_with_properties_identical" to null,
                            "union_of_objects_with_properties_overlapping" to null,
                            "union_of_objects_with_properties_nonoverlapping" to null,
                            "union_of_objects_with_properties_contradicting" to null,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            )

        dumpAndDiffRecords(
            parsedConfig,
            expectedRecords,
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    companion object {
        private val intType = FieldType(IntegerType, nullable = true)
        private val stringType = FieldType(StringType, nullable = true)
        private val timestamptzType = FieldType(TimestampTypeWithTimezone, nullable = true)
    }
}
