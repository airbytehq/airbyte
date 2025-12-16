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
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.dataflow.state.stats.StateAdditionalStatsStore
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.InputGlobalCheckpoint
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_INDEX_NAME
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AdditionalStats
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.math.BigDecimal
import java.math.BigInteger
import java.math.RoundingMode
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll
import org.junit.jupiter.api.assertThrows

// TODO kill Untyped, rename StronglyTyped -> AllTypes, and use the
//  SimpleTypeBehavior enum for all types.
//  https://github.com/airbytehq/airbyte-internal-issues/issues/12715
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
    /** Whether the destination supports numbers larger than 1e39-1 */
    val numberCanBeLarge: Boolean = true,
    /**
     * Clearly redundant with other fields on this struct. We should do some sort of refactor here.
     * Many warehouse destinations use a NUMERIC(38, 9) type for number columns. This flag enables a
     * test case to validate some specific rounding/truncation behavior for fixed-point numbers.
     */
    val numberIsFixedPointPrecision38Scale9: Boolean = false,
    /**
     * No effect unless [numberIsFixedPointPrecision38Scale9] is set.
     *
     * If your connector relies on the warehouse to truncate/round off numbers with too many decimal
     * places, and therefore does not populate an `airbyte_meta.changes` entry, you should enable
     * this flag.
     *
     * This is not best practice, but is compatible with historical behavior, and we don't have a
     * strong preference to enforce populating the `changes` list in this case.
     */
    val truncatedNumbersPopulateAirbyteMeta: Boolean = true,
    /** No effect unless [numberIsFixedPointPrecision38Scale9] is set. */
    val truncatedNumberRoundingMode: RoundingMode = RoundingMode.HALF_UP,
    /**
     * In some strongly-typed destinations, timetz columns are actually weakly typed. For example,
     * Bigquery writes timetz values into STRING columns, and doesn't actually validate that they
     * are valid timetz values.
     */
    val timeWithTimezoneBehavior: SimpleValueBehavior = SimpleValueBehavior.STRONGLY_TYPE,
) : AllTypesBehavior

data object Untyped : AllTypesBehavior

enum class SimpleValueBehavior {
    /**
     * The destination doesn't support this data type, so we just write a JSON field. We also don't
     * validate the value in any way.
     *
     * This is generally poor practice. Some older connectors use this behavior for legacy reasons,
     * but newer connectors should prefer [VALIDATE_AND_PASS_THROUGH].
     */
    PASS_THROUGH,

    /**
     * The destination doesn't support this data type, so we just write a JSON field. However, we
     * still validate that the value is valid before writing it to the destination.
     */
    VALIDATE_AND_PASS_THROUGH,

    /** The destination supports this data type natively. */
    STRONGLY_TYPE,
}

/**
 * Destinations may choose to handle nested objects/arrays in a few different ways.
 *
 * Note that this is _not_ the same as
 * [BasicFunctionalityIntegrationTest.stringifySchemalessObjects]. This enum is only used for
 * objects with an explicit, non-empty list of properties.
 */
enum class SchematizedNestedValueBehavior {
    /**
     * Nested objects are written without modification: undeclared fields are retained; values not
     * matching the schema are retained.
     */
    PASS_THROUGH,

    /**
     * Nested objects are written as structs: undeclared fields are dropped, and values not matching
     * the schema are nulled.
     */
    STRONGLY_TYPE,

    /**
     * Nested objects/arrays are JSON-serialized and written as strings. Similar to [PASS_THROUGH],
     * objects are written without modification.
     */
    STRINGIFY,
}

enum class UnionBehavior {
    /**
     * Values corresponding to union fields are passed through, regardless of whether they actually
     * match any of the union options.
     */
    PASS_THROUGH,

    /**
     * Union fields are turned into objects, with a `type` field indicating the selected union
     * option. For example, the value `42` in a union with an Integer option would be represented as
     * `{"type": "integer", "integer": 42}`.
     *
     * Values which do not match any union options are nulled.
     */
    PROMOTE_TO_OBJECT,

    /**
     * Union fields are JSON-serialized and written as strings. Similar to the [PASS_THROUGH]
     * option, no validation is performed.
     */
    STRINGIFY,
}

enum class UnknownTypesBehavior {
    NULL,

    /**
     * Values of unknown types are JSON-serialized. In particular, this means that a string `"foo"`
     * would be written to the destination as `"\"foo\""`.
     */
    SERIALIZE,

    /**
     * Values of unknown types are naively converted to string. String values are written as-is, and
     * other types are JSON-serialized.
     *
     * In most cases, we prefer [SERIALIZE] over [PASS_THROUGH], but there are some destinations
     * (e.g. blob storage writing JSONL) where this makes sense. Additionally, destination-s3 in CSV
     * mode does this for historical reasons.
     */
    PASS_THROUGH,

    /**
     * The sync is expected to fail on unrecognized types. We generally prefer to avoid this
     * behavior, but destination-s3 in avro/parquet mode does this for historical reasons.
     *
     * New connectors should generally try to use [SERIALIZE].
     */
    FAIL,
}

data class DedupBehavior(
    val cdcDeletionMode: CdcDeletionMode = CdcDeletionMode.HARD_DELETE,
) {
    enum class CdcDeletionMode {
        /**
         * CDC deletions are actual deletions; we completely drop the record from the destination.
         */
        HARD_DELETE,

        /**
         * CDC deletions are represented by simply upserting the deletion record to the destination.
         * This behavior is source-dependent, but typically results in nulling out all fields except
         * for the primary key(s), cursor, and any `_ab_cdc_*` fields.
         */
        SOFT_DELETE,
    }
}

