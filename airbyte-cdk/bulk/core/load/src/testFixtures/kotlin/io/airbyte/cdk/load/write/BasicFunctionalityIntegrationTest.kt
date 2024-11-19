/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecord.Change
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
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll
import org.junit.jupiter.api.assertThrows

sealed interface AllTypesBehavior

data class StronglyTyped(
    /**
     * Whether the destination can cast any value to string. E.g. given a StringType column, if a
     * record contains `{"the_column": {"foo": "bar"}}`, does the connector treat this as a type
     * error, or does it persist a serialized JSON string?
     */
    val convertAllValuesToString: Boolean = true,
    /** Whether top-level fields are represented as float64, or as fixed-point values */
    val topLevelFloatLosesPrecision: Boolean = true,
    /** Whether floats nested inside objects/arrays are represented as float64. */
    val nestedFloatLosesPrecision: Boolean = true,
    /** Whether the destination supports integers larger than int64 */
    val integerCanBeLarge: Boolean = true,
) : AllTypesBehavior

data object Untyped : AllTypesBehavior

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
    /**
     * Whether the destination commits new data when it receives a non-`COMPLETE` stream status. For
     * example:
     * * A destination which writes new data to a temporary directory, and moves those files to the
     * "real" directory at the end of the sync if and only if it received a COMPLETE status, would
     * set this parameter to `false`.
     * * A destination which writes new data directly into the real directory throughout the sync,
     * would set this parameter to `true`.
     */
    val commitDataIncrementally: Boolean,
    val allTypesBehavior: AllTypesBehavior,
    nullEqualsUnset: Boolean = false,
) : IntegrationTest(dataDumper, destinationCleaner, recordMangler, nameMapper, nullEqualsUnset) {
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
                                Change(
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
                                                Change(
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
                                        """{"foo": "bar1"}""".deserializeToNode(),
                                        stateMessage.stream.streamState,
                                    )
                                }
                                "test_stream2" -> {
                                    assertEquals(
                                        """{"foo": "bar2"}""".deserializeToNode(),
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

    /**
     * Test behavior in a failed truncate refresh. Sync 1 just populates two records with ID 1 and
     * 2. The test then runs two more syncs:
     * 1. Sync 2 emits ID 1, and then fails the sync (i.e. no COMPLETE stream status). We expect the
     * first sync's records to still exist in the destination. The new record may be visible to the
     * data dumper, depending on the [commitDataIncrementally] parameter.
     * 2. Sync 3 emits ID 2, and then ends the sync normally (i.e. COMPLETE stream status). After
     * this sync, the data from the first sync should be deleted, and the data from both the second
     * and third syncs should be visible to the data dumper.
     */
    @Test
    open fun testInterruptedTruncateWithPriorData() {
        assumeTrue(verifyDataWriting)
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
            )
        fun makeOutputRecord(
            id: Int,
            updatedAt: String,
            extractedAt: Long,
            generationId: Long,
            syncId: Long,
        ) =
            OutputRecord(
                extractedAt = extractedAt,
                generationId = generationId,
                data =
                    mapOf(
                        "id" to id,
                        "updated_at" to OffsetDateTime.parse(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        // Run a normal sync with nonempty data
        val stream1 =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to intType,
                        "updated_at" to timestamptzType,
                        "name" to stringType,
                    )
                ),
                generationId = 41,
                minimumGenerationId = 0,
                syncId = 41,
            )
        runSync(
            configContents,
            stream1,
            listOf(
                makeInputRecord(1, "2024-01-23T01:00:00Z", 100),
                makeInputRecord(2, "2024-01-23T01:00:00Z", 100),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
            ),
            stream1,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after initial sync - this indicates a bug in basic connector behavior",
        )

        val stream2 =
            stream1.copy(
                generationId = 42,
                minimumGenerationId = 42,
                syncId = 42,
            )
        // Run a sync, but don't emit a stream status. This should not delete any existing data.
        assertThrows<DestinationUncleanExitException> {
            runSync(
                configContents,
                stream2,
                listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
                streamStatus = null,
            )
        }
        dumpAndDiffRecords(
            parsedConfig,
            listOfNotNull(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                if (commitDataIncrementally) {
                    makeOutputRecord(
                        id = 1,
                        updatedAt = "2024-01-23T02:00:00Z",
                        extractedAt = 200,
                        generationId = 42,
                        syncId = 42,
                    )
                } else {
                    null
                }
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a failed sync.",
        )

        // Run a third sync, this time with a successful status.
        // This should delete the first sync's data, and retain the second+third syncs' data.
        runSync(
            configContents,
            stream2,
            listOf(makeInputRecord(2, "2024-01-23T03:00:00Z", 300)),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T02:00:00Z",
                    extractedAt = 200,
                    generationId = 42,
                    syncId = 42,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T03:00:00Z",
                    extractedAt = 300,
                    generationId = 42,
                    syncId = 42,
                ),
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a successful sync following a failed sync. This may indicate that we are not retaining data from the failed sync.",
        )
    }

    /**
     * Largely identical to [testInterruptedTruncateWithPriorData], but doesn't run the initial
     * sync. This is mostly relevant to warehouse destinations, where running a truncate sync into
     * an empty destination behaves differently from running a truncate sync when the destination
     * already contains data.
     */
    @Test
    open fun testInterruptedTruncateWithoutPriorData() {
        assumeTrue(verifyDataWriting)
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
            )
        fun makeOutputRecord(
            id: Int,
            updatedAt: String,
            extractedAt: Long,
            generationId: Long,
            syncId: Long,
        ) =
            OutputRecord(
                extractedAt = extractedAt,
                generationId = generationId,
                data =
                    mapOf(
                        "id" to id,
                        "updated_at" to OffsetDateTime.parse(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to intType,
                        "updated_at" to timestamptzType,
                        "name" to stringType,
                    )
                ),
                generationId = 42,
                minimumGenerationId = 42,
                syncId = 42,
            )
        // Run a sync, but don't emit a stream status.
        assertThrows<DestinationUncleanExitException> {
            runSync(
                configContents,
                stream,
                listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
                streamStatus = null,
            )
        }
        dumpAndDiffRecords(
            parsedConfig,
            if (commitDataIncrementally) {
                listOf(
                    makeOutputRecord(
                        id = 1,
                        updatedAt = "2024-01-23T02:00:00Z",
                        extractedAt = 200,
                        generationId = 42,
                        syncId = 42,
                    )
                )
            } else {
                listOf()
            },
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a failed sync.",
        )

        // Run a second sync, this time with a successful status.
        // This should retain the first syncs' data.
        runSync(
            configContents,
            stream,
            listOf(makeInputRecord(2, "2024-01-23T03:00:00Z", 300)),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T02:00:00Z",
                    extractedAt = 200,
                    generationId = 42,
                    syncId = 42,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T03:00:00Z",
                    extractedAt = 300,
                    generationId = 42,
                    syncId = 42,
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a successful sync following a failed sync. This may indicate that we are not retaining data from the failed sync.",
        )
    }

    /**
     * Emulates this sequence of events:
     * 1. User runs a normal incremental sync
     * 2. User initiates a truncate refresh, but it fails.
     * 3. User cancels the truncate refresh, and initiates a normal incremental sync.
     *
     * In particular, we must retain all records from both the first and second syncs.
     *
     * This is, again, similar to [testInterruptedTruncateWithPriorData], except that the third sync
     * has generation 43 + minGeneration 0 (instead of generation=minGeneration=42)(.
     */
    @Test
    open fun resumeAfterCancelledTruncate() {
        assumeTrue(verifyDataWriting)
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
            )
        fun makeOutputRecord(
            id: Int,
            updatedAt: String,
            extractedAt: Long,
            generationId: Long,
            syncId: Long,
        ) =
            OutputRecord(
                extractedAt = extractedAt,
                generationId = generationId,
                data =
                    mapOf(
                        "id" to id,
                        "updated_at" to OffsetDateTime.parse(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        // Run a normal sync with nonempty data
        val stream1 =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to intType,
                        "updated_at" to timestamptzType,
                        "name" to stringType,
                    )
                ),
                generationId = 41,
                minimumGenerationId = 0,
                syncId = 41,
            )
        runSync(
            configContents,
            stream1,
            listOf(
                makeInputRecord(1, "2024-01-23T01:00:00Z", 100),
                makeInputRecord(2, "2024-01-23T01:00:00Z", 100),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
            ),
            stream1,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after initial sync - this indicates a bug in basic connector behavior",
        )

        val stream2 =
            stream1.copy(
                generationId = 42,
                minimumGenerationId = 42,
                syncId = 42,
            )
        // Run a sync, but don't emit a stream status. This should not delete any existing data.
        assertThrows<DestinationUncleanExitException> {
            runSync(
                configContents,
                stream2,
                listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
                streamStatus = null,
            )
        }
        dumpAndDiffRecords(
            parsedConfig,
            listOfNotNull(
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                if (commitDataIncrementally) {
                    makeOutputRecord(
                        id = 1,
                        updatedAt = "2024-01-23T02:00:00Z",
                        extractedAt = 200,
                        generationId = 42,
                        syncId = 42,
                    )
                } else {
                    null
                }
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a failed sync.",
        )

        // Run a third sync, this time with a successful status.
        // This should delete the first sync's data, and retain the second+third syncs' data.
        val stream3 =
            stream2.copy(
                generationId = 43,
                minimumGenerationId = 0,
                syncId = 43,
            )
        runSync(
            configContents,
            stream3,
            listOf(makeInputRecord(2, "2024-01-23T03:00:00Z", 300)),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // records from sync 1
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T01:00:00Z",
                    extractedAt = 100,
                    generationId = 41,
                    syncId = 41,
                ),
                // sync 2
                makeOutputRecord(
                    id = 1,
                    updatedAt = "2024-01-23T02:00:00Z",
                    extractedAt = 200,
                    generationId = 42,
                    syncId = 42,
                ),
                // and sync 3
                makeOutputRecord(
                    id = 2,
                    updatedAt = "2024-01-23T03:00:00Z",
                    extractedAt = 300,
                    generationId = 43,
                    syncId = 43,
                ),
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            "Records were incorrect after a successful sync following a failed sync. This may indicate that we are not retaining data from the failed sync.",
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

    /**
     * Change the cursor column in the second sync to a column that doesn't exist in the first sync.
     * Verify that we overwrite everything correctly.
     *
     * This essentially verifies that the destination connector correctly recognizes NULL cursors as
     * older than non-NULL cursors.
     */
    @Test
    open fun testDedupChangeCursor() {
        assumeTrue(verifyDataWriting && supportsDedup)
        fun makeStream(cursor: String) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Dedupe(
                    primaryKey = listOf(listOf("id")),
                    cursor = listOf(cursor),
                ),
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to intType,
                            cursor to intType,
                            "name" to stringType,
                        )
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
        fun makeRecord(cursorName: String) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                data = """{"id": 1, "$cursorName": 1, "name": "foo_$cursorName"}""",
                // this is unrealistic (extractedAt should always increase between syncs),
                // but it lets us force the dedupe behavior to rely solely on the cursor column,
                // instead of being able to fallback onto extractedAt.
                emittedAtMs = 100,
            )
        runSync(configContents, makeStream("cursor1"), listOf(makeRecord("cursor1")))
        val stream2 = makeStream("cursor2")
        runSync(configContents, stream2, listOf(makeRecord("cursor2")))
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "cursor2" to 1,
                            "name" to "foo_cursor2",
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                )
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = listOf("cursor2"),
        )
    }

    open val manyStreamCount = 20

    /**
     * Some destinations can't handle large numbers of streams. This test runs a basic smoke test
     * against a catalog with many streams. Subclasses many configure the number of streams using
     * [manyStreamCount].
     */
    @Test
    open fun testManyStreamsCompletion() {
        assumeTrue(verifyDataWriting)
        assertTrue(
            manyStreamCount > 1,
            "manyStreamCount should be greater than 1. If you want to disable this test, just override it and use @Disabled.",
        )
        val streams =
            (0..manyStreamCount).map { i ->
                DestinationStream(
                    DestinationStream.Descriptor(randomizedNamespace, "test_stream_$i"),
                    Append,
                    ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                    generationId = 42,
                    minimumGenerationId = 42,
                    syncId = 42,
                )
            }
        val messages =
            (0..manyStreamCount).map { i ->
                DestinationRecord(
                    randomizedNamespace,
                    "test_stream_$i",
                    """{"id": 1, "name": "foo_$i"}""",
                    emittedAtMs = 100,
                )
            }
        // Just verify that we don't crash.
        assertDoesNotThrow { runSync(configContents, DestinationCatalog(streams), messages) }
    }

    /**
     * A basic test that we handle all supported basic data types in a reasonable way. See also
     * [testContainerTypes] for objects/arrays.
     */
    // Depending on how future connector development goes - we might need to do something similar to
    // BaseSqlGeneratorIntegrationTest, where we split out tests for connectors that do/don't
    // support safe_cast. (or, we move fully to in-connector typing, and we stop worrying about
    // per-destination safe_cast support).
    @Test
    open fun testBasicTypes() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to intType,
                        // Some destinations handle numbers differently in root and nested fields
                        "struct" to
                            FieldType(
                                ObjectType(linkedMapOf("foo" to numberType)),
                                nullable = true
                            ),
                        "string" to FieldType(StringType, nullable = true),
                        "number" to FieldType(NumberType, nullable = true),
                        "integer" to FieldType(IntegerType, nullable = true),
                        "boolean" to FieldType(BooleanType, nullable = true),
                        "timestamp_with_timezone" to
                            FieldType(TimestampTypeWithTimezone, nullable = true),
                        "timestamp_without_timezone" to
                            FieldType(TimestampTypeWithoutTimezone, nullable = true),
                        "time_with_timezone" to FieldType(TimeTypeWithTimezone, nullable = true),
                        "time_without_timezone" to
                            FieldType(TimeTypeWithoutTimezone, nullable = true),
                        "date" to FieldType(DateType, nullable = true),
                    )
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
        fun makeRecord(data: String) =
            DestinationRecord(
                randomizedNamespace,
                "test_stream",
                data,
                emittedAtMs = 100,
            )
        runSync(
            configContents,
            stream,
            listOf(
                // A record with valid values for all fields
                makeRecord(
                    """
                        {
                          "id": 1,
                          "string": "foo",
                          "number": 42.1,
                          "integer": 42,
                          "boolean": true,
                          "timestamp_with_timezone": "2023-01-23T12:34:56Z",
                          "timestamp_without_timezone": "2023-01-23T12:34:56",
                          "time_with_timezone": "12:34:56Z",
                          "time_without_timezone": "12:34:56",
                          "date": "2023-01-23"
                        }
                    """.trimIndent()
                ),
                // A record with null for all fields
                makeRecord(
                    """
                        {
                          "id": 2,
                          "string": null,
                          "number": null,
                          "integer": null,
                          "boolean": null,
                          "timestamp_with_timezone": null,
                          "timestamp_without_timezone": null,
                          "time_with_timezone": null,
                          "time_without_timezone": null,
                          "date": null
                        }
                    """.trimIndent()
                ),
                // A record with all fields unset
                makeRecord("""{"id": 3}"""),
                // A record that verifies numeric behavior.
                // 99999999999999999999999999999999 is out of range for int64.
                // 50000.0000000000000001 can't be represented as a standard float64,
                // and gets rounded off.
                makeRecord(
                    """
                        {
                          "id": 4,
                          "struct": {"foo": 50000.0000000000000001},
                          "number": 50000.0000000000000001,
                          "integer": 99999999999999999999999999999999
                        }
                    """.trimIndent(),
                ),
                // A record with invalid values for all fields
                makeRecord(
                    """
                        {
                          "id": 5,
                          "string": {},
                          "number": "foo",
                          "integer": "foo",
                          "boolean": "foo",
                          "timestamp_with_timezone": "foo",
                          "timestamp_without_timezone": "foo",
                          "time_with_timezone": "foo",
                          "time_without_timezone": "foo",
                          "date": "foo"
                        }
                    """.trimIndent()
                ),
            ),
        )

        val nestedFloat: BigDecimal
        val topLevelFloat: BigDecimal
        val bigInt: BigInteger?
        val bigIntChanges: List<Change>
        val badValuesData: Map<String, Any?>
        val badValuesChanges: MutableList<Change>
        when (allTypesBehavior) {
            is StronglyTyped -> {
                nestedFloat =
                    if (allTypesBehavior.nestedFloatLosesPrecision) {
                        BigDecimal("50000.0")
                    } else {
                        BigDecimal("50000.0000000000000001")
                    }
                topLevelFloat =
                    if (allTypesBehavior.topLevelFloatLosesPrecision) {
                        BigDecimal("50000.0")
                    } else {
                        BigDecimal("50000.0000000000000001")
                    }
                bigInt =
                    if (allTypesBehavior.integerCanBeLarge) {
                        BigInteger("99999999999999999999999999999999")
                    } else {
                        null
                    }
                bigIntChanges =
                    if (allTypesBehavior.integerCanBeLarge) {
                        emptyList()
                    } else {
                        listOf(
                            Change(
                                "integer",
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        )
                    }
                badValuesData =
                    mapOf(
                        "id" to 5,
                        "string" to
                            if (allTypesBehavior.convertAllValuesToString) {
                                "{}"
                            } else {
                                null
                            },
                        "number" to null,
                        "integer" to null,
                        "boolean" to null,
                        "timestamp_with_timezone" to null,
                        "timestamp_without_timezone" to null,
                        "time_with_timezone" to null,
                        "time_without_timezone" to null,
                        "date" to null,
                    )
                badValuesChanges =
                    (stream.schema as ObjectType)
                        .properties
                        .keys
                        // id and struct don't have a bad value case here
                        // (id would make the test unusable; struct is tested in testContainerTypes)
                        .filter { it != "id" && it != "struct" }
                        .map { key ->
                            Change(
                                key,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR,
                            )
                        }
                        .filter {
                            !allTypesBehavior.convertAllValuesToString || it.field != "string"
                        }
                        .toMutableList()
            }
            Untyped -> {
                nestedFloat = BigDecimal("50000.0000000000000001")
                topLevelFloat = BigDecimal("50000.0000000000000001")
                bigInt = BigInteger("99999999999999999999999999999999")
                bigIntChanges = emptyList<Change>()
                badValuesData =
                    mapOf(
                        "id" to 5,
                        "string" to StringValue("{}"),
                        "number" to "foo",
                        "integer" to "foo",
                        "boolean" to "foo",
                        // TODO this probably indicates that we should
                        // 1. actually parse time types
                        // 2. and just rely on the fallback to JsonToAirbyteValue.fromJson to return
                        //    a StringValue
                        "timestamp_with_timezone" to TimestampValue("foo"),
                        "timestamp_without_timezone" to TimestampValue("foo"),
                        "time_with_timezone" to TimeValue("foo"),
                        "time_without_timezone" to TimeValue("foo"),
                        "date" to DateValue("foo"),
                    )
                badValuesChanges = mutableListOf()
            }
        }
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "string" to "foo",
                            "number" to 42.1,
                            "integer" to 42,
                            "boolean" to true,
                            "timestamp_with_timezone" to
                                OffsetDateTime.parse("2023-01-23T12:34:56Z"),
                            "timestamp_without_timezone" to
                                LocalDateTime.parse("2023-01-23T12:34:56"),
                            "time_with_timezone" to OffsetTime.parse("12:34:56Z"),
                            "time_without_timezone" to LocalTime.parse("12:34:56"),
                            "date" to LocalDate.parse("2023-01-23"),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 2,
                            "string" to null,
                            "number" to null,
                            "integer" to null,
                            "boolean" to null,
                            "timestamp_with_timezone" to null,
                            "timestamp_without_timezone" to null,
                            "time_with_timezone" to null,
                            "time_without_timezone" to null,
                            "date" to null,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data = mapOf("id" to 3),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 4,
                            "struct" to mapOf("foo" to nestedFloat),
                            "number" to topLevelFloat,
                            "integer" to bigInt,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = bigIntChanges),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data = badValuesData,
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = badValuesChanges),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

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
                        "schematized_array" to FieldType(ArrayType(intType), nullable = true),
                        "schemaless_array" to FieldType(ArrayTypeWithoutSchema, nullable = true),
                        "unknown" to
                            FieldType(
                                UnknownType(JsonNodeFactory.instance.textNode("test")),
                                nullable = true
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
                          "schematized_object": { "id": 1, "name": "Joe" },
                          "empty_object": {},
                          "schemaless_object": { "uuid": "38F52396-736D-4B23-B5B4-F504D8894B97", "probability": 1.5 },
                          "schematized_array": [10, null],
                          "schemaless_array": [ 10, "foo", null, { "bar": "qua" } ],
                          "unknown": {"foo": "bar"}
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
                          "schematized_array": [],
                          "schemaless_array": [],
                          "unknown": {}
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
                          "schematized_array": null,
                          "schemaless_array": null,
                          "unknown": null
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
                            "empty_object" to
                                if (stringifySchemalessObjects) "{}" else emptyMap<Any, Any>(),
                            "schemaless_object" to
                                if (stringifySchemalessObjects) {
                                    """{"uuid":"38F52396-736D-4B23-B5B4-F504D8894B97","probability":1.5}"""
                                } else {
                                    mapOf(
                                        "uuid" to "38F52396-736D-4B23-B5B4-F504D8894B97",
                                        "probability" to 1.5
                                    )
                                },
                            "schematized_array" to listOf(10, null),
                            "schemaless_array" to
                                if (stringifySchemalessObjects) {
                                    """[10,"foo",null,{"bar":"qua"}]"""
                                } else {
                                    listOf(10, "foo", null, mapOf("bar" to "qua"))
                                },
                            "unknown" to
                                if (stringifySchemalessObjects) {
                                    """{"foo":"bar"}"""
                                } else {
                                    mapOf("foo" to "bar")
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
                            "schematized_array" to emptyList<Long>(),
                            "schemaless_array" to
                                if (stringifySchemalessObjects) {
                                    "[]"
                                } else {
                                    emptyList<Any>()
                                },
                            "unknown" to
                                if (stringifySchemalessObjects) {
                                    """{}"""
                                } else {
                                    emptyMap<String, Any?>()
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
                            "schematized_array" to null,
                            "schemaless_array" to null,
                            "unknown" to null,
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
                            FieldType(UnionType.of(StringType, IntegerType), nullable = true),
                        "union_of_objects_with_properties_identical" to
                            FieldType(
                                UnionType.of(
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
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_overlapping" to
                            FieldType(
                                UnionType.of(
                                    ObjectType(
                                        linkedMapOf(
                                            "id" to FieldType(IntegerType, nullable = true),
                                            "name" to FieldType(StringType, nullable = true),
                                        )
                                    ),
                                    ObjectType(
                                        linkedMapOf(
                                            "name" to FieldType(StringType, nullable = true),
                                            "flagged" to FieldType(BooleanType, nullable = true),
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_nonoverlapping" to
                            FieldType(
                                UnionType.of(
                                    ObjectType(
                                        linkedMapOf(
                                            "id" to FieldType(IntegerType, nullable = true),
                                            "name" to FieldType(StringType, nullable = true),
                                        )
                                    ),
                                    ObjectType(
                                        linkedMapOf(
                                            "flagged" to FieldType(BooleanType, nullable = true),
                                            "description" to FieldType(StringType, nullable = true),
                                        )
                                    )
                                ),
                                nullable = true,
                            ),
                        "union_of_objects_with_properties_contradicting" to
                            FieldType(
                                UnionType.of(
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
                                mapOf("id" to 10, "name" to "Joe"),
                            "union_of_objects_with_properties_overlapping" to
                                mapOf("id" to 20, "name" to "Jane", "flagged" to true),
                            "union_of_objects_with_properties_contradicting" to
                                mapOf("id" to maybePromote("integer", 1), "name" to "Jenny"),
                            "union_of_objects_with_properties_nonoverlapping" to
                                mapOf(
                                    "id" to 30,
                                    "name" to "Phil",
                                    "flagged" to false,
                                    "description" to "Very Phil",
                                )
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
                                emptyMap<String, Any?>(),
                            "union_of_objects_with_properties_nonoverlapping" to
                                emptyMap<String, Any?>(),
                            "union_of_objects_with_properties_overlapping" to
                                emptyMap<String, Any?>(),
                            "union_of_objects_with_properties_contradicting" to
                                mapOf(
                                    "id" to maybePromote("string", "seal-one-hippity"),
                                    "name" to "James"
                                )
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
                            "union_of_objects_with_properties_contradicting" to null
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
        private val numberType = FieldType(NumberType, nullable = true)
        private val stringType = FieldType(StringType, nullable = true)
        private val timestamptzType = FieldType(TimestampTypeWithTimezone, nullable = true)
    }
}