abstract class BasicFunctionalityIntegrationTest(
    /** The config to pass into the connector, as a serialized JSON blob */
    configContents: String,
    val configSpecClass: Class<out ConfigurationSpecification>,
    dataDumper: DestinationDataDumper,
    destinationCleaner: DestinationCleaner,
    recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    nameMapper: NameMapper = NoopNameMapper,
    additionalMicronautEnvs: List<String> = emptyList(),
    micronautProperties: Map<Property, String> = emptyMap(),
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
     *
     * If set to `false`, we don't even run the schema change tests, under the presumption that the
     * destination doesn't have any interesting behavior in schema change scenarios.
     */
    val isStreamSchemaRetroactive: Boolean,
    /**
     * Similar to [isStreamSchemaRetroactive], but specifically for altering a column from UNKNOWN
     * to STRING.
     *
     * Destinations which represent UnknownType as a STRING column, and JSON-serialize all UNKNOWN
     * values, should set this to `false`. In these destinations, altering a column between
     * unknown/json will not be retroactive (because we have no way to recognize which columns were
     * STRING vs UNKNOWN).
     */
    val isStreamSchemaRetroactiveForUnknownTypeToString: Boolean = true,
    val dedupBehavior: DedupBehavior?,
    val stringifySchemalessObjects: Boolean,
    val stringifyUnionObjects: Boolean = false,
    val schematizedObjectBehavior: SchematizedNestedValueBehavior,
    val schematizedArrayBehavior: SchematizedNestedValueBehavior,
    val unionBehavior: UnionBehavior,
    val coercesLegacyUnions: Boolean = false,
    val supportFileTransfer: Boolean,
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
    /**
     * Some destination connectors commit data incrementally, but only when the stream is an append
     * one. When the running a schema change, the behavior might be different than append.
     */
    val commitDataIncrementallyOnAppend: Boolean = commitDataIncrementally,
    /**
     * The same concept as [commitDataIncrementally], but specifically describes how the connector
     * behaves when the destination contains no data at the start of the sync. Some destinations
     * commit incrementally during such an "initial" truncate refresh, then switch to committing
     * non-incrementally for subsequent truncates.
     *
     * (warehouse destinations with direct-load tables should set this to true).
     */
    val commitDataIncrementallyToEmptyDestinationOnAppend: Boolean =
        commitDataIncrementally || commitDataIncrementallyOnAppend,
    val commitDataIncrementallyToEmptyDestinationOnDedupe: Boolean =
        commitDataIncrementally || commitDataIncrementallyOnAppend,
    val allTypesBehavior: AllTypesBehavior,
    val unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    // If it simply isn't possible to represent a mismatched type on the wire (ie, protobuf).
    val mismatchedTypesUnrepresentable: Boolean = false,
    // When changing a column to a PK, some destination set the column to a default value.
    // This flag is addressing this behavior.
    val dedupChangeUsesDefault: Boolean = false,
    nullEqualsUnset: Boolean = false,
    configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
    // Which medium to use as your input source for the test
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    val testSpeedModeStatsEmission: Boolean = true,
    val useDataFlowPipeline: Boolean = false,
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = dataDumper,
        destinationCleaner = destinationCleaner,
        recordMangler = recordMangler,
        nameMapper = nameMapper,
        nullEqualsUnset = nullEqualsUnset,
        configUpdater = configUpdater,
        micronautProperties = micronautProperties,
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
    ) {

    // Update config with any replacements.  This may be necessary when using testcontainers.
    val updatedConfig = configUpdater.update(configContents)
    val parsedConfig = ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig)

    @Test
    open fun testOutOfOrderStateMessages() {
        if (
            dataChannelMedium != DataChannelMedium.SOCKET ||
                dataChannelFormat != DataChannelFormat.PROTOBUF
        ) {
            return
        }
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(stream)),
                listOf(
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 0,
                            additionalProperties =
                                mapOf(CHECKPOINT_INDEX_NAME to 5, CHECKPOINT_ID_NAME to "1"),
                        ),
                    ),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 0,
                            additionalProperties =
                                mapOf(CHECKPOINT_INDEX_NAME to 4, CHECKPOINT_ID_NAME to "2"),
                        ),
                    ),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 0,
                            additionalProperties =
                                mapOf(CHECKPOINT_INDEX_NAME to 3, CHECKPOINT_ID_NAME to "3"),
                        ),
                    ),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 0,
                            additionalProperties =
                                mapOf(CHECKPOINT_INDEX_NAME to 2, CHECKPOINT_ID_NAME to "4"),
                        ),
                    ),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 0,
                            additionalProperties =
                                mapOf(CHECKPOINT_INDEX_NAME to 1, CHECKPOINT_ID_NAME to "5"),
                        ),
                    ),
                ),
            )

        val stateMessages =
            messages
                .filter { it.type == AirbyteMessage.Type.STATE }
                .withIndex()
                .associate { (index, message) ->
                    index to
                        message.state.additionalProperties[CHECKPOINT_INDEX_NAME]!!
                            .toString()
                            .toInt()
                }
        assertEquals(5, stateMessages.size)

        stateMessages.forEach { state -> assertEquals(state.key + 1, state.value) }
    }

    @Test
    open fun testStateMessageBeforeRecords() {
        if (
            dataChannelMedium != DataChannelMedium.SOCKET ||
                dataChannelFormat != DataChannelFormat.PROTOBUF
        ) {
            return
        }
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(stream)),
                listOf(
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 2,
                            additionalProperties =
                                mapOf(
                                    CHECKPOINT_INDEX_NAME to 2,
                                    CHECKPOINT_ID_NAME to "partition_2"
                                ),
                        ),
                    ),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            unmappedNamespace = stream.unmappedNamespace,
                            unmappedName = stream.unmappedName,
                            blob =
                                io.airbyte.protocol.models.Jsons.jsonNode(
                                        mapOf("stream1" to "state"),
                                    )
                                    .toString(),
                            sourceRecordCount = 1,
                            additionalProperties =
                                mapOf(
                                    CHECKPOINT_INDEX_NAME to 1,
                                    CHECKPOINT_ID_NAME to "partition_1"
                                ),
                        ),
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 1}""",
                        emittedAtMs = 1234,
                        checkpointId = CheckpointId("partition_1"),
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 2}""",
                        emittedAtMs = 1234,
                        checkpointId = CheckpointId("partition_2"),
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 3}""",
                        emittedAtMs = 1234,
                        checkpointId = CheckpointId("partition_2"),
                    ),
                ),
            )

        val stateMessages =
            messages
                .filter { m -> m.type == AirbyteMessage.Type.STATE }
                .associateBy(
                    keySelector = {
                        it.state.additionalProperties[CHECKPOINT_INDEX_NAME]!!.toString().toInt()
                    },
                    valueTransform = { it.state.stream },
                )

        val stateMessagesOuter =
            messages
                .filter { m -> m.type == AirbyteMessage.Type.STATE }
                .associateBy(
                    keySelector = {
                        it.state.additionalProperties[CHECKPOINT_INDEX_NAME]!!.toString().toInt()
                    },
                    valueTransform = { it.state },
                )
        assertEquals(2, stateMessages.size)

        stateMessages[1]!!.also { state ->
            assertEquals(
                StreamDescriptor().withNamespace(randomizedNamespace).withName("test_stream"),
                state.streamDescriptor
            )

            assertEquals(
                io.airbyte.protocol.models.Jsons.jsonNode(
                    mapOf("stream1" to "state"),
                ),
                state.streamState
            )

            stateMessagesOuter[1]!!.also { outer ->
                assertEquals(
                    mapOf(
                        CHECKPOINT_ID_NAME to "partition_1",
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 56,
                        CHECKPOINT_INDEX_NAME to 1,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 1,
                    ),
                    outer.additionalProperties,
                )
                assertEquals(
                    AirbyteStateStats()
                        .withRecordCount(1.0)
                        .withAdditionalStats(expectedAdditionalStats()),
                    outer.destinationStats,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(1.0),
                    outer.sourceStats,
                )
            }
        }

        stateMessages[2]!!.also { state ->
            assertEquals(
                StreamDescriptor().withNamespace(randomizedNamespace).withName("test_stream"),
                state.streamDescriptor
            )

            assertEquals(
                io.airbyte.protocol.models.Jsons.jsonNode(
                    mapOf("stream1" to "state"),
                ),
                state.streamState
            )

            stateMessagesOuter[2]!!.also { outer ->
                assertEquals(
                    mapOf(
                        CHECKPOINT_ID_NAME to "partition_2",
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 168,
                        CHECKPOINT_INDEX_NAME to 2,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 3,
                    ),
                    outer.additionalProperties,
                )

                assertEquals(
                    AirbyteStateStats()
                        .withRecordCount(2.0)
                        .withAdditionalStats(expectedAdditionalStats()),
                    outer.destinationStats,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(2.0),
                    outer.sourceStats,
                )
            }
        }
    }

    @Test
    open fun testStreamStateTypes() {
        if (
            dataChannelMedium != DataChannelMedium.SOCKET ||
                dataChannelFormat != DataChannelFormat.PROTOBUF
        ) {
            return
        }
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream2 =
            DestinationStream(
                randomizedNamespace,
                "test_stream_2",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream3 =
            DestinationStream(
                randomizedNamespace,
                "test_stream_3",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(stream, stream2, stream3)),
                listOf(
                    InputRecord(
                        stream = stream,
                        data = """{"id": 1}""",
                        emittedAtMs = 1234,
                        checkpointId =
                            checkpointKeyForMedium(
                                    1,
                                    "stream_1_partition_1",
                                )
                                ?.checkpointId,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream.unmappedNamespace,
                        unmappedName = stream.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream1" to "state"),
                                )
                                .toString(),
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(1, "stream_1_partition_1"),
                    ),
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 2}""",
                        emittedAtMs = 1234,
                        checkpointId =
                            checkpointKeyForMedium(
                                    1,
                                    "stream_2_partition_1",
                                )
                                ?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 3}""",
                        emittedAtMs = 1234,
                        checkpointId =
                            checkpointKeyForMedium(
                                    1,
                                    "stream_2_partition_1",
                                )
                                ?.checkpointId,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream2.unmappedNamespace,
                        unmappedName = stream2.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream2" to "state"),
                                )
                                .toString(),
                        sourceRecordCount = 2,
                        checkpointKey = checkpointKeyForMedium(1, "stream_2_partition_1"),
                    ),
                    InputRecord(
                        stream = stream3,
                        data = """{"id": 4}""",
                        emittedAtMs = 1234,
                        checkpointId =
                            checkpointKeyForMedium(
                                    1,
                                    "stream_3_partition_1",
                                )
                                ?.checkpointId,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream3.unmappedNamespace,
                        unmappedName = stream3.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream3" to "state"),
                                )
                                .toString(),
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(1, "stream_3_partition_1"),
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 5}""",
                        emittedAtMs = 5678,
                        checkpointId =
                            checkpointKeyForMedium(
                                    2,
                                    "stream_1_partition_2",
                                )
                                ?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 6}""",
                        emittedAtMs = 5678,
                        checkpointId =
                            checkpointKeyForMedium(
                                    2,
                                    "stream_2_partition_2",
                                )
                                ?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream3,
                        data = """{"id": 7}""",
                        emittedAtMs = 5678,
                        checkpointId =
                            checkpointKeyForMedium(
                                    2,
                                    "stream_3_partition_2",
                                )
                                ?.checkpointId,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream.unmappedNamespace,
                        unmappedName = stream.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream1" to "state2"),
                                )
                                .toString(),
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(2, "stream_1_partition_2"),
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream2.unmappedNamespace,
                        unmappedName = stream2.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream2" to "state2"),
                                )
                                .toString(),
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(2, "stream_2_partition_2"),
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = stream3.unmappedNamespace,
                        unmappedName = stream3.unmappedName,
                        blob =
                            io.airbyte.protocol.models.Jsons.jsonNode(
                                    mapOf("stream3" to "state2"),
                                )
                                .toString(),
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(2, "stream_3_partition_2"),
                    ),
                ),
            )

        val stateMessages =
            messages.filter { m -> m.type == AirbyteMessage.Type.STATE }.map { it.state }

        assertEquals(6, stateMessages.size)

        val stateMessagesPerDescriptor =
            stateMessages.groupBy({ it.stream.streamDescriptor }, { it })

        val stateMessagesFromFirstStream =
            stateMessagesPerDescriptor[
                StreamDescriptor().withName("test_stream").withNamespace(randomizedNamespace),
            ]
        assertEquals(2, stateMessagesFromFirstStream!!.size)
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream1" to "state"),
            ),
            stateMessagesFromFirstStream[0].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0),
            stateMessagesFromFirstStream[0].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromFirstStream[0].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_1_partition_1",
                "committedBytesCount" to 65,
                "id" to 1,
                "committedRecordsCount" to 1,
            ),
            stateMessagesFromFirstStream[0].additionalProperties,
        )
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream1" to "state2"),
            ),
            stateMessagesFromFirstStream[1].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0),
            stateMessagesFromFirstStream[1].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromFirstStream[1].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_1_partition_2",
                "committedBytesCount" to 130,
                "id" to 2,
                "committedRecordsCount" to 2,
            ),
            stateMessagesFromFirstStream[1].additionalProperties,
        )

        val stateMessagesFromSecondStream =
            stateMessagesPerDescriptor[
                StreamDescriptor().withName("test_stream_2").withNamespace(randomizedNamespace),
            ]
        assertEquals(2, stateMessagesFromSecondStream!!.size)
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream2" to "state"),
            ),
            stateMessagesFromSecondStream[0].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(2.0),
            stateMessagesFromSecondStream[0].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(2.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromSecondStream[0].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_2_partition_1",
                "committedBytesCount" to 134,
                "id" to 1,
                "committedRecordsCount" to 2,
            ),
            stateMessagesFromSecondStream[0].additionalProperties,
        )
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream2" to "state2"),
            ),
            stateMessagesFromSecondStream[1].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0),
            stateMessagesFromSecondStream[1].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromSecondStream[1].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_2_partition_2",
                "committedBytesCount" to 201,
                "id" to 2,
                "committedRecordsCount" to 3,
            ),
            stateMessagesFromSecondStream[1].additionalProperties,
        )

        val stateMessagesFromThirdStream =
            stateMessagesPerDescriptor[
                StreamDescriptor().withName("test_stream_3").withNamespace(randomizedNamespace),
            ]
        assertEquals(2, stateMessagesFromThirdStream!!.size)
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream3" to "state"),
            ),
            stateMessagesFromThirdStream[0].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0),
            stateMessagesFromThirdStream[0].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromThirdStream[0].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_3_partition_1",
                "committedBytesCount" to 67,
                "id" to 1,
                "committedRecordsCount" to 1,
            ),
            stateMessagesFromThirdStream[0].additionalProperties,
        )
        assertEquals(
            io.airbyte.protocol.models.Jsons.jsonNode(
                mapOf("stream3" to "state2"),
            ),
            stateMessagesFromThirdStream[1].stream.streamState,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0),
            stateMessagesFromSecondStream[1].sourceStats,
        )
        assertEquals(
            AirbyteStateStats().withRecordCount(1.0).withAdditionalStats(expectedAdditionalStats()),
            stateMessagesFromSecondStream[1].destinationStats,
        )
        assertEquals(
            mapOf<String, Any>(
                "partition_id" to "stream_3_partition_2",
                "committedBytesCount" to 134,
                "id" to 2,
                "committedRecordsCount" to 2,
            ),
            stateMessagesFromThirdStream[1].additionalProperties,
        )
    }

    @Test
    open fun testCDCStateTypes() {
        if (
            dataChannelMedium != DataChannelMedium.SOCKET ||
                dataChannelFormat != DataChannelFormat.PROTOBUF
        ) {
            return
        }
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream2 =
            DestinationStream(
                randomizedNamespace,
                "test_stream_2",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream3 =
            DestinationStream(
                randomizedNamespace,
                "test_stream_3",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(stream, stream2, stream3)),
                listOf(
                    // record from snapshot
                    InputRecord(
                        stream = stream,
                        data = """{"id": 1}""",
                        emittedAtMs = 1234,
                        checkpointId = checkpointKeyForMedium(1, "partition_1")?.checkpointId,
                    ),
                    // record from snapshot
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 2}""",
                        emittedAtMs = 1234,
                        checkpointId = checkpointKeyForMedium(1, "partition_2")?.checkpointId,
                    ),
                    // record from binlog
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 3}""",
                        emittedAtMs = 1234,
                        checkpointId = checkpointKeyForMedium(1, "outer_partition")?.checkpointId,
                    ),
                    // record from binlog
                    InputRecord(
                        stream = stream3,
                        data = """{"id": 4}""",
                        emittedAtMs = 1234,
                        checkpointId = checkpointKeyForMedium(1, "outer_partition")?.checkpointId,
                    ),
                    InputGlobalCheckpoint(
                        sharedState =
                            io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                        checkpointKey = checkpointKeyForMedium(1, "outer_partition"),
                        streamStates =
                            listOf(
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream.unmappedNamespace,
                                    unmappedName = stream.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream1" to "state"),
                                        ),
                                    additionalProperties =
                                        linkedMapOf(
                                            CHECKPOINT_INDEX_NAME to 1,
                                            CHECKPOINT_ID_NAME to "partition_1",
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream2.unmappedNamespace,
                                    unmappedName = stream2.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream2" to "state"),
                                        ),
                                    additionalProperties =
                                        linkedMapOf(
                                            CHECKPOINT_INDEX_NAME to 1,
                                            CHECKPOINT_ID_NAME to "partition_2",
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream3.unmappedNamespace,
                                    unmappedName = stream3.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream3" to "state"),
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = "namespace-not-present-in-catalog",
                                    unmappedName = "stream-not-present-in-catalog",
                                    state = io.airbyte.protocol.models.Jsons.emptyObject(),
                                ),
                            ),
                        sourceRecordCount = 4,
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 5}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(2, "partition_5")?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 6}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(2, "partition_6")?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream3,
                        data = """{"id": 7}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(2, "partition_7")?.checkpointId,
                    ),
                    InputGlobalCheckpoint(
                        sharedState =
                            io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                        checkpointKey = checkpointKeyForMedium(2, "outer_partition_2"),
                        streamStates =
                            listOf(
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream.unmappedNamespace,
                                    unmappedName = stream.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream1" to "state"),
                                        ),
                                    additionalProperties =
                                        linkedMapOf(
                                            CHECKPOINT_INDEX_NAME to 2,
                                            CHECKPOINT_ID_NAME to "partition_5",
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream2.unmappedNamespace,
                                    unmappedName = stream2.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream2" to "state"),
                                        ),
                                    additionalProperties =
                                        linkedMapOf(
                                            CHECKPOINT_INDEX_NAME to 2,
                                            CHECKPOINT_ID_NAME to "partition_6",
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream3.unmappedNamespace,
                                    unmappedName = stream3.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream3" to "state"),
                                        ),
                                    additionalProperties =
                                        linkedMapOf(
                                            CHECKPOINT_INDEX_NAME to 2,
                                            CHECKPOINT_ID_NAME to "partition_7",
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = "namespace-not-present-in-catalog",
                                    unmappedName = "stream-not-present-in-catalog",
                                    state = io.airbyte.protocol.models.Jsons.emptyObject(),
                                ),
                            ),
                        sourceRecordCount = 3,
                    ),
                    InputRecord(
                        stream = stream,
                        data = """{"id": 8}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(3, "outer_partition_3")?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream2,
                        data = """{"id": 9}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(3, "outer_partition_3")?.checkpointId,
                    ),
                    InputRecord(
                        stream = stream3,
                        data = """{"id": 10}""",
                        emittedAtMs = 5678,
                        checkpointId = checkpointKeyForMedium(3, "outer_partition_3")?.checkpointId,
                    ),
                    InputGlobalCheckpoint(
                        sharedState =
                            io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                        checkpointKey = checkpointKeyForMedium(3, "outer_partition_3"),
                        streamStates =
                            listOf(
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream.unmappedNamespace,
                                    unmappedName = stream.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream1" to "state"),
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream2.unmappedNamespace,
                                    unmappedName = stream2.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream2" to "state"),
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = stream3.unmappedNamespace,
                                    unmappedName = stream3.unmappedName,
                                    state =
                                        io.airbyte.protocol.models.Jsons.jsonNode(
                                            mapOf("stream3" to "state"),
                                        ),
                                ),
                                CheckpointMessage.Checkpoint(
                                    unmappedNamespace = "namespace-not-present-in-catalog",
                                    unmappedName = "stream-not-present-in-catalog",
                                    state = io.airbyte.protocol.models.Jsons.emptyObject(),
                                ),
                            ),
                        sourceRecordCount = 3,
                    ),
                ),
            )

        val stateMessages =
            messages
                .filter { m -> m.type == AirbyteMessage.Type.STATE }
                .associateBy(
                    keySelector = {
                        it.state.additionalProperties[CHECKPOINT_INDEX_NAME]!!.toString().toInt()
                    },
                    valueTransform = { it.state.global },
                )

        val stateMessagesOuter =
            messages
                .filter { m -> m.type == AirbyteMessage.Type.STATE }
                .associateBy(
                    keySelector = {
                        it.state.additionalProperties[CHECKPOINT_INDEX_NAME]!!.toString().toInt()
                    },
                    valueTransform = { it.state },
                )

        val firstStream =
            StreamDescriptor().withName("test_stream").withNamespace(randomizedNamespace)
        val secondStream =
            StreamDescriptor().withName("test_stream_2").withNamespace(randomizedNamespace)
        val thirdStream =
            StreamDescriptor().withName("test_stream_3").withNamespace(randomizedNamespace)

        assertEquals(3, stateMessages.size)
        val firstStateMessage = stateMessages[1]!!

        firstStateMessage.also { state ->
            assertEquals(
                io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                state.sharedState,
            )

            val streamStatesMappedByStreamNames =
                state.streamStates.associateBy { it.streamDescriptor }

            assertEquals(4, streamStatesMappedByStreamNames.size)

            streamStatesMappedByStreamNames.also {
                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream1" to "state")),
                    it[firstStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 56,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 1,
                    ),
                    it[firstStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream2" to "state")),
                    it[secondStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 120,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 2,
                    ),
                    it[secondStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream3" to "state")),
                    it[thirdStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 62,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 1,
                    ),
                    it[thirdStream]!!.additionalProperties,
                )
            }

            stateMessagesOuter[1]!!.also { outer ->
                assertEquals(
                    mapOf(
                        CHECKPOINT_ID_NAME to "outer_partition",
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 238,
                        CHECKPOINT_INDEX_NAME to 1,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 4,
                    ),
                    outer.additionalProperties,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(4.0),
                    outer.destinationStats,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(4.0),
                    outer.sourceStats,
                )
            }
        }

        val secondStateMessage = stateMessages[2]!!
        secondStateMessage.also { state ->
            assertEquals(
                io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                state.sharedState,
            )

            val streamStatesMappedByStreamNames =
                state.streamStates.associateBy { it.streamDescriptor }

            assertEquals(4, streamStatesMappedByStreamNames.size)

            streamStatesMappedByStreamNames.also {
                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream1" to "state")),
                    it[firstStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 112,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 2,
                    ),
                    it[firstStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream2" to "state")),
                    it[secondStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 178,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 3,
                    ),
                    it[secondStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream3" to "state")),
                    it[thirdStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 120,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 2,
                    ),
                    it[thirdStream]!!.additionalProperties,
                )
            }

            stateMessagesOuter[2]!!.also { outer ->
                assertEquals(
                    mapOf(
                        CHECKPOINT_ID_NAME to "outer_partition_2",
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 410,
                        CHECKPOINT_INDEX_NAME to 2,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 7,
                    ),
                    outer.additionalProperties,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(3.0),
                    outer.destinationStats,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(3.0),
                    outer.sourceStats,
                )
            }
        }

        val thirdStateMessage = stateMessages[3]!!
        thirdStateMessage.also { state ->
            assertEquals(
                io.airbyte.protocol.models.Jsons.jsonNode(mapOf("shared" to "state")),
                state.sharedState,
            )

            val streamStatesMappedByStreamNames =
                state.streamStates.associateBy { it.streamDescriptor }

            assertEquals(4, streamStatesMappedByStreamNames.size)

            streamStatesMappedByStreamNames.also {
                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream1" to "state")),
                    it[firstStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 174,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 3,
                    ),
                    it[firstStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream2" to "state")),
                    it[secondStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 242,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 4,
                    ),
                    it[secondStream]!!.additionalProperties,
                )

                assertEquals(
                    io.airbyte.protocol.models.Jsons.jsonNode(mapOf("stream3" to "state")),
                    it[thirdStream]!!.streamState,
                )

                assertEquals(
                    mapOf(
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 184,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 3,
                    ),
                    it[thirdStream]!!.additionalProperties,
                )
            }

            stateMessagesOuter[3]!!.also { outer ->
                assertEquals(
                    mapOf(
                        CHECKPOINT_ID_NAME to "outer_partition_3",
                        CheckpointMessage.COMMITTED_BYTES_COUNT to 600,
                        CHECKPOINT_INDEX_NAME to 3,
                        CheckpointMessage.COMMITTED_RECORDS_COUNT to 10,
                    ),
                    outer.additionalProperties,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(3.0),
                    outer.destinationStats,
                )

                assertEquals(
                    AirbyteStateStats().withRecordCount(3.0),
                    outer.sourceStats,
                )
            }
        }
    }

    @Test
    open fun testBasicWrite() {
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val messages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    InputRecord(
                        stream = stream,
                        data = """{"id": 5678}""",
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
                            ),
                        checkpointId = checkpointKeyForMedium()?.checkpointId
                    ),
                    InputStreamCheckpoint(
                        unmappedName = stream.unmappedName,
                        unmappedNamespace = stream.unmappedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(),
                    )
                ),
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }

        // Only used for speed mode (unnecessary to test if dest does not support speed)
        val expectedBytes =
            if (testSpeedModeStatsEmission) expectedBytesForMediumAndFormat(214L, 234L, 56L)
            else null

        assertAll(
            {
                assertEquals(
                    1,
                    stateMessages.size,
                    "Expected to receive exactly one state message, got ${stateMessages.size} ($stateMessages)"
                )

                val asProtocolMessage =
                    StreamCheckpoint(
                            unmappedName = stream.unmappedName,
                            unmappedNamespace = stream.unmappedNamespace,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 1,
                            destinationRecordCount = 1,
                            checkpointKey = checkpointKeyForMedium(),
                            totalRecords = 1L,
                            totalBytes = expectedBytes,
                            additionalStats =
                                if (useDataFlowPipeline)
                                    StateAdditionalStatsStore.ObservabilityMetrics.entries
                                        .associate { it.metricName to 0.0 }
                                        .toMutableMap()
                                else mutableMapOf(),
                        )
                        .asProtocolMessage()
                assertEquals(
                    Jsons.readValue(
                        Jsons.writeValueAsBytes(asProtocolMessage),
                        AirbyteMessage::class.java
                    ),
                    stateMessages.first(),
                )
            },
            {
                if (verifyDataWriting) {
                    dumpAndDiffRecords(
                        ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig),
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to 5678),
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

    @Test
    open fun testBasicWriteFile() {
        assumeTrue(supportFileTransfer)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream_file",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                isFileBased = true,
                includeFiles = true,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )

        val sourcePath = "path/to/file"
        // these must match the values hard-coded in DockerizedDestination
        val stagingDir = "tmp"
        val fileName = "test_file"
        val fileContents = "123"

        val fileReference =
            AirbyteRecordMessageFileReference()
                .withSourceFileRelativePath(sourcePath)
                .withStagingFileUrl("/$stagingDir/$fileName")
                .withFileSizeBytes(1234L)

        val input =
            InputRecord(
                stream = stream,
                data = """{"id": 5678}""",
                emittedAtMs = 1234,
                changes = mutableListOf(),
                fileReference = fileReference,
                checkpointId = checkpointKeyForMedium()?.checkpointId
            )

        val messages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    input,
                    InputStreamCheckpoint(
                        unmappedName = stream.unmappedName,
                        unmappedNamespace = stream.unmappedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(),
                    )
                ),
                useFileTransfer = true,
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll({
            assertEquals(
                1,
                stateMessages.size,
                "Expected to receive exactly one state message, got ${stateMessages.size} ($stateMessages)"
            )
            assertEquals(
                StreamCheckpoint(
                        unmappedName = stream.unmappedName,
                        unmappedNamespace = stream.unmappedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                        destinationRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium(),
                        // Files doesn't need these, but they get added anyway
                        totalRecords = 1,
                        totalBytes = 267L
                    )
                    .asProtocolMessage()
                    .serializeToString(),
                stateMessages.first().serializeToString()
            )
        })

        val config = ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig)
        val fileContent = dataDumper.dumpFile(config, stream)

        assertEquals(fileContents, fileContent[sourcePath])
    }

    /**
     * Runs a sync, kills it before finishing, then asserts second sync finishes moving the data to
     * the final table.
     *
     * Tests any sort of 2 phase commit write operation recovers from failure.
     */
    @Test
    open fun testMidSyncCheckpointingStreamState(): Unit =
        runBlocking(Dispatchers.IO) {
            assumeTrue(verifyDataWriting)
            val stream =
                DestinationStream(
                    randomizedNamespace,
                    "test_stream",
                    Append,
                    ObjectType(linkedMapOf("id" to intType)),
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 42,
                    namespaceMapper = namespaceMapperForMedium(),
                    tableSchema = emptyTableSchema,
                )
            val stateMessage =
                runSyncUntilStateAckAndExpectFailure(
                    this@BasicFunctionalityIntegrationTest.updatedConfig,
                    stream,
                    listOf(
                        InputRecord(
                            stream = stream,
                            data = """{"id": 12}""",
                            emittedAtMs = 1234,
                            checkpointId = checkpointKeyForMedium()?.checkpointId
                        )
                    ),
                    StreamCheckpoint(
                        unmappedName = stream.unmappedName,
                        unmappedNamespace = stream.unmappedNamespace,
                        blob = """{"foo": "bar1"}""",
                        sourceRecordCount = 1,
                        checkpointKey = checkpointKeyForMedium()
                    ),
                    syncEndBehavior = UncleanSyncEndBehavior.KILL,
                )
            runSync(this@BasicFunctionalityIntegrationTest.updatedConfig, stream, emptyList())

            val streamName = stateMessage.stream.streamDescriptor.name
            val streamNamespace = stateMessage.stream.streamDescriptor.namespace
            // basic state message checks - this is mostly just exercising the CDK itself,
            // but is cheap and easy to do.
            assertAll(
                { assertEquals(randomizedNamespace, streamNamespace) },
                {
                    assertEquals(
                        streamName,
                        "test_stream",
                        "Expected stream name to be test_stream, got $streamName"
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
                    assertEquals(
                        """{"foo": "bar1"}""".deserializeToNode(),
                        stateMessage.stream.streamState
                    )
                }
            )
            if (verifyDataWriting) {
                dumpAndDiffRecords(
                    parsedConfig,
                    listOf(
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 0,
                            data = mapOf("id" to 12),
                            airbyteMeta = OutputRecord.Meta(syncId = 42)
                        )
                    ),
                    stream,
                    primaryKey = listOf(listOf("id")),
                    cursor = null,
                    allowUnexpectedRecord = true,
                )
            }
        }

    @Test
    open fun testNamespaces() {
        assumeTrue(verifyDataWriting)
        fun makeStream(namespace: String?) =
            DestinationStream(
                // We need to randomize the stream name for destinations which support
                // namespace=null natively.
                // Otherwise, multiple test runs would write to `<null>.test_stream`.
                // Now, they instead write to `<null>.test_stream_test20250123abcd`.
                namespace,
                "test_stream_$randomizedNamespace",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream1 = makeStream(randomizedNamespace + "_1")
        val stream2 = makeStream(randomizedNamespace + "_2")
        val streamWithDefaultNamespace = makeStream(null)
        val (configWithRandomizedDefaultNamespace, actualDefaultNamespace) =
            configUpdater.setDefaultNamespace(updatedConfig, randomizedNamespace + "_default")
        runSync(
            configWithRandomizedDefaultNamespace,
            DestinationCatalog(
                listOf(
                    stream1,
                    stream2,
                    streamWithDefaultNamespace,
                )
            ),
            listOf(
                InputRecord(
                    stream = stream1,
                    data = """{"id": 1234}""",
                    emittedAtMs = 1234,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream = stream2,
                    data = """{"id": 5678}""",
                    emittedAtMs = 1234,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream = streamWithDefaultNamespace,
                    data = """{"id": 91011}""",
                    emittedAtMs = 1234,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
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
            },
            {
                dumpAndDiffRecords(
                    parsedConfig,
                    listOf(
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 0,
                            data = mapOf("id" to 91011),
                            airbyteMeta = OutputRecord.Meta(syncId = 42)
                        )
                    ),
                    streamWithDefaultNamespace.copy(unmappedNamespace = actualDefaultNamespace),
                    listOf(listOf("id")),
                    cursor = null
                )
            }
        )
    }

    @Test
    open fun testFunkyCharacters() {
        assumeTrue(verifyDataWriting)
        fun makeStream(
            name: String,
            schema: LinkedHashMap<String, FieldType> = linkedMapOf("id" to intType),
            namespaceSuffix: String = "",
        ) =
            DestinationStream(
                randomizedNamespace + namespaceSuffix,
                name,
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
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
                    makeStream("stream_with_spécial_character"),
                    makeStream("stream_name_with_operator+1"),
                    makeStream("stream_name_with_numbers_123"),
                    makeStream("1stream_with_a_leading_number"),
                    makeStream("c'est une belle histoire,./<>?'\";[]\\:{}|`~!@#\$%^&*()_+-="),
                    makeStream(
                        "stream_with_edge_case_field_names_and_values",
                        linkedMapOf(
                            "id" to intType,
                            "fieldWithCamelCase" to stringType,
                            "field_with_underscore" to stringType,
                            "FIELD_WITH_ALL_CAPS" to stringType,
                            "field_with_spécial_character" to stringType,
                            "field_name_with_operator+1" to stringType,
                            "field_name_with_numbers_123" to stringType,
                            "1field_with_a_leading_number" to stringType,
                            // "order" is a reserved word in many sql engines
                            "order" to stringType,
                            "ProperCase" to stringType,
                            "Foo.Bar" to stringType,
                        )
                    ),
                    // this is apparently trying to test for reserved words?
                    // https://github.com/airbytehq/airbyte/pull/1753
                    makeStream(
                        "groups",
                        linkedMapOf("id" to intType, "authorization" to stringType)
                    ),
                    makeStream(
                        "streamWithSpecialCharactersInNamespace",
                        namespaceSuffix = "_spøcial"
                    ),
                    makeStream("streamWithOperatorInNamespace", namespaceSuffix = "_operator-1"),
                )
            )
        // For each stream, generate a record containing every field in the schema.
        // The id field is always 42, and the string fields are always "foo\nbar".
        val messages =
            catalog.streams.map { stream ->
                InputRecord(
                    stream,
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
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            }
        runSync(updatedConfig, catalog, messages)
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

    /**
     * [testFunkyCharacters] runs using APPEND streams, so it can run on all destinations. But we
     * should also test that funky characters in the PK/cursor behave correctly.
     *
     * This test just runs a single DEDUP stream, whose PK+cursor include various special
     * characters.
     */
    @Test
    open fun testFunkyCharactersDedup() {
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                importType =
                    Dedupe(
                        // the actual string here is id~!@#$%^&*()`[]{}|;':",./<>?
                        // note: no `\` character, because it causes significant problems in some
                        // destinations (T+D destinations with noncompliant JSONPath
                        // implementations,
                        // e.g. bigquery)
                        primaryKey = listOf(listOf("id~!@#\$%^&*()`[]{}|;':\",./<>?")),
                        cursor = listOf("updated_at~!@#$%^&*()`[]{}|;':\",./<>?"),
                    ),
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id~!@#\$%^&*()`[]{}|;':\",./<>?" to intType,
                                "updated_at~!@#\$%^&*()`[]{}|;':\",./<>?" to timestamptzType,
                                "name~!@#\$%^&*()`[]{}|;':\",./<>?" to stringType,
                            )
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                    {
                      "id~!@#${'$'}%^&*()`[]{}|;':\",./<>?": 1,
                      "updated_at~!@#${'$'}%^&*()`[]{}|;':\",./<>?": "2000-01-01T00:00:00Z",
                      "name~!@#${'$'}%^&*()`[]{}|;':\",./<>?": "Alice1"
                    }""".trimIndent(),
                    emittedAtMs = 1000,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
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
                            "id~!@#\$%^&*()`[]{}|;':\",./<>?" to 1,
                            "updated_at~!@#\$%^&*()`[]{}|;':\",./<>?" to
                                TimestampWithTimezoneValue("2000-01-01T00:00:00Z"),
                            "name~!@#\$%^&*()`[]{}|;':\",./<>?" to "Alice1",
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id~!@#\$%^&*()`[]{}|;':\",./<>?")),
            cursor = listOf("updated_at~!@#$%^&*()`[]{}|;':\",./<>?"),
        )
    }

    @Test
    open fun testTruncateRefresh() {
        assumeTrue(verifyDataWriting)
        fun makeStream(generationId: Long, minimumGenerationId: Long, syncId: Long) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId,
                minimumGenerationId,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream =
            makeStream(
                generationId = 12,
                minimumGenerationId = 0,
                syncId = 42,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream = stream,
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )

        val finalStream = makeStream(generationId = 13, minimumGenerationId = 13, syncId = 43)
        // start a truncate refresh, but emit INCOMPLETE.
        // This should retain the existing data, and maybe insert the new record.
        runSyncUntilStateAckAndExpectFailure(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    stream = stream,
                    """{"id": 42, "name": "second_value"}""",
                    emittedAtMs = 2345,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            ),
            StreamCheckpoint(
                unmappedName = stream.unmappedName,
                unmappedNamespace = stream.unmappedNamespace,
                blob = """{}""",
                sourceRecordCount = 1,
                checkpointKey = checkpointKeyForMedium(),
            ),
            syncEndBehavior = UncleanSyncEndBehavior.TERMINATE_WITH_NO_STREAM_STATUS,
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOfNotNull(
                // first record is still present
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 12,
                    data = mapOf("id" to 42, "name" to "first_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                if (commitDataIncrementally) {
                    OutputRecord(
                        extractedAt = 2345,
                        generationId = 13,
                        data = mapOf("id" to 42, "name" to "second_value"),
                        airbyteMeta = OutputRecord.Meta(syncId = 43),
                    )
                } else {
                    null
                }
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )

        // finish the truncate. This should now delete the first sync's data,
        // and definitely insert the second+third syncs' data.
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    stream = stream,
                    """{"id": 42, "name": "third_value"}""",
                    emittedAtMs = 3456,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // retain the second+third records
                OutputRecord(
                    extractedAt = 2345,
                    generationId = 13,
                    data = mapOf("id" to 42, "name" to "second_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                ),
                OutputRecord(
                    extractedAt = 3456,
                    generationId = 13,
                    data = mapOf("id" to 42, "name" to "third_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                ),
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    /**
     * Some destinations make complicated changes based on the sync mode, e.g. Bigquery changing the
     * table's clustering config. Verify that we can do those changes across truncates.
     *
     * This test validates we can finish a truncate refresh when the import type changes between
     * runs.
     */
    @Test
    open fun testTruncateRefreshChangeSyncMode() {
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)
        fun makeStream(
            generationId: Long,
            minimumGenerationId: Long,
            syncId: Long,
            importType: ImportType
        ) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                importType,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId,
                minimumGenerationId,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream =
            makeStream(
                generationId = 12,
                minimumGenerationId = 12,
                syncId = 42,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
            )
        // start a truncate refresh in DEDUPE mode, but emit INCOMPLETE.
        runSyncUntilStateAckAndExpectFailure(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream = stream,
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            ),
            StreamCheckpoint(
                unmappedName = stream.unmappedName,
                unmappedNamespace = stream.unmappedNamespace,
                blob = """{}""",
                sourceRecordCount = 1,
                checkpointKey = checkpointKeyForMedium(),
            ),
            syncEndBehavior = UncleanSyncEndBehavior.TERMINATE_WITH_NO_STREAM_STATUS,
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOfNotNull(
                if (commitDataIncrementally || commitDataIncrementallyToEmptyDestinationOnDedupe) {
                    OutputRecord(
                        extractedAt = 1234,
                        generationId = 12,
                        data = mapOf("id" to 42, "name" to "first_value"),
                        airbyteMeta = OutputRecord.Meta(syncId = 42),
                    )
                } else {
                    null
                }
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )

        // start (and complete) a new truncate in APPEND mode.
        // This should now delete the first sync's data, and insert the new record.
        val finalStream =
            makeStream(
                generationId = 13,
                minimumGenerationId = 13,
                syncId = 43,
                Append,
            )
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    stream = stream,
                    """{"id": 43, "name": "second_value"}""",
                    emittedAtMs = 2345,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 2345,
                    generationId = 13,
                    data = mapOf("id" to 43, "name" to "second_value"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                ),
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
        val stream1 =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            InputRecord(
                stream1,
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
                checkpointId = checkpointKeyForMedium()?.checkpointId
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
                        "updated_at" to TimestampWithTimezoneValue(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        // Run a normal sync with nonempty data
        runSync(
            updatedConfig,
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
        // Run a sync, but emit a status incomplete. This should not delete any existing data.
        runSyncUntilStateAckAndExpectFailure(
            updatedConfig,
            stream2,
            listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
            StreamCheckpoint(
                unmappedName = stream2.unmappedName,
                unmappedNamespace = stream2.unmappedNamespace,
                blob = """{}""",
                sourceRecordCount = 1,
                checkpointKey = checkpointKeyForMedium(),
            ),
            syncEndBehavior = UncleanSyncEndBehavior.KILL,
        )
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
            updatedConfig,
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
            allowUnexpectedRecord = true,
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
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            InputRecord(
                stream,
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
                checkpointId = checkpointKeyForMedium()?.checkpointId
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
                        "updated_at" to TimestampWithTimezoneValue(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        // Run a sync, but emit a stream status incomplete.
        runSyncUntilStateAckAndExpectFailure(
            updatedConfig,
            stream,
            listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
            StreamCheckpoint(
                unmappedName = stream.unmappedName,
                unmappedNamespace = stream.unmappedNamespace,
                blob = """{}""",
                sourceRecordCount = 1,
                checkpointKey = checkpointKeyForMedium(),
            ),
            syncEndBehavior = UncleanSyncEndBehavior.KILL,
        )
        dumpAndDiffRecords(
            parsedConfig,
            if (commitDataIncrementallyToEmptyDestinationOnAppend) {
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
            updatedConfig,
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
            allowUnexpectedRecord = true,
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
    @Disabled("Still flaky")
    open fun resumeAfterCancelledTruncate() {
        assumeTrue(verifyDataWriting)
        val stream1 =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeInputRecord(id: Int, updatedAt: String, extractedAt: Long) =
            InputRecord(
                stream1,
                """{"id": $id, "updated_at": "$updatedAt", "name": "foo_${id}_$extractedAt"}""",
                emittedAtMs = extractedAt,
                checkpointId = checkpointKeyForMedium()?.checkpointId
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
                        "updated_at" to TimestampWithTimezoneValue(updatedAt),
                        "name" to "foo_${id}_$extractedAt",
                    ),
                airbyteMeta = OutputRecord.Meta(syncId = syncId),
            )
        // Run a normal sync with nonempty data
        runSync(
            updatedConfig,
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
        // Run a sync, but emit a stream status incomplete. This should not delete any existing
        // data.
        runSyncUntilStateAckAndExpectFailure(
            updatedConfig,
            stream2,
            listOf(makeInputRecord(1, "2024-01-23T02:00:00Z", 200)),
            StreamCheckpoint(
                unmappedName = stream2.unmappedName,
                unmappedNamespace = stream2.unmappedNamespace,
                blob = """{}""",
                sourceRecordCount = 1,
                checkpointKey = checkpointKeyForMedium(),
            ),
            syncEndBehavior = UncleanSyncEndBehavior.KILL,
        )
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
            updatedConfig,
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
            allowUnexpectedRecord = true,
        )
    }

    @Test
    open fun testAppend() {
        assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream = makeStream(syncId = 42)
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        val finalStream = makeStream(syncId = 43)
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    finalStream,
                    """{"id": 42, "name": "second_value"}""",
                    emittedAtMs = 5678L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
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
                    extractedAt = 5678,
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
        assumeTrue(isStreamSchemaRetroactive)
        fun makeStream(syncId: Long, schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream =
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "to_change" to intType)
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{"id": 42, "to_drop": "val1", "to_change": 42}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        val finalStream =
            makeStream(
                syncId = 43,
                linkedMapOf("id" to intType, "to_change" to stringType, "to_add" to stringType)
            )
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    finalStream,
                    """{"id": 42, "to_change": "val2", "to_add": "val3"}""",
                    emittedAtMs = 2345,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    // the first sync's record has to_change modified to a string,
                    // and to_drop is gone completely
                    data = mapOf("id" to 42, "to_change" to "42"),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 2345,
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

    /**
     * In many databases/warehouses, changing a column to/from JSON is nontrivial. This test runs
     * syncs to execute that schema change (under the assumption that UnknownType is rendered as a
     * JSON column).
     */
    @Test
    open fun testAppendJsonSchemaEvolution() {
        assumeTrue(verifyDataWriting)
        assumeTrue(isStreamSchemaRetroactive)
        assumeTrue(isStreamSchemaRetroactiveForUnknownTypeToString)
        fun makeStream(schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )

        val stream1 =
            makeStream(linkedMapOf("id" to intType, "a" to unknownType, "b" to stringType))
        runSync(
            updatedConfig,
            stream1,
            listOf(
                InputRecord(
                    stream1,
                    """{"id": 42, "a": "foo1", "b": "bar1"}""",
                    emittedAtMs = 100,
                ),
            ),
        )

        // note: `a` is changed from unknown -> string; `b` is changed from string -> unknown
        val stream2 =
            makeStream(linkedMapOf("id" to intType, "a" to stringType, "b" to unknownType))
        runSync(
            updatedConfig,
            stream2,
            listOf(
                InputRecord(
                    stream2,
                    """{"id": 43, "a": "foo2", "b": "bar2"}""",
                    emittedAtMs = 200,
                )
            )
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // the values are always strings, the only change is how the destination
                // represents them.
                OutputRecord(
                    extractedAt = 100,
                    generationId = 0,
                    data = mapOf("id" to 42, "a" to "foo1", "b" to "bar1"),
                    airbyteMeta = OutputRecord.Meta(syncId = 0),
                ),
                OutputRecord(
                    extractedAt = 200,
                    generationId = 0,
                    data = mapOf("id" to 43, "a" to "foo2", "b" to "bar2"),
                    airbyteMeta = OutputRecord.Meta(syncId = 0),
                )
            ),
            stream2,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    /**
     * Some destinations have better support for schema evolution in single-generation truncate
     * syncs. For example, if a destination imposes limitations on column type changes, we can
     * actually ignore those limits in a truncate sync (because we're dropping all older data
     * anyway).
     */
    @Test
    open fun testOverwriteSchemaEvolution() {
        assumeTrue(verifyDataWriting)
        fun makeStream(
            syncId: Long,
            schema: LinkedHashMap<String, FieldType>,
            generationId: Long,
            minimumGenerationId: Long,
        ) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(schema),
                generationId = generationId,
                minimumGenerationId = minimumGenerationId,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream =
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "to_change" to intType),
                generationId = 1,
                minimumGenerationId = 0,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{"id": 42, "to_drop": "val1", "to_change": 42}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        val changedStream =
            makeStream(
                syncId = 43,
                linkedMapOf("id" to intType, "to_change" to stringType, "to_add" to stringType),
                generationId = 2,
                minimumGenerationId = 2,
            )
        runSync(
            updatedConfig,
            changedStream,
            listOf(
                InputRecord(
                    changedStream,
                    """{"id": 42, "to_change": "val2", "to_add": "val3"}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 2,
                    data = mapOf("id" to 42, "to_change" to "val2", "to_add" to "val3"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            changedStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            reason = "Records were incorrect when trying to change the schema."
        )

        // Run a third sync, to verify that the schema is stable after evolution
        // (this is relevant for e.g. iceberg, where every column has an ID,
        // and we need to be able to match the new columns to their ID)
        val finalStream = changedStream.copy(minimumGenerationId = 0, syncId = 44)
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    finalStream,
                    """{"id": 42, "to_change": "val4", "to_add": "val5"}""",
                    emittedAtMs = 5678L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 2,
                    data = mapOf("id" to 42, "to_change" to "val2", "to_add" to "val3"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                ),
                OutputRecord(
                    extractedAt = 5678,
                    generationId = 2,
                    data = mapOf("id" to 42, "to_change" to "val4", "to_add" to "val5"),
                    airbyteMeta = OutputRecord.Meta(syncId = 44),
                ),
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
            reason = "Records were incorrect after running a second sync with the updated schema."
        )
    }

    private fun baseTestDedup(
        idType: AirbyteType,
        idValue: Any?,
    ) {
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)
        fun makeStream(syncId: Long) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("id1"), listOf("id2")),
                        cursor = listOf("updated_at"),
                    ),
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id1" to FieldType(idType, nullable = false),
                                "id2" to intType,
                                "updated_at" to timestamptzType,
                                "name" to stringType,
                                "_ab_cdc_deleted_at" to timestamptzType,
                            )
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val sync1Stream = makeStream(syncId = 42)
        fun makeRecord(data: String, extractedAt: Long) =
            InputRecord(
                sync1Stream,
                data,
                emittedAtMs = extractedAt,
                checkpointId = checkpointKeyForMedium()?.checkpointId
            )
        runSync(
            updatedConfig,
            sync1Stream,
            listOf(
                // emitted_at:1000 is equal to 1970-01-01 00:00:01Z.
                // This obviously makes no sense in relation to updated_at being in the year 2000,
                // but that's OK because (from destinations POV) updated_at has no relation to
                // extractedAt.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 200, "updated_at": "2000-01-01T00:00:00Z", "name": "Alice1", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 1000,
                ),
                // Emit a second record for id=(1,200) with a different updated_at.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 200, "updated_at": "2000-01-01T00:01:00Z", "name": "Alice2", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 1000,
                ),
                // Emit a record with no _ab_cdc_deleted_at field. CDC sources typically emit an
                // explicit null, but we should handle both cases.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 201, "updated_at": "2000-01-01T00:02:00Z", "name": "Bob1"}""",
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
                            "id1" to idValue,
                            "id2" to 200,
                            "updated_at" to TimestampWithTimezoneValue("2000-01-01T00:01:00Z"),
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
                            "id1" to idValue,
                            "id2" to 201,
                            "updated_at" to TimestampWithTimezoneValue("2000-01-01T00:02:00Z"),
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
            updatedConfig,
            sync2Stream,
            listOf(
                // Update both Alice and Bob
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 200, "updated_at": "2000-01-02T00:00:00Z", "name": "Alice3", "_ab_cdc_deleted_at": null}""",
                    extractedAt = 2000,
                ),
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 201, "updated_at": "2000-01-02T00:00:00Z", "name": "Bob2"}""",
                    extractedAt = 2000,
                ),
                // And delete Bob. Again, T+D doesn't check the actual _value_ of deleted_at (i.e.
                // the fact that it's in the past is irrelevant). It only cares whether deleted_at
                // is non-null. So the destination should delete Bob.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 201, "updated_at": "2000-01-02T00:01:00Z", "_ab_cdc_deleted_at": "1970-01-01T00:00:00Z"}""",
                    extractedAt = 2000,
                ),
                // insert + delete Charlie within a single sync.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 202, "updated_at": "2000-01-02T00:00:00Z", "name": "Charlie1"}""",
                    extractedAt = 2000,
                ),
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 202, "updated_at": "2000-01-02T00:01:00Z", "_ab_cdc_deleted_at": "1970-01-01T00:00:00Z"}""",
                    extractedAt = 2000,
                ),
                // delete some nonexistent record - this is incoherent, but we should behave
                // reasonably.
                makeRecord(
                    """{"id1": ${idValue.serializeToString()}, "id2": 203, "updated_at": "2000-01-02T00:01:00Z", "_ab_cdc_deleted_at": "1970-01-01T00:00:00Z"}""",
                    extractedAt = 2000,
                ),
            ),
        )
        val deletedRecords =
            when (dedupBehavior!!.cdcDeletionMode) {
                // in hard deletes mode, we drop Bob
                DedupBehavior.CdcDeletionMode.HARD_DELETE -> emptyList()
                // in soft deletes mode, we just take the deletion record wholesale.
                // note that we just upsert the record directly, without retaining any previous
                // values. I.e. the `name` field is null, because the final records have null name.
                DedupBehavior.CdcDeletionMode.SOFT_DELETE ->
                    listOf(
                        OutputRecord(
                            extractedAt = 2000,
                            generationId = 42,
                            data =
                                mapOf(
                                    "id1" to idValue,
                                    "id2" to 201,
                                    "updated_at" to
                                        TimestampWithTimezoneValue("2000-01-02T00:01:00Z"),
                                    "_ab_cdc_deleted_at" to
                                        TimestampWithTimezoneValue("1970-01-01T00:00:00Z"),
                                ),
                            airbyteMeta = OutputRecord.Meta(syncId = 43),
                        ),
                        OutputRecord(
                            extractedAt = 2000,
                            generationId = 42,
                            data =
                                mapOf(
                                    "id1" to idValue,
                                    "id2" to 202,
                                    "updated_at" to
                                        TimestampWithTimezoneValue("2000-01-02T00:01:00Z"),
                                    "_ab_cdc_deleted_at" to
                                        TimestampWithTimezoneValue("1970-01-01T00:00:00Z"),
                                ),
                            airbyteMeta = OutputRecord.Meta(syncId = 43),
                        ),
                        OutputRecord(
                            extractedAt = 2000,
                            generationId = 42,
                            data =
                                mapOf(
                                    "id1" to idValue,
                                    "id2" to 203,
                                    "updated_at" to
                                        TimestampWithTimezoneValue("2000-01-02T00:01:00Z"),
                                    "_ab_cdc_deleted_at" to
                                        TimestampWithTimezoneValue("1970-01-01T00:00:00Z"),
                                ),
                            airbyteMeta = OutputRecord.Meta(syncId = 43),
                        ),
                    )
            }
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // Alice still exists (and has been updated to the latest version), and Bob is
                // deleted.
                OutputRecord(
                    extractedAt = 2000,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to idValue,
                            "id2" to 200,
                            "updated_at" to TimestampWithTimezoneValue("2000-01-02T00:00:00Z"),
                            "name" to "Alice3",
                            "_ab_cdc_deleted_at" to null
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ) + deletedRecords,
            sync2Stream,
            primaryKey = listOf(listOf("id1"), listOf("id2")),
            cursor = listOf("updated_at"),
        )
    }

    @Test
    open fun testDedup() {
        baseTestDedup(IntegerType, idValue = 1)
    }

    @Test
    open fun testDedupWithStringKey() {
        baseTestDedup(StringType, idValue = "9cf974de-52cf-4194-9f3d-7efa76ba4d84")
    }

    @Test
    open fun testDedupNoCursor() {
        assumeTrue(verifyDataWriting && dedupBehavior != null)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    data = """{"id": 1234, "name": "a"}""",
                    emittedAtMs = 1234,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
            ),
        )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    data = """{"id": 1234, "name": "b"}""",
                    emittedAtMs = 5678,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 5678,
                    generationId = 0,
                    data = mapOf("id" to 1234, "name" to "b"),
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = emptyList()),
                ),
            ),
            stream,
            listOf(listOf("id")),
            cursor = null,
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
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)
        fun makeStream(cursor: String) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val stream1 = makeStream("cursor1")
        fun makeRecord(stream: DestinationStream, cursorName: String, emittedAtMs: Long) =
            InputRecord(
                stream,
                data = """{"id": 1, "$cursorName": 1, "name": "foo_$cursorName"}""",
                emittedAtMs = emittedAtMs,
                checkpointId = checkpointKeyForMedium()?.checkpointId
            )
        runSync(
            updatedConfig,
            stream1,
            listOf(makeRecord(stream1, "cursor1", emittedAtMs = 100)),
        )
        val stream2 = makeStream("cursor2")
        runSync(updatedConfig, stream2, listOf(makeRecord(stream2, "cursor2", emittedAtMs = 200)))
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 200,
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

    /**
     * This is a bit of an edge case, but we should handle it regardless. If the user configures a
     * primary key, then changes it (e.g. they realize that their composite key doesn't need to
     * include a certain column), we should do _something_ reasonable.
     *
     * Intentionally not doing a complex scenario here; users should probably just truncate refresh
     * if they want to do this. Just assert that if we upsert a record after changing the PK, the
     * upsert looks correct.
     */
    @Test
    open fun testDedupChangePk() {
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)
        fun makeStream(secondPk: String) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Dedupe(
                    primaryKey = listOf(listOf("id1"), listOf(secondPk)),
                    cursor = listOf("updated_at"),
                ),
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id1" to intType,
                            "id2" to intType,
                            "id3" to intType,
                            "updated_at" to intType,
                            "name" to stringType,
                        )
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeRecord(stream: DestinationStream, secondPk: String, emittedAtMs: Long) =
            InputRecord(
                stream,
                data =
                    """{"id1": 1, "$secondPk": 200, "updated_at": 1, "name": "foo_$emittedAtMs"}""",
                emittedAtMs = emittedAtMs,
            )

        val stream1 = makeStream(secondPk = "id2")
        runSync(
            updatedConfig,
            stream1,
            listOf(makeRecord(stream1, secondPk = "id2", emittedAtMs = 100)),
        )
        val stream2 = makeStream(secondPk = "id3")
        runSync(
            updatedConfig,
            stream2,
            listOf(makeRecord(stream2, secondPk = "id3", emittedAtMs = 200))
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to 1,
                            "id2" to 200,
                            "updated_at" to 1,
                            "name" to "foo_100",
                        ) + if (dedupChangeUsesDefault) mapOf("id3" to 0) else emptyMap(),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 200,
                    generationId = 42,
                    data =
                        mapOf(
                            "id1" to 1,
                            "id3" to 200,
                            "updated_at" to 1,
                            "name" to "foo_200",
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream2,
            primaryKey = listOf(listOf("id1"), listOf("id3")),
            cursor = listOf("updated_at"),
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
                    unmappedNamespace = randomizedNamespace,
                    unmappedName = "test_stream_$i",
                    Append,
                    ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                    generationId = 42,
                    minimumGenerationId = 42,
                    syncId = 42,
                    namespaceMapper = namespaceMapperForMedium(),
                    tableSchema = emptyTableSchema,
                )
            }
        val messages =
            (0..manyStreamCount).map { i ->
                InputRecord(
                    streams[i],
                    """{"id": 1, "name": "foo_$i"}""",
                    emittedAtMs = 100,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            }
        // Just verify that we don't crash.
        assertDoesNotThrow { runSync(updatedConfig, DestinationCatalog(streams), messages) }
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
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeRecord(data: String) =
            InputRecord(
                stream,
                data,
                emittedAtMs = 100,
                checkpointId = checkpointKeyForMedium()?.checkpointId
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                // A record with valid values for all fields
                makeRecord(
                    """
                        {
                          "id": 1,
                          "string": "fo\u0000o",
                          "number": 42.1,
                          "integer": 42,
                          "boolean": true,
                          "timestamp_with_timezone": "2023-01-23T11:34:56-01:00",
                          "timestamp_without_timezone": "2023-01-23T12:34:56",
                          "time_with_timezone": "11:34:56-01:00",
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
                // and gets rounded off.
                // 1e39 is greater than the typical max 1e39-1 for database/warehouse destinations
                // (decimal points are to force jackson to recognize it as a decimal)
                makeRecord(
                    """
                        {
                          "id": 4,
                          "struct": {"foo": 50000.0000000000000001},
                          "integer": 99999999999999999999999999999999,
                          "number": 1.0000000000000000000000000000000000000000e39
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
                // Another record that verifies numeric behavior.
                // -99999999999999999999999999999999 is out of range for int64.
                // -1e39 is out of range for many database/warehouse destinations,
                // where the maximum precision of a numeric type is 38.
                makeRecord(
                    """
                        {
                          "id": 6,
                          "number": -2.0000000000000000000000000000000000000000e39,
                          "integer": -99999999999999999999999999999999
                        }
                    """.trimIndent(),
                ),
                // A record with truncated timestamps (i.e. the seconds value is 0).
                // Some destinations have specific formatting requirements, and it's easy
                // to mess these values up.
                makeRecord(
                    """
                        {
                          "id": 7,
                          "timestamp_with_timezone": "2023-01-23T11:34:00-01:00",
                          "timestamp_without_timezone": "2023-01-23T12:34:00",
                          "time_with_timezone": "11:34:00-01:00",
                          "time_without_timezone": "12:34:00"
                        }
                    """.trimIndent()
                ),
                // lol, more numbers
                // it's surprisingly easy to handle zero / negative numbers wrong
                // in particular, if you compare `value < Double.MIN_VALUE`, you will be sad
                // and should instead do `value < -Double.MAX_VALUE`
                makeRecord(
                    """
                        {
                          "id": 8,
                          "integer": 0,
                          "number": 0.0
                        }
                    """.trimIndent(),
                ),
                makeRecord(
                    """
                        {
                          "id": 9,
                          "integer": -1,
                          "number": -1.0
                        }
                    """.trimIndent(),
                ),
            ),
        )

        val nestedFloat: BigDecimal
        val topLevelFloat: BigDecimal
        val positiveBigInt: BigInteger?
        val bigIntChanges: List<Change>
        val negativeBigInt: BigInteger?
        val positiveBigNumber: BigDecimal?
        val bigNumberChanges: List<Change>
        val negativeBigNumber: BigDecimal?
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
                if (allTypesBehavior.integerCanBeLarge) {
                    positiveBigInt = BigInteger("99999999999999999999999999999999")
                    negativeBigInt = BigInteger("-99999999999999999999999999999999")
                } else {
                    positiveBigInt = null
                    negativeBigInt = null
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
                if (allTypesBehavior.numberCanBeLarge) {
                    positiveBigNumber = BigDecimal("1e39")
                    negativeBigNumber = BigDecimal("-2e39")
                } else {
                    positiveBigNumber = null
                    negativeBigNumber = null
                }
                bigNumberChanges =
                    if (allTypesBehavior.numberCanBeLarge) {
                        emptyList()
                    } else {
                        listOf(
                            Change(
                                "number",
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
                            if (
                                allTypesBehavior.convertAllValuesToString &&
                                    dataChannelFormat != DataChannelFormat.PROTOBUF
                            ) {
                                "{}"
                            } else {
                                null
                            },
                        "number" to null,
                        "integer" to null,
                        "boolean" to null,
                        "timestamp_with_timezone" to null,
                        "timestamp_without_timezone" to null,
                        "time_with_timezone" to
                            timetz(
                                "\"foo\"",
                                null,
                            ),
                        "time_without_timezone" to null,
                        "date" to null,
                    )
                badValuesChanges =
                    (stream.schema as ObjectType)
                        .properties
                        .keys
                        .asSequence()
                        // id and struct don't have a bad value case here
                        // (id would make the test unusable; struct is tested in testContainerTypes)
                        .filter { it != "id" && it != "struct" }
                        .filter {
                            it != "boolean" || dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .filter {
                            it != "integer" || dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .filter {
                            it != "number" || dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        // With protobuf, temporal types are encoded as proper types (not strings),
                        // so it's impossible to send invalid values like "foo"
                        .filter { it != "date" || dataChannelFormat != DataChannelFormat.PROTOBUF }
                        .filter {
                            it != "time_with_timezone" ||
                                dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .filter {
                            it != "time_without_timezone" ||
                                dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .filter {
                            it != "timestamp_with_timezone" ||
                                dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .filter {
                            it != "timestamp_without_timezone" ||
                                dataChannelFormat != DataChannelFormat.PROTOBUF
                        }
                        .map { key ->
                            val change =
                                Change(
                                    key,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_SERIALIZATION_ERROR,
                                )
                            // this is kind of dumb, see
                            // https://github.com/airbytehq/airbyte-internal-issues/issues/12715
                            if (key == "time_with_timezone") {
                                timetzChange(change)
                            } else {
                                change
                            }
                        }
                        .filterNotNull()
                        .filter {
                            !allTypesBehavior.convertAllValuesToString || it.field != "string"
                        }
                        .toMutableList()
            }
            Untyped -> {
                nestedFloat = BigDecimal("50000.0000000000000001")
                topLevelFloat = BigDecimal("50000.0000000000000001")
                positiveBigInt = BigInteger("99999999999999999999999999999999")
                negativeBigInt = BigInteger("-99999999999999999999999999999999")
                bigIntChanges = emptyList()
                positiveBigNumber = BigDecimal("1e39")
                negativeBigNumber = BigDecimal("-2e39")
                bigNumberChanges = emptyList()
                badValuesData =
                    // note that the values have different types than what's declared in the schema
                    // With protobuf, temporal types can't be sent as strings, so exclude them
                    (mapOf("id" to 5) +
                        if (dataChannelFormat != DataChannelFormat.PROTOBUF) {
                            mapOf(
                                "timestamp_with_timezone" to "foo",
                                "timestamp_without_timezone" to "foo",
                                "time_with_timezone" to "foo",
                                "time_without_timezone" to "foo",
                                "date" to "foo",
                            )
                        } else {
                            mapOf(
                                "timestamp_with_timezone" to null,
                                "timestamp_without_timezone" to null,
                                "time_with_timezone" to null,
                                "time_without_timezone" to null,
                                "date" to null,
                            )
                        }) +
                        if (mismatchedTypesUnrepresentable) emptyMap()
                        else
                            mapOf(
                                "string" to ObjectValue(linkedMapOf()),
                                "number" to "foo",
                                "integer" to "foo",
                                "boolean" to "foo"
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
                            "string" to "fo\u0000o",
                            "number" to 42.1,
                            "integer" to 42,
                            "boolean" to true,
                            "timestamp_with_timezone" to
                                OffsetDateTime.parse("2023-01-23T11:34:56-01:00"),
                            "timestamp_without_timezone" to
                                LocalDateTime.parse("2023-01-23T12:34:56"),
                            "time_with_timezone" to
                                timetz(
                                    "\"11:34:56-01:00\"",
                                    OffsetTime.parse("11:34:56-01:00"),
                                ),
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
                            "struct" to schematizedObject(linkedMapOf("foo" to nestedFloat)),
                            "number" to topLevelFloat,
                            "integer" to positiveBigInt,
                            "number" to positiveBigNumber,
                        ),
                    airbyteMeta =
                        OutputRecord.Meta(syncId = 42, changes = bigNumberChanges + bigIntChanges),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data = badValuesData,
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = badValuesChanges),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 6,
                            "integer" to negativeBigInt,
                            "number" to negativeBigNumber,
                        ),
                    airbyteMeta =
                        OutputRecord.Meta(syncId = 42, changes = bigNumberChanges + bigIntChanges),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 7,
                            "timestamp_with_timezone" to
                                OffsetDateTime.parse("2023-01-23T11:34:00-01:00"),
                            "timestamp_without_timezone" to
                                LocalDateTime.parse("2023-01-23T12:34:00"),
                            "time_with_timezone" to
                                timetz(
                                    "\"11:34:00-01:00\"",
                                    OffsetTime.parse("11:34:00-01:00"),
                                ),
                            "time_without_timezone" to LocalTime.parse("12:34:00"),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 8,
                            "integer" to 0,
                            "number" to 0.0,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 9,
                            "integer" to -1,
                            "number" to -1.0,
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    /**
     * Further tests for number/int types. For historical reasons, some of the records in
     * [testBasicTypes] also cover numerics.
     */
    @Test
    open fun testNumericTypes() {
        assumeTrue(verifyDataWriting)
        assumeTrue(allTypesBehavior is StronglyTyped)
        // TODO ideally we would have some more flexibility here, but it's kind of painful to
        //   configure our tests already.
        assumeTrue((allTypesBehavior as StronglyTyped).numberIsFixedPointPrecision38Scale9)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Append,
                ObjectType(
                    linkedMapOf(
                        "id" to intType,
                        "number" to FieldType(NumberType, nullable = true),
                        "integer" to FieldType(IntegerType, nullable = true),
                    )
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        fun makeRecord(data: String) =
            InputRecord(
                stream,
                data,
                emittedAtMs = 100,
                checkpointId = checkpointKeyForMedium()?.checkpointId
            )
        // large numbers, 0, and -1 are already tested in testBasicTypes, but add them here also.
        // Eventually we should remove them from testBasicTypes, but that would require a less dumb
        // test config system.
        val roundingModeTest = "5e-10"
        val highPrecisionTest = "12345678912345678912345678912.3456789123"
        runSync(
            updatedConfig,
            stream,
            listOf(
                // Test that we can handle numbers which require scale=10.
                // Depending on destination behavior, these should either be
                // truncated to 0, or rounded to +/-1e9
                makeRecord(
                    """
                        {
                          "id": 1,
                          "number": $roundingModeTest
                        }
                    """.trimIndent(),
                ),
                makeRecord(
                    """
                        {
                          "id": 2,
                          "number": -$roundingModeTest
                        }
                    """.trimIndent(),
                ),
                // Similarly, test that we can handle numbers with precision=39,
                // but that still fit within a (38, 9) field's min/max values.
                makeRecord(
                    """
                        {
                          "id": 3,
                          "number": $highPrecisionTest
                        }
                    """.trimIndent(),
                ),
                makeRecord(
                    """
                        {
                          "id": 4,
                          "number": -$highPrecisionTest
                        }
                    """.trimIndent(),
                ),
            ),
        )
        val roundingModeExpectedValue =
            BigDecimal(roundingModeTest).setScale(9, allTypesBehavior.truncatedNumberRoundingMode)
        val highPrecisionExpectedValue =
            BigDecimal(highPrecisionTest).setScale(9, allTypesBehavior.truncatedNumberRoundingMode)
        val meta =
            OutputRecord.Meta(
                syncId = 42,
                changes =
                    listOfNotNull(
                        if (allTypesBehavior.truncatedNumbersPopulateAirbyteMeta) {
                            Change(
                                "number",
                                AirbyteRecordMessageMetaChange.Change.TRUNCATED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        } else {
                            null
                        }
                    ),
            )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "number" to roundingModeExpectedValue,
                        ),
                    airbyteMeta = meta,
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 2,
                            "number" to roundingModeExpectedValue.negate(),
                        ),
                    airbyteMeta = meta,
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 3,
                            "number" to highPrecisionExpectedValue,
                        ),
                    airbyteMeta = meta,
                ),
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 4,
                            "number" to highPrecisionExpectedValue.negate(),
                        ),
                    airbyteMeta = meta,
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
                unmappedNamespace = randomizedNamespace,
                unmappedName = "problematic_types",
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
                    ),
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                        {
                          "id": 1,
                          "schematized_object": { "id": 1, "name": "Joe", "undeclared": 42 },
                          "empty_object": {},
                          "schemaless_object": { "uuid": "38F52396-736D-4B23-B5B4-F504D8894B97", "probability": 1.5 },
                          "schematized_array": [10, null],
                          "schemaless_array": [ 10, "foo", null, { "bar": "qua" } ]
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream,
                    """
                        {
                          "id": 2,
                          "schematized_object": { "id": 2, "name": "Jane" },
                          "empty_object": {"extra": "stuff"},
                          "schemaless_object": { "address": { "street": "113 Hickey Rd", "zip": "37932" }, "flags": [ true, false, false ] },
                          "schematized_array": [],
                          "schemaless_array": []
                        }""".trimIndent(),
                    emittedAtMs = 1602637589200,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream,
                    """
                        {
                          "id": 3,
                          "schematized_object": null,
                          "empty_object": null,
                          "schemaless_object": null,
                          "schematized_array": null,
                          "schemaless_array": null
                        }""".trimIndent(),
                    emittedAtMs = 1602637589300,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
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
                            "schematized_object" to
                                schematizedObject(
                                    linkedMapOf("id" to 1, "name" to "Joe", "undeclared" to 42),
                                    linkedMapOf("id" to 1, "name" to "Joe"),
                                ),
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
                            "schematized_array" to
                                when (schematizedArrayBehavior) {
                                    SchematizedNestedValueBehavior.PASS_THROUGH -> listOf(10, null)
                                    SchematizedNestedValueBehavior.STRONGLY_TYPE -> listOf(10, null)
                                    SchematizedNestedValueBehavior.STRINGIFY -> "[10,null]"
                                },
                            "schemaless_array" to
                                if (stringifySchemalessObjects) {
                                    """[10,"foo",null,{"bar":"qua"}]"""
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
                            "schematized_object" to
                                schematizedObject(linkedMapOf("id" to 2, "name" to "Jane")),
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
                            "schematized_array" to
                                when (schematizedArrayBehavior) {
                                    SchematizedNestedValueBehavior.PASS_THROUGH -> emptyList<Long>()
                                    SchematizedNestedValueBehavior.STRONGLY_TYPE ->
                                        emptyList<Long>()
                                    SchematizedNestedValueBehavior.STRINGIFY -> "[]"
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
                            "schematized_array" to null,
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

    @Test
    open fun testUnknownTypes() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "problematic_types",
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to unknownType)),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )

        fun runSync() =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    InputRecord(
                        stream,
                        """
                        {
                          "id": 1,
                          "name": "ex falso quodlibet"
                        }""".trimIndent(),
                        emittedAtMs = 1602637589100,
                        checkpointId = checkpointKeyForMedium()?.checkpointId,
                        unknownFieldNames = setOf("name")
                    )
                )
            )
        if (unknownTypesBehavior == UnknownTypesBehavior.FAIL) {
            assertThrows<DestinationUncleanExitException> { runSync() }
        } else {
            assertDoesNotThrow { runSync() }
            val expectedRecords: List<OutputRecord> =
                listOf(
                    OutputRecord(
                        extractedAt = 1602637589100,
                        generationId = 42,
                        data =
                            mapOf(
                                "id" to 1,
                                "name" to
                                    when (unknownTypesBehavior) {
                                        UnknownTypesBehavior.NULL -> null
                                        UnknownTypesBehavior.PASS_THROUGH -> "ex falso quodlibet"
                                        UnknownTypesBehavior.SERIALIZE -> "\"ex falso quodlibet\""
                                        // this is required to satisfy the compiler,
                                        // but intellij correctly detects that it's unreachable.
                                        UnknownTypesBehavior.FAIL ->
                                            throw IllegalStateException(
                                                "The sync was expected to fail, so we should not be asserting that its records were correct"
                                            )
                                    },
                            ),
                        airbyteMeta =
                            OutputRecord.Meta(
                                syncId = 42,
                                changes =
                                    when (unknownTypesBehavior) {
                                        UnknownTypesBehavior.NULL ->
                                            listOf(
                                                Change(
                                                    "name",
                                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                                    AirbyteRecordMessageMetaChange.Reason
                                                        .DESTINATION_SERIALIZATION_ERROR
                                                )
                                            )
                                        else -> emptyList()
                                    }
                            ),
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
                unmappedNamespace = randomizedNamespace,
                unmappedName = "problematic_types",
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
                        // For destinations which promote unions to objects,
                        // and also stringify schemaless values,
                        // we should verify that the promoted schemaless value
                        // is still labelled as "object" rather than "string".
                        "union_of_string_and_schemaless_type" to
                            FieldType(
                                UnionType.of(ObjectTypeWithoutSchema, IntegerType),
                                nullable = true,
                            ),
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
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                        {
                          "id": 1,
                          "combined_type": "string1",
                          "union_of_string_and_schemaless_type": {"foo": "bar"},
                          "union_of_objects_with_properties_identical": { "id": 10, "name": "Joe" },
                          "union_of_objects_with_properties_overlapping": { "id": 20, "name": "Jane", "flagged": true },
                          "union_of_objects_with_properties_contradicting": { "id": 1, "name": "Jenny" },
                          "union_of_objects_with_properties_nonoverlapping": { "id": 30, "name": "Phil", "flagged": false, "description":"Very Phil" }
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream,
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
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
                InputRecord(
                    stream,
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
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                ),
            )
        )

        fun unionValue(typeName: String, value: Any?, skipSerialize: Boolean = false) =
            when (unionBehavior) {
                UnionBehavior.PASS_THROUGH -> value
                UnionBehavior.PROMOTE_TO_OBJECT ->
                    mapOf(
                        "type" to typeName,
                        typeName to value,
                    )
                UnionBehavior.STRINGIFY ->
                    if (value is String && skipSerialize) {
                        StringValue(value)
                    } else {
                        StringValue(value.serializeToString())
                    }
            }
        val expectedRecords: List<OutputRecord> =
            listOf(
                OutputRecord(
                    extractedAt = 1602637589100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "combined_type" to unionValue("string", "string1"),
                            "union_of_string_and_schemaless_type" to
                                unionValue(
                                    "object",
                                    if (stringifySchemalessObjects) {
                                        """{"foo":"bar"}"""
                                    } else {
                                        schematizedObject(linkedMapOf("foo" to "bar"))
                                    },
                                    // Don't double-serialize the object.
                                    skipSerialize = stringifySchemalessObjects,
                                ),
                            "union_of_objects_with_properties_identical" to
                                schematizedObject(linkedMapOf("id" to 10, "name" to "Joe")),
                            "union_of_objects_with_properties_overlapping" to
                                if (stringifyUnionObjects) {
                                    """{"id":20,"name":"Jane","flagged":true}"""
                                } else {
                                    schematizedObject(
                                        linkedMapOf("id" to 20, "name" to "Jane", "flagged" to true)
                                    )
                                },
                            "union_of_objects_with_properties_contradicting" to
                                if (stringifyUnionObjects) {
                                    """{"id":1,"name":"Jenny"}"""
                                } else {
                                    // can't just call schematizedObject(... unionValue) - there's
                                    // some
                                    // nontrivial interactions here
                                    when (schematizedObjectBehavior) {
                                        // these two cases are simple
                                        SchematizedNestedValueBehavior.PASS_THROUGH,
                                        SchematizedNestedValueBehavior.STRONGLY_TYPE ->
                                            linkedMapOf(
                                                "id" to unionValue("integer", 1),
                                                "name" to "Jenny"
                                            )
                                        // If we stringify, then the nested union value is _not_
                                        // processed
                                        // (note that `id` is mapped to 1 and not "1")
                                        SchematizedNestedValueBehavior.STRINGIFY ->
                                            """{"id":1,"name":"Jenny"}"""
                                    }
                                },
                            "union_of_objects_with_properties_nonoverlapping" to
                                if (stringifyUnionObjects) {
                                    """{"id":30,"name":"Phil","flagged":false,"description":"Very Phil"}"""
                                } else {
                                    schematizedObject(
                                        linkedMapOf(
                                            "id" to 30,
                                            "name" to "Phil",
                                            "flagged" to false,
                                            "description" to "Very Phil",
                                        )
                                    )
                                }
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1602637589200,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 2,
                            "combined_type" to unionValue("integer", 20),
                            "union_of_objects_with_properties_identical" to
                                schematizedObject(linkedMapOf()),
                            "union_of_objects_with_properties_nonoverlapping" to
                                if (stringifyUnionObjects) {
                                    """{}"""
                                } else {
                                    schematizedObject(linkedMapOf())
                                },
                            "union_of_objects_with_properties_overlapping" to
                                if (stringifyUnionObjects) {
                                    """{}"""
                                } else {
                                    schematizedObject(linkedMapOf())
                                },
                            "union_of_objects_with_properties_contradicting" to
                                if (stringifyUnionObjects) {
                                    """{"id":"seal-one-hippity","name":"James"}"""
                                } else {
                                    // similar to the previous record - need to handle this branch
                                    // manually
                                    when (schematizedObjectBehavior) {
                                        // these two cases are simple
                                        SchematizedNestedValueBehavior.PASS_THROUGH,
                                        SchematizedNestedValueBehavior.STRONGLY_TYPE ->
                                            linkedMapOf(
                                                "id" to unionValue("string", "seal-one-hippity"),
                                                "name" to "James"
                                            )
                                        // If we stringify, then the nested union value is _not_
                                        // processed
                                        // (note that `id` is mapped to 1 and not "1")
                                        SchematizedNestedValueBehavior.STRINGIFY ->
                                            """{"id":"seal-one-hippity","name":"James"}"""
                                    }
                                }
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

    /**
     * Run a sync with a legacy union of number|boolean. Validate that we correctly coerce/null
     * nonobvious values.
     */
    @Test
    open fun testCoerceLegacyUnions() {
        assumeTrue(verifyDataWriting)
        assumeTrue(coercesLegacyUnions)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(
                    linkedMapOf(
                        "x" to
                            FieldType(
                                // It's easier to just hardcode a jsonschema here.
                                // In theory we could modify AirbyteTypeToJsonSchema to do this,
                                // but legacy unions are really annoying to construct.
                                UnknownType(Jsons.readTree("""{"type": ["number", "boolean"]}""")),
                                nullable = true
                            ),
                    )
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 12,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                // 42 wrapped in a string - should be coerced to 42
                InputRecord(stream, """{"x": "42"}""", emittedAtMs = 1234),
                // "potato" is not a valid number, should get nulled out.
                InputRecord(stream, """{"x": "potato"}""", emittedAtMs = 2345),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 42,
                    data = mapOf("x" to NumberValue(BigDecimal.valueOf(42))),
                    airbyteMeta = OutputRecord.Meta(syncId = 12),
                ),
                OutputRecord(
                    extractedAt = 2345,
                    generationId = 42,
                    data = mapOf("x" to NullValue),
                    airbyteMeta =
                        OutputRecord.Meta(
                            syncId = 12,
                            changes =
                                listOf(
                                    Change(
                                        "x",
                                        AirbyteRecordMessageMetaChange.Change.NULLED,
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_SERIALIZATION_ERROR,
                                    ),
                                ),
                        ),
                ),
            ),
            stream,
            primaryKey = emptyList(),
            cursor = null,
        )
    }

    /**
     * Verify that we can handle a stream with 0 columns. This is... not particularly useful, but
     * happens sometimes.
     */
    @Test
    open fun testNoColumns() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Append,
                ObjectType(linkedMapOf()),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{}""",
                    emittedAtMs = 1000L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        val expectedFirstRecord =
            OutputRecord(
                extractedAt = 1000L,
                generationId = 42,
                data = emptyMap(),
                airbyteMeta = OutputRecord.Meta(syncId = 42),
            )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(expectedFirstRecord),
            stream,
            primaryKey = listOf(),
            cursor = null,
        )
        // Run a second sync to catch bugs in schema change detection.
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{}""",
                    emittedAtMs = 2000L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                expectedFirstRecord,
                OutputRecord(
                    extractedAt = 2000L,
                    generationId = 42,
                    data = emptyMap(),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(),
            cursor = null,
        )
    }

    @Test
    open fun testNoData() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        assertDoesNotThrow { runSync(updatedConfig, stream, messages = emptyList()) }
        dumpAndDiffRecords(
            parsedConfig,
            canonicalExpectedRecords = emptyList(),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testTruncateRefreshNoData() {
        assumeTrue(verifyDataWriting)
        fun makeStream(generationId: Long, minimumGenerationId: Long, syncId: Long) =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType, "name" to stringType)),
                generationId,
                minimumGenerationId,
                syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        val firstStream = makeStream(generationId = 12, minimumGenerationId = 0, syncId = 42)
        runSync(
            updatedConfig,
            firstStream,
            listOf(
                InputRecord(
                    firstStream,
                    """{"id": 42, "name": "first_value"}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            )
        )
        val finalStream = makeStream(generationId = 13, minimumGenerationId = 13, syncId = 43)
        runSync(updatedConfig, finalStream, emptyList())
        dumpAndDiffRecords(
            parsedConfig,
            emptyList(),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testClear() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = emptyTableSchema,
            )
        assertDoesNotThrow {
            runSync(
                updatedConfig,
                stream,
                messages =
                    listOf(
                        InputGlobalCheckpoint(null, checkpointKeyForMedium(), sourceRecordCount = 0)
                    )
            )
        }
    }

    private fun schematizedObject(
        fullObject: LinkedHashMap<String, Any?>,
        coercedObject: LinkedHashMap<String, Any?> = fullObject
    ): AirbyteValue =
        schematizedObject(ObjectValue.from(fullObject), ObjectValue.from(coercedObject))

    private fun schematizedObject(
        fullObject: ObjectValue,
        coercedObject: ObjectValue = fullObject
    ): AirbyteValue {
        return when (schematizedObjectBehavior) {
            SchematizedNestedValueBehavior.PASS_THROUGH -> fullObject
            SchematizedNestedValueBehavior.STRONGLY_TYPE -> coercedObject
            SchematizedNestedValueBehavior.STRINGIFY -> StringValue(fullObject.serializeToString())
        }
    }

    private fun timetz(originalValue: String, parsedValue: Any?): Any? =
        when (allTypesBehavior) {
            is StronglyTyped ->
                expect(originalValue, parsedValue, allTypesBehavior.timeWithTimezoneBehavior)
            Untyped -> expect(originalValue, parsedValue, SimpleValueBehavior.PASS_THROUGH)
        }
    private fun timetzChange(change: Change?) =
        when (allTypesBehavior) {
            is StronglyTyped -> expectChange(change, allTypesBehavior.timeWithTimezoneBehavior)
            Untyped -> expectChange(change, SimpleValueBehavior.PASS_THROUGH)
        }

    private fun expect(
        originalValue: String,
        parsedValue: Any?,
        behavior: SimpleValueBehavior
    ): Any? {
        val passthroughValue = originalValue.deserializeToNode().toAirbyteValue()
        return when (behavior) {
            SimpleValueBehavior.PASS_THROUGH -> passthroughValue
            SimpleValueBehavior.VALIDATE_AND_PASS_THROUGH -> {
                if (parsedValue != null) {
                    passthroughValue
                } else {
                    null
                }
            }
            SimpleValueBehavior.STRONGLY_TYPE -> parsedValue
        }
    }
    private fun expectChange(change: Change?, behavior: SimpleValueBehavior) =
        when (behavior) {
            SimpleValueBehavior.PASS_THROUGH -> null
            SimpleValueBehavior.VALIDATE_AND_PASS_THROUGH,
            SimpleValueBehavior.STRONGLY_TYPE -> change
        }

    companion object {
        val intType = FieldType(IntegerType, nullable = true)
        val numberType = FieldType(NumberType, nullable = true)
        val stringType = FieldType(StringType, nullable = true)
        val unknownType =
            FieldType(
                UnknownType(Jsons.readTree("""{"type": "potato"}""")),
                nullable = true,
            )
        private val timestamptzType = FieldType(TimestampTypeWithTimezone, nullable = true)
    }

    fun checkpointKeyForMedium(index: Int = 1, partitionId: String = "1"): CheckpointKey? {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO -> null
            DataChannelMedium.SOCKET ->
                CheckpointKey(CheckpointIndex(index), CheckpointId(partitionId))
        }
    }

    /** Jsonl is bigger for sockets than stdio because there are extra fields. */
    private fun expectedBytesForMediumAndFormat(
        bytesForStdio: Long,
        bytesForSocketJsonl: Long,
        bytesForSocketProtobuf: Long
    ): Long {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO -> bytesForStdio
            DataChannelMedium.SOCKET ->
                when (dataChannelFormat) {
                    DataChannelFormat.JSONL -> bytesForSocketJsonl
                    DataChannelFormat.PROTOBUF -> bytesForSocketProtobuf
                    DataChannelFormat.FLATBUFFERS -> TODO()
                }
        }
    }

    private fun expectedAdditionalStats(): AdditionalStats? =
        if (useDataFlowPipeline) {
            val expectedAdditionalStats = AdditionalStats()
            StateAdditionalStatsStore.ObservabilityMetrics.entries.forEach {
                expectedAdditionalStats.withAdditionalProperty(it.metricName, 0.0)
            }
            expectedAdditionalStats
        } else null

    protected fun namespaceMapperForMedium(): NamespaceMapper {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO ->
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE)
            // TODO: Return something more dynamic? Based on the test?
            DataChannelMedium.SOCKET ->
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE)
        }
    }

    // This will get blown away in the tests as the DestinationStream's we are mocking just get
    // converted to the protocol which has no concept of destination schemas
    protected val emptyTableSchema: StreamTableSchema =
        StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = mapOf(),
                    inputToFinalColumnNames = mapOf(),
                    finalSchema = mapOf(),
                ),
            importType = Append,
            tableNames = TableNames(finalTableName = TableName("namespace", "test")),
        )
}
