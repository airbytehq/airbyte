/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeSoftReset
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import kotlin.test.assertFails
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assumptions.assumeFalse
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.mockito.kotlin.mock

private val LOGGER = KotlinLogging.logger {}
/**
 * This class exercises [SqlGenerator] implementations. All destinations should extend this class
 * for their respective implementation. Subclasses are encouraged to add additional tests with
 * destination-specific behavior (for example, verifying that datasets are created in the correct
 * BigQuery region).
 *
 * Subclasses should implement a [org.junit.jupiter.api.BeforeAll] method to load any secrets and
 * connect to the destination. This test expects to be able to run [.getDestinationHandler] in a
 * [org.junit.jupiter.api.BeforeEach] method.
 */
@Execution(ExecutionMode.CONCURRENT)
abstract class BaseSqlGeneratorIntegrationTest<DestinationState : MinimumDestinationState> {
    protected var DIFFER: RecordDiffer? = null

    /** Subclasses may use these four StreamConfigs in their tests. */
    protected var incrementalDedupStream: StreamConfig = mock()

    /**
     * We intentionally don't have full refresh overwrite/append streams. Those actually behave
     * identically in the sqlgenerator. Overwrite mode is actually handled in [DefaultTyperDeduper].
     */
    protected var incrementalAppendStream: StreamConfig = mock()
    protected var cdcIncrementalDedupStream: StreamConfig = mock()

    /** This isn't particularly realistic, but it's technically possible. */
    protected var cdcIncrementalAppendStream: StreamConfig = mock()

    protected var generator: SqlGenerator = mock()
    protected abstract val destinationHandler: DestinationHandler<DestinationState>
    // Need a placeholder otherwise Spotbugs will complain with
    // a possibility of returning null value in getNamespace.
    protected var namespace: String = "dummy_holder"

    protected var streamId: StreamId = mock()
    private lateinit var primaryKey: List<ColumnId>
    private lateinit var cursor: ColumnId
    private var COLUMNS: LinkedHashMap<ColumnId, AirbyteType> = mock()

    protected abstract val sqlGenerator: SqlGenerator
    protected abstract val supportsSafeCast: Boolean

    /**
     * Subclasses should override this method if they need to make changes to the stream ID. For
     * example, you could upcase the final table name here.
     */
    open protected fun buildStreamId(
        namespace: String,
        finalTableName: String,
        rawTableName: String
    ): StreamId {
        return StreamId(
            namespace,
            finalTableName,
            namespace,
            rawTableName,
            namespace,
            finalTableName
        )
    }

    /**
     * Do any setup work to create a namespace for this test run. For example, this might create a
     * BigQuery dataset, or a Snowflake schema.
     */
    @Throws(Exception::class) protected abstract fun createNamespace(namespace: String)

    /** Create a raw table using the StreamId's rawTableId. */
    @Throws(Exception::class) protected abstract fun createRawTable(streamId: StreamId)

    /** Creates a raw table in the v1 format */
    @Throws(Exception::class) protected abstract fun createV1RawTable(v1RawTable: StreamId)

    @Throws(Exception::class)
    protected abstract fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>)

    @Throws(Exception::class)
    protected abstract fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>)

    @Throws(Exception::class)
    protected abstract fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>
    )

    /**
     * The two dump methods are defined identically as in [BaseTypingDedupingTest], but with
     * slightly different method signature. This test expects subclasses to respect the
     * raw/finalTableId on the StreamId object, rather than hardcoding e.g. the airbyte_internal
     * dataset.
     *
     * The `_airbyte_data` field must be deserialized into an ObjectNode, even if it's stored in the
     * destination as a string.
     */
    @Throws(Exception::class)
    protected abstract fun dumpRawTableRecords(streamId: StreamId): List<JsonNode>

    @Throws(Exception::class)
    protected abstract fun dumpFinalTableRecords(
        streamId: StreamId,
        suffix: String?
    ): List<JsonNode>

    /**
     * Clean up all resources in the namespace. For example, this might delete the BigQuery dataset
     * created in [.createNamespace].
     */
    @Throws(Exception::class) protected abstract fun teardownNamespace(namespace: String)

    protected val rawMetadataColumnNames: Map<String, String>
        /** Identical to [BaseTypingDedupingTest.getRawMetadataColumnNames]. */
        get() = HashMap()

    open protected val finalMetadataColumnNames: Map<String, String>
        /** Identical to [BaseTypingDedupingTest.getFinalMetadataColumnNames]. */
        get() = HashMap()

    /**
     * This test implementation is extremely destination-specific, but all destinations must
     * implement it. This test should verify that creating a table using [.incrementalDedupStream]
     * works as expected, including column types, indexing, partitioning, etc.
     *
     * Note that subclasses must also annotate their implementation with @Test.
     */
    @Test @Throws(Exception::class) abstract fun testCreateTableIncremental()

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        generator = sqlGenerator

        val id1 = generator.buildColumnId("id1")
        val id2 = generator.buildColumnId("id2")
        primaryKey = listOf(id1, id2)
        val cursor = generator.buildColumnId("updated_at")
        this.cursor = cursor

        COLUMNS = LinkedHashMap()
        COLUMNS[id1] = AirbyteProtocolType.INTEGER
        COLUMNS[id2] = AirbyteProtocolType.INTEGER
        COLUMNS[cursor] = AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        COLUMNS[generator.buildColumnId("struct")] = Struct(LinkedHashMap())
        COLUMNS[generator.buildColumnId("array")] = Array(AirbyteProtocolType.UNKNOWN)
        COLUMNS[generator.buildColumnId("string")] = AirbyteProtocolType.STRING
        COLUMNS[generator.buildColumnId("number")] = AirbyteProtocolType.NUMBER
        COLUMNS[generator.buildColumnId("integer")] = AirbyteProtocolType.INTEGER
        COLUMNS[generator.buildColumnId("boolean")] = AirbyteProtocolType.BOOLEAN
        COLUMNS[generator.buildColumnId("timestamp_with_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        COLUMNS[generator.buildColumnId("timestamp_without_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE
        COLUMNS[generator.buildColumnId("time_with_timezone")] =
            AirbyteProtocolType.TIME_WITH_TIMEZONE
        COLUMNS[generator.buildColumnId("time_without_timezone")] =
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE
        COLUMNS[generator.buildColumnId("date")] = AirbyteProtocolType.DATE
        COLUMNS[generator.buildColumnId("unknown")] = AirbyteProtocolType.UNKNOWN

        val cdcColumns = LinkedHashMap(COLUMNS)
        cdcColumns[generator.buildColumnId("_ab_cdc_deleted_at")] =
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE

        DIFFER =
            RecordDiffer(
                rawMetadataColumnNames,
                finalMetadataColumnNames,
                id1 to AirbyteProtocolType.INTEGER,
                id2 to AirbyteProtocolType.INTEGER,
                cursor to AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
            )

        namespace = Strings.addRandomSuffix("sql_generator_test", "_", 10)
        // This is not a typical stream ID would look like, but SqlGenerator isn't allowed to make
        // any
        // assumptions about StreamId structure.
        // In practice, the final table would be testDataset.users, and the raw table would be
        // airbyte_internal.testDataset_raw__stream_users.
        streamId = buildStreamId(namespace, "users_final", "users_raw")

        incrementalDedupStream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                primaryKey,
                Optional.of(cursor),
                COLUMNS,
                0,
                0,
                0,
            )
        incrementalAppendStream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                primaryKey,
                Optional.of(cursor),
                COLUMNS,
                0,
                0,
                0,
            )

        cdcIncrementalDedupStream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                primaryKey,
                Optional.of(cursor),
                cdcColumns,
                0,
                0,
                0,
            )
        cdcIncrementalAppendStream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                primaryKey,
                Optional.of(cursor),
                cdcColumns,
                0,
                0,
                0,
            )

        LOGGER.info { "Running with namespace $namespace" }
        createNamespace(namespace)
    }

    @AfterEach
    @Throws(Exception::class)
    fun teardown() {
        teardownNamespace(namespace)
    }

    @Throws(Exception::class)
    private fun getDestinationInitialState(
        streamConfig: StreamConfig
    ): DestinationInitialStatus<DestinationState> {
        val initialState = destinationHandler.gatherInitialState(java.util.List.of(streamConfig))
        Assertions.assertEquals(
            1,
            initialState.size,
            "gatherInitialState returned the wrong number of futures"
        )
        Assertions.assertTrue(
            initialState.first().isFinalTablePresent,
            "Destination handler could not find existing table"
        )
        return initialState.first()
    }

    /** Create a table and verify that we correctly recognize it as identical to itself. */
    @Test
    @Throws(Exception::class)
    fun detectNoSchemaChange() {
        val createTable = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(createTable)
        val destinationInitialStatus = getDestinationInitialState(incrementalDedupStream)
        assertFalse(
            destinationInitialStatus!!.isSchemaMismatch,
            "Unchanged schema was incorrectly detected as a schema change."
        )
    }

    /** Verify that adding a new column is detected as a schema change. */
    @Test
    @Throws(Exception::class)
    fun detectColumnAdded() {
        val createTable = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(createTable)
        incrementalDedupStream.columns!!.put(
            generator.buildColumnId("new_column"),
            AirbyteProtocolType.STRING
        )
        val destinationInitialStatus = getDestinationInitialState(incrementalDedupStream)
        Assertions.assertTrue(
            destinationInitialStatus.isSchemaMismatch,
            "Adding a new column was not detected as a schema change."
        )
    }

    /** Verify that removing a column is detected as a schema change. */
    @Test
    @Throws(Exception::class)
    fun detectColumnRemoved() {
        val createTable = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(createTable)
        incrementalDedupStream.columns!!.remove(generator.buildColumnId("string"))
        val destinationInitialStatus = getDestinationInitialState(incrementalDedupStream)
        Assertions.assertTrue(
            destinationInitialStatus.isSchemaMismatch,
            "Removing a column was not detected as a schema change."
        )
    }

    /** Verify that changing a column's type is detected as a schema change. */
    @Test
    @Throws(Exception::class)
    fun detectColumnChanged() {
        val createTable = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(createTable)
        incrementalDedupStream.columns!!.put(
            generator.buildColumnId("string"),
            AirbyteProtocolType.INTEGER
        )
        val destinationInitialStatus = getDestinationInitialState(incrementalDedupStream)
        Assertions.assertTrue(
            destinationInitialStatus.isSchemaMismatch,
            "Altering a column was not detected as a schema change."
        )
    }

    /** Test that T+D supports streams whose name and namespace are the same. */
    @Test
    @Throws(Exception::class)
    fun incrementalDedupSameNameNamespace() {
        val streamId = buildStreamId(namespace, namespace, namespace + "_raw")
        val stream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                incrementalDedupStream.primaryKey,
                incrementalDedupStream.cursor,
                incrementalDedupStream.columns,
                0,
                0,
                0,
            )

        createRawTable(streamId)
        createFinalTable(stream, "")
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "5ce60e70-98aa-4fe3-8159-67207352c4f0",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {"id1": 1, "id2": 100}
            }

            """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")

        val rawRecords = dumpRawTableRecords(streamId)
        val finalRecords = dumpFinalTableRecords(streamId, "")
        verifyRecordCounts(1, rawRecords, 1, finalRecords)
    }

    private fun getOnly(
        initialStates: List<DestinationInitialStatus<DestinationState>>
    ): DestinationInitialStatus<DestinationState> {
        Assertions.assertEquals(1, initialStates.size)
        return initialStates.first()
    }

    /**
     * Run a full T+D update for an incremental-dedup stream, writing to a final table with "_foo"
     * suffix, with values for all data types. Verifies all behaviors for all types:
     *
     * * A valid, nonnull value
     * * No value (i.e. the column is missing from the record)
     * * A JSON null value
     * * An invalid value
     *
     * In practice, incremental streams never write to a suffixed table, but SqlGenerator isn't
     * allowed to make that assumption (and we might as well exercise that code path).
     */
    @Test
    @Throws(Exception::class)
    fun allTypes_safeCast() {
        assumeTrue(
            supportsSafeCast,
            "Skipping test because this connector does not support safe casting"
        )
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            readAllTypesInputRecords(includeSafeCastRecords = true),
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecords(
            "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/alltypes_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /** Run a basic test to verify that we don't throw an exception on basic data values. */
    @Test
    @Throws(Exception::class)
    fun allTypes_safeCast_handleGoodData() {
        assumeTrue(
            supportsSafeCast,
            "Skipping test because this connector does not support safe casting"
        )
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            readAllTypesInputRecords(includeSafeCastRecords = false),
        )

        // Instead of using the full T+D transaction, explicitly run with useSafeCasting=false.
        val unsafeSql = generator.updateTable(incrementalDedupStream, "", Optional.empty(), false)
        destinationHandler.execute(unsafeSql)
    }

    /**
     * Similar to [allTypes_safeCast], but just the records with good data. This verifies that the
     * connector handles all types correctly.
     */
    @Test
    @Throws(Exception::class)
    fun allTypes_noSafeCast_handleGoodData() {
        assumeFalse(supportsSafeCast, "Skipping test because this connector supports safe casting")

        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            readAllTypesInputRecords(includeSafeCastRecords = false),
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecords(
            "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/alltypes_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Run a basic test to verify that we don't throw an exception on basic data values. Similar to
     * {@link #allTypes_safeCast()}, but just the records with bad data. This verifies that the
     * connector throws an error when it encounters bad data.
     */
    @Test
    fun allTypes_noSafeCast_crashOnBadData() {
        assumeFalse(supportsSafeCast, "Skipping test because this connector supports safe casting")

        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(streamId, readAllTypesInputRecords(includeSafeCastRecords = true))

        assertFails {
            executeTypeAndDedupe(
                generator,
                destinationHandler,
                incrementalDedupStream,
                Optional.empty(),
                ""
            )
        }
    }

    /**
     * Verifies two behaviors:
     * 1. The isFinalTableEmpty method behaves correctly during a sync
     * 2. Column names with mixed case are handled correctly
     *
     * The first behavior technically should be its own test, but we might as well just throw it
     * into a random testcase to avoid running test setup/teardown again.
     */
    @Test
    @Throws(java.lang.Exception::class)
    fun mixedCaseTest() {
        // Add case-sensitive columnName to test json path querying
        incrementalDedupStream.columns!![generator.buildColumnId("IamACaseSensitiveColumnName")] =
            AirbyteProtocolType.STRING
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.readRecords(
                "sqlgenerator/mixedcasecolumnname_inputrecords.jsonl"
            )
        )

        var initialState =
            getOnly(destinationHandler.gatherInitialState(listOf(incrementalDedupStream)))
        Assertions.assertTrue(
            initialState.isFinalTableEmpty,
            "Final table should be empty before T+D"
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecords(
            "sqlgenerator/mixedcasecolumnname_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/mixedcasecolumnname_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )

        initialState =
            getOnly(destinationHandler.gatherInitialState(listOf(incrementalDedupStream)))
        assertFalse(initialState.isFinalTableEmpty, "Final table should not be empty after T+D")
    }

    @Throws(Exception::class)
    private fun getInitialRawTableState(streamConfig: StreamConfig?): InitialRawTableStatus {
        val initialStates = destinationHandler.gatherInitialState(java.util.List.of(streamConfig!!))
        Assertions.assertEquals(1, initialStates.size)
        return initialStates.first().initialRawTableStatus
    }

    /**
     * Run through some plausible T+D scenarios to verify that we correctly identify the min raw
     * timestamp.
     */
    @Test
    @Throws(Exception::class)
    fun minTimestampBehavesCorrectly() {
        // When the raw table doesn't exist, there are no unprocessed records and no timestamp
        Assertions.assertEquals(
            InitialRawTableStatus(false, false, Optional.empty()),
            getInitialRawTableState(incrementalAppendStream)
        )

        // When the raw table is empty, there are still no unprocessed records and no timestamp
        createRawTable(streamId)
        Assertions.assertEquals(
            InitialRawTableStatus(true, false, Optional.empty()),
            getInitialRawTableState(incrementalAppendStream)
        )

        // If we insert some raw records with null loaded_at, we should get the min extracted_at
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {}
                }

                """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "47f46eb6-fcae-469c-a7fc-31d4b9ce7474",
                  "_airbyte_extracted_at": "2023-01-02T00:00:00Z",
                  "_airbyte_data": {}
                }

                """.trimIndent()
                )
            )
        )
        var tableState = getInitialRawTableState(incrementalAppendStream)
        Assertions.assertTrue(
            tableState.hasUnprocessedRecords,
            "When all raw records have null loaded_at, we should recognize that there are unprocessed records"
        )
        Assertions.assertTrue(
            tableState.maxProcessedTimestamp.get().isBefore(Instant.parse("2023-01-01T00:00:00Z")),
            "When all raw records have null loaded_at, the min timestamp should be earlier than all of their extracted_at values (2023-01-01). Was actually " +
                tableState.maxProcessedTimestamp.get()
        )

        // Execute T+D to set loaded_at on the records
        createFinalTable(incrementalAppendStream, "")
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalAppendStream,
            Optional.empty(),
            ""
        )

        Assertions.assertEquals(
            getInitialRawTableState(incrementalAppendStream),
            InitialRawTableStatus(true, false, Optional.of(Instant.parse("2023-01-02T00:00:00Z"))),
            "When all raw records have non-null loaded_at, we should recognize that there are no unprocessed records, and the min timestamp should be equal to the latest extracted_at"
        )

        // If we insert another raw record with older extracted_at than the typed records, we should
        // fetch a
        // timestamp earlier than this new record.
        // This emulates a sync inserting some records out of order, running T+D on newer records,
        // inserting
        // an older record, and then crashing before it can execute T+D. The next sync should
        // recognize
        // that older record as still needing to be processed.
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
              "_airbyte_extracted_at": "2023-01-01T12:00:00Z",
              "_airbyte_data": {}
            }

            """.trimIndent()
                )
            )
        )
        tableState = getInitialRawTableState(incrementalAppendStream)
        // this is a pretty confusing pair of assertions. To explain them in more detail: There are
        // three
        // records in the raw table:
        // * loaded_at not null, extracted_at = 2023-01-01 00:00Z
        // * loaded_at is null, extracted_at = 2023-01-01 12:00Z
        // * loaded_at not null, extracted_at = 2023-01-02 00:00Z
        // We should have a timestamp which is older than the second record, but newer than or equal
        // to
        // (i.e. not before) the first record. This allows us to query the raw table using
        // `_airbyte_extracted_at > ?`, which will include the second record and exclude the first
        // record.
        Assertions.assertTrue(
            tableState.hasUnprocessedRecords,
            "When some raw records have null loaded_at, we should recognize that there are unprocessed records"
        )
        Assertions.assertTrue(
            tableState.maxProcessedTimestamp.get().isBefore(Instant.parse("2023-01-01T12:00:00Z")),
            "When some raw records have null loaded_at, the min timestamp should be earlier than the oldest unloaded record (2023-01-01 12:00Z). Was actually " +
                tableState
        )
        assertFalse(
            tableState.maxProcessedTimestamp.get().isBefore(Instant.parse("2023-01-01T00:00:00Z")),
            "When some raw records have null loaded_at, the min timestamp should be later than the newest loaded record older than the oldest unloaded record (2023-01-01 00:00Z). Was actually " +
                tableState
        )
    }

    /**
     * Identical to [.allTypes], but queries for the min raw timestamp first. This verifies that if
     * a previous sync doesn't fully type-and-dedupe a table, we still get those records on the next
     * sync.
     */
    @Test
    @Throws(Exception::class)
    fun handlePreexistingRecords() {
        // Add case-sensitive columnName to test json path querying
        incrementalDedupStream.columns!!.put(
            generator.buildColumnId("IamACaseSensitiveColumnName"),
            AirbyteProtocolType.STRING
        )
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(streamId, readAllTypesInputRecords())

        val tableState = getInitialRawTableState(incrementalDedupStream)
        Assertions.assertAll(
            Executable {
                Assertions.assertTrue(
                    tableState.hasUnprocessedRecords,
                    "After writing some raw records, we should recognize that there are unprocessed records"
                )
            },
            Executable {
                Assertions.assertTrue(
                    tableState.maxProcessedTimestamp.isPresent(),
                    "After writing some raw records, the min timestamp should be present."
                )
            }
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            tableState.maxProcessedTimestamp,
            ""
        )

        verifyRecords(
            "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/alltypes_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Identical to [.handlePreexistingRecords], but queries for the min timestamp before inserting
     * any raw records. This emulates a sync starting with an empty table.
     */
    @Test
    @Throws(Exception::class)
    fun handleNoPreexistingRecords() {
        createRawTable(streamId)
        val tableState = getInitialRawTableState(incrementalDedupStream)
        Assertions.assertAll(
            Executable {
                assertFalse(
                    tableState.hasUnprocessedRecords,
                    "With an empty raw table, we should recognize that there are no unprocessed records"
                )
            },
            Executable {
                Assertions.assertEquals(
                    Optional.empty<Instant>(),
                    tableState.maxProcessedTimestamp,
                    "With an empty raw table, the min timestamp should be empty"
                )
            }
        )

        createFinalTable(incrementalDedupStream, "")
        insertRawTableRecords(streamId, readAllTypesInputRecords())

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            tableState.maxProcessedTimestamp,
            ""
        )

        verifyRecords(
            "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/alltypes_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Verify that we correctly only process raw records with recent extracted_at. In practice,
     * destinations should not do this - but their SQL should work correctly.
     *
     * Create two raw records, one with an old extracted_at. Verify that updatedTable only T+Ds the
     * new record, and doesn't set loaded_at on the old record.
     */
    @Test
    @Throws(Exception::class)
    open fun ignoreOldRawRecords() {
        createRawTable(streamId)
        createFinalTable(incrementalAppendStream, "")
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                  "_airbyte_extracted_at": "2022-01-01T00:00:00Z",
                  "_airbyte_data": {
                    "string": "foo"
                  }
                }

                """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                  "_airbyte_extracted_at": "2023-01-01T01:00:00Z",
                  "_airbyte_data": {
                    "string": "bar"
                  }
                }

                """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalAppendStream,
            Optional.of(Instant.parse("2023-01-01T00:00:00Z")),
            ""
        )

        val rawRecords = dumpRawTableRecords(streamId)
        val finalRecords = dumpFinalTableRecords(streamId, "")
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    1,
                    rawRecords
                        .filter { record: JsonNode -> record["_airbyte_loaded_at"] == null }
                        .count(),
                    "Raw table should only have non-null loaded_at on the newer record"
                )
            },
            Executable {
                Assertions.assertEquals(
                    1,
                    finalRecords.size,
                    "T+D should only execute on the newer record"
                )
            }
        )
    }

    /**
     * Test JSON Types encounted for a String Type field.
     *
     * @throws Exception
     */
    @Test
    @Throws(Exception::class)
    fun jsonStringifyTypes() {
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "_foo")
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/json_types_in_string_inputrecords.jsonl"
            )
        )
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            "_foo"
        )
        verifyRecords(
            "sqlgenerator/json_types_in_string_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/json_types_in_string_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "_foo")
        )
    }

    @Test
    @Throws(Exception::class)
    fun timestampFormats() {
        createRawTable(streamId)
        createFinalTable(incrementalAppendStream, "")
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/timestampformats_inputrecords.jsonl"
            )
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalAppendStream,
            Optional.empty(),
            ""
        )

        DIFFER!!.diffFinalTableRecords(
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/timestampformats_expectedrecords_final.jsonl"
            ),
            dumpFinalTableRecords(streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun incrementalDedup() {
        createRawTable(streamId)
        createFinalTable(incrementalDedupStream, "")
        val inputRecords: MutableList<JsonNode> =
            ArrayList(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/incrementaldedup_inputrecords.jsonl"
                )
            )
        if (supportsSafeCast) {
            inputRecords.addAll(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/safe_cast/incrementaldedup_inputrecords.jsonl"
                )
            )
        }
        insertRawTableRecords(streamId, inputRecords)

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecords(
            "sqlgenerator/incrementaldedup_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/incrementaldedup_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * We shouldn't crash on a sync with null cursor. Insert two records and verify that we keep the
     * record with higher extracted_at.
     */
    @Test
    @Throws(Exception::class)
    fun incrementalDedupNoCursor() {
        val streamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                primaryKey,
                Optional.empty(),
                COLUMNS,
                0,
                0,
                0,
            )
        createRawTable(streamId)
        createFinalTable(streamConfig, "")
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {
                    "id1": 1,
                    "id2": 100,
                    "string": "foo"
                  }
                }

                """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                {
                  "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                  "_airbyte_extracted_at": "2023-01-01T01:00:00Z",
                  "_airbyte_data": {
                    "id1": 1,
                    "id2": 100,
                    "string": "bar"
                  }
                }

                """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(generator, destinationHandler, streamConfig, Optional.empty(), "")

        val actualRawRecords = dumpRawTableRecords(streamId)
        val actualFinalRecords = dumpFinalTableRecords(streamId, "")
        verifyRecordCounts(2, actualRawRecords, 1, actualFinalRecords)
        Assertions.assertEquals(
            "bar",
            actualFinalRecords[0][generator.buildColumnId("string").name].asText()
        )
    }

    @Test
    @Throws(Exception::class)
    fun incrementalAppend() {
        createRawTable(streamId)
        createFinalTable(incrementalAppendStream, "")
        val inputRecords: MutableList<JsonNode> =
            ArrayList(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/incrementaldedup_inputrecords.jsonl"
                )
            )
        if (supportsSafeCast) {
            inputRecords.addAll(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/safe_cast/incrementaldedup_inputrecords.jsonl"
                )
            )
        }
        insertRawTableRecords(streamId, inputRecords)

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalAppendStream,
            Optional.empty(),
            ""
        )

        verifyRecordCounts(
            if (supportsSafeCast) 4 else 3,
            dumpRawTableRecords(streamId),
            if (supportsSafeCast) 4 else 3,
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Create a nonempty users_final_tmp table. Overwrite users_final from users_final_tmp. Verify
     * that users_final now exists and contains nonzero records.
     */
    @Test
    @Throws(Exception::class)
    fun overwriteFinalTable() {
        createFinalTable(incrementalAppendStream, "_tmp")
        val records =
            listOf(
                Jsons.deserialize(
                    """
        {
          "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
          "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
          "_airbyte_meta": {}
        }

        """.trimIndent()
                )
            )
        insertFinalTableRecords(false, streamId, "_tmp", records)

        val sql = generator.overwriteFinalTable(streamId, "_tmp")
        destinationHandler.execute(sql)

        Assertions.assertEquals(1, dumpFinalTableRecords(streamId, "").size)
    }

    @Test
    @Throws(Exception::class)
    fun cdcImmediateDeletion() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            listOf(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "updated_at": "2023-01-01T00:00:00Z",
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }

            """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecordCounts(1, dumpRawTableRecords(streamId), 0, dumpFinalTableRecords(streamId, ""))
    }

    /**
     * Verify that running T+D twice is idempotent. Previously there was a bug where non-dedup syncs
     * with an _ab_cdc_deleted_at column would duplicate "deleted" records on each run.
     */
    @Test
    @Throws(Exception::class)
    fun cdcIdempotent() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalAppendStream, "")
        insertRawTableRecords(
            streamId,
            listOf(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "updated_at": "2023-01-01T00:00:00Z",
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }

            """.trimIndent()
                )
            )
        )

        // Execute T+D twice
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalAppendStream,
            Optional.empty(),
            ""
        )
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalAppendStream,
            Optional.empty(),
            ""
        )

        verifyRecordCounts(1, dumpRawTableRecords(streamId), 1, dumpFinalTableRecords(streamId, ""))
    }

    @Test
    @Throws(Exception::class)
    fun cdcComplexUpdate() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalDedupStream, "")
        val inputRecords: MutableList<JsonNode> =
            ArrayList(
                BaseTypingDedupingTest.readRecords("sqlgenerator/cdcupdate_inputrecords_raw.jsonl")
            )
        if (supportsSafeCast) {
            inputRecords.addAll(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/safe_cast/cdcupdate_inputrecords_raw.jsonl"
                )
            )
        }
        insertRawTableRecords(streamId, inputRecords)
        insertFinalTableRecords(
            true,
            streamId,
            "",
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcupdate_inputrecords_final.jsonl"
            )
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalDedupStream,
            Optional.empty(),
            ""
        )

        verifyRecordCounts(
            if (supportsSafeCast) 11 else 10,
            dumpRawTableRecords(streamId),
            6,
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * source operations:
     *
     * 1. insert id=1 (lsn 10000)
     * 1. delete id=1 (lsn 10001)
     *
     * But the destination writes lsn 10001 before 10000. We should still end up with no records in
     * the final table.
     *
     * All records have the same emitted_at timestamp. This means that we live or die purely based
     * on our ability to use _ab_cdc_lsn.
     */
    @Test
    @Throws(Exception::class)
    fun testCdcOrdering_updateAfterDelete() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcordering_updateafterdelete_inputrecords.jsonl"
            )
        )

        val tableState = getInitialRawTableState(cdcIncrementalDedupStream)
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalDedupStream,
            tableState.maxProcessedTimestamp,
            ""
        )

        verifyRecordCounts(2, dumpRawTableRecords(streamId), 0, dumpFinalTableRecords(streamId, ""))
    }

    /**
     * source operations:
     *
     * 1. arbitrary history...
     * 1. delete id=1 (lsn 10001)
     * 1. reinsert id=1 (lsn 10002)
     *
     * But the destination receives LSNs 10002 before 10001. In this case, we should keep the
     * reinserted record in the final table.
     *
     * All records have the same emitted_at timestamp. This means that we live or die purely based
     * on our ability to use _ab_cdc_lsn.
     */
    @Test
    @Throws(Exception::class)
    fun testCdcOrdering_insertAfterDelete() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalDedupStream, "")
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcordering_insertafterdelete_inputrecords_raw.jsonl"
            )
        )
        insertFinalTableRecords(
            true,
            streamId,
            "",
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcordering_insertafterdelete_inputrecords_final.jsonl"
            )
        )

        val tableState = getInitialRawTableState(cdcIncrementalAppendStream)
        executeTypeAndDedupe(
            generator,
            destinationHandler,
            cdcIncrementalDedupStream,
            tableState.maxProcessedTimestamp,
            ""
        )
        verifyRecordCounts(2, dumpRawTableRecords(streamId), 1, dumpFinalTableRecords(streamId, ""))
    }

    /**
     * Create a table which includes the _ab_cdc_deleted_at column, then soft reset it using the
     * non-cdc stream config. Verify that the deleted_at column gets dropped.
     */
    @Test
    @Throws(Exception::class)
    fun softReset() {
        createRawTable(streamId)
        createFinalTable(cdcIncrementalAppendStream, "")
        insertRawTableRecords(
            streamId,
            listOf(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "arst",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_loaded_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }

            """.trimIndent()
                )
            )
        )
        insertFinalTableRecords(
            true,
            streamId,
            "",
            listOf(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "arst",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_meta": {},
              "id1": 1,
              "id2": 100,
              "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
            }

            """.trimIndent()
                )
            )
        )

        executeSoftReset(generator, destinationHandler, incrementalAppendStream)

        val actualRawRecords = dumpRawTableRecords(streamId)
        val actualFinalRecords = dumpFinalTableRecords(streamId, "")
        Assertions.assertAll(
            Executable { Assertions.assertEquals(1, actualRawRecords.size) },
            Executable { Assertions.assertEquals(1, actualFinalRecords.size) },
            Executable {
                Assertions.assertTrue(
                    actualFinalRecords.none { record: JsonNode ->
                        record.has("_ab_cdc_deleted_at")
                    },
                    "_ab_cdc_deleted_at column was expected to be dropped. Actual final table had: $actualFinalRecords"
                )
            }
        )
    }

    @Test
    @Throws(Exception::class)
    fun weirdColumnNames() {
        createRawTable(streamId)
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/weirdcolumnnames_inputrecords_raw.jsonl"
            )
        )
        val stream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                primaryKey,
                Optional.of(cursor),
                linkedMapOf(
                    generator.buildColumnId("id1") to AirbyteProtocolType.INTEGER,
                    generator.buildColumnId("id2") to AirbyteProtocolType.INTEGER,
                    generator.buildColumnId("updated_at") to
                        AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
                    generator.buildColumnId("\$starts_with_dollar_sign") to
                        AirbyteProtocolType.STRING,
                    generator.buildColumnId("includes\"doublequote") to AirbyteProtocolType.STRING,
                    generator.buildColumnId("includes'singlequote") to AirbyteProtocolType.STRING,
                    generator.buildColumnId("includes`backtick") to AirbyteProtocolType.STRING,
                    generator.buildColumnId("includes.period") to AirbyteProtocolType.STRING,
                    generator.buildColumnId("includes$\$doubledollar") to
                        AirbyteProtocolType.STRING,
                    generator.buildColumnId("endswithbackslash\\") to AirbyteProtocolType.STRING
                ),
                0,
                0,
                0,
            )

        val createTable = generator.createTable(stream, "", false)
        destinationHandler.execute(createTable)
        executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")

        verifyRecords(
            "sqlgenerator/weirdcolumnnames_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/weirdcolumnnames_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Verify that we don't crash when there are special characters in the stream namespace, name,
     * primary key, or cursor.
     */
    @ParameterizedTest
    @ValueSource(
        strings = ["$", "\${", "\${\${", "\${foo}", "\"", "'", "`", ".", "$$", "\\", "{", "}"]
    )
    @Throws(Exception::class)
    open fun noCrashOnSpecialCharacters(specialChars: String) {
        val str = specialChars + "_" + namespace + "_" + specialChars
        val originalStreamId = generator.buildStreamId(str, str, "unused")
        val modifiedStreamId =
            buildStreamId(
                originalStreamId.finalNamespace!!,
                originalStreamId.finalName!!,
                "raw_table"
            )
        val columnId = generator.buildColumnId(str)
        try {
            createNamespace(modifiedStreamId.finalNamespace)
            createRawTable(modifiedStreamId)
            insertRawTableRecords(
                modifiedStreamId,
                java.util.List.of(
                    Jsons.jsonNode(
                        java.util.Map.of(
                            "_airbyte_raw_id",
                            "758989f2-b148-4dd3-8754-30d9c17d05fb",
                            "_airbyte_extracted_at",
                            "2023-01-01T00:00:00Z",
                            "_airbyte_data",
                            java.util.Map.of(str, "bar")
                        )
                    )
                )
            )
            val stream =
                StreamConfig(
                    modifiedStreamId,
                    DestinationSyncMode.APPEND_DEDUP,
                    java.util.List.of(columnId),
                    Optional.of(columnId),
                    linkedMapOf(columnId to AirbyteProtocolType.STRING),
                    0,
                    0,
                    0,
                )

            val createTable = generator.createTable(stream, "", false)
            destinationHandler.execute(createTable)
            // Not verifying anything about the data; let's just make sure we don't crash.
            executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")
        } finally {
            teardownNamespace(modifiedStreamId.finalNamespace)
        }
    }

    /**
     * Verify column names that are reserved keywords are handled successfully. Each destination
     * should always have at least 1 column in the record data that is a reserved keyword.
     */
    @Test
    @Throws(Exception::class)
    fun testReservedKeywords() {
        createRawTable(streamId)
        insertRawTableRecords(
            streamId,
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/reservedkeywords_inputrecords_raw.jsonl"
            )
        )
        val stream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                emptyList(),
                Optional.empty(),
                linkedMapOf(
                    generator.buildColumnId("current_date") to AirbyteProtocolType.STRING,
                    generator.buildColumnId("join") to AirbyteProtocolType.STRING
                ),
                0,
                0,
                0,
            )

        val createTable = generator.createTable(stream, "", false)
        destinationHandler.execute(createTable)
        executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")

        DIFFER!!.diffFinalTableRecords(
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/reservedkeywords_expectedrecords_final.jsonl"
            ),
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * A stream with no columns is weird, but we shouldn't treat it specially in any way. It should
     * create a final table as usual, and populate it with the relevant metadata columns.
     */
    @Test
    @Throws(Exception::class)
    fun noColumns() {
        createRawTable(streamId)
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "14ba7c7f-e398-4e69-ac22-28d578400dbc",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {}
            }

            """.trimIndent()
                )
            )
        )
        val stream =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                emptyList<ColumnId>(),
                Optional.empty(),
                LinkedHashMap(),
                0,
                0,
                0,
            )

        val createTable = generator.createTable(stream, "", false)
        destinationHandler.execute(createTable)
        executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")

        verifyRecords(
            "sqlgenerator/nocolumns_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/nocolumns_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    open fun testV1V2migration() {
        // This is maybe a little hacky, but it avoids having to refactor this entire class and
        // subclasses
        // for something that is going away
        val v1RawTableStreamId =
            StreamId(
                "fake",
                "fake",
                streamId.finalNamespace,
                "v1_" + streamId.rawName,
                "fake",
                "fake"
            )
        createV1RawTable(v1RawTableStreamId)
        val inputRecords: MutableList<JsonNode> =
            ArrayList(
                BaseTypingDedupingTest.readRecords("sqlgenerator/all_types_v1_inputrecords.jsonl")
            )
        if (supportsSafeCast) {
            inputRecords.addAll(
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/safe_cast/all_types_v1_inputrecords.jsonl"
                )
            )
        }
        insertV1RawTableRecords(v1RawTableStreamId, inputRecords)
        val migration =
            generator.migrateFromV1toV2(
                streamId,
                v1RawTableStreamId.rawNamespace,
                v1RawTableStreamId.rawName
            )
        destinationHandler.execute(migration)
        val v1RawRecords = dumpV1RawTableRecords(v1RawTableStreamId)
        val v2RawRecords = dumpRawTableRecords(streamId)
        migrationAssertions(v1RawRecords, v2RawRecords)

        // And then run T+D on the migrated raw data
        val createTable = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(createTable)
        val updateTable = generator.updateTable(incrementalDedupStream, "", Optional.empty(), true)
        destinationHandler.execute(updateTable)
        verifyRecords(
            "sqlgenerator/alltypes_v1v2_expectedrecords_raw.jsonl",
            dumpRawTableRecords(streamId),
            "sqlgenerator/alltypes_v1v2_expectedrecords_final.jsonl",
            dumpFinalTableRecords(streamId, "")
        )
    }

    /**
     * Sometimes, a sync doesn't delete its soft reset temp table. (it's not entirely clear why this
     * happens.) In these cases, the next sync should not crash.
     */
    @Test
    @Throws(Exception::class)
    fun softResetIgnoresPreexistingTempTable() {
        createRawTable(incrementalDedupStream.id)

        // Create a soft reset table. Use incremental append mode, in case the destination connector
        // uses
        // different
        // indexing/partitioning/etc.
        val createOldTempTable =
            generator.createTable(incrementalDedupStream, TyperDeduperUtil.SOFT_RESET_SUFFIX, false)
        destinationHandler.execute(createOldTempTable)

        // Execute a soft reset. This should not crash.
        executeSoftReset(generator, destinationHandler, incrementalAppendStream)
    }

    protected open fun migrationAssertions(
        v1RawRecords: List<JsonNode>,
        v2RawRecords: List<JsonNode>
    ) {
        val v2RecordMap = v2RawRecords.associateBy { it["_airbyte_raw_id"].asText() }
        val expectedRecordCount: Int =
            if (supportsSafeCast) {
                5
            } else {
                // safe_cast_unsupported excludes one record with invalid data.
                4
            }
        Assertions.assertAll(
            Executable { Assertions.assertEquals(expectedRecordCount, v1RawRecords.size) },
            Executable { Assertions.assertEquals(expectedRecordCount, v2RawRecords.size) }
        )
        v1RawRecords.forEach(
            Consumer { v1Record: JsonNode ->
                val v1id = v1Record["_airbyte_ab_id"].asText()
                Assertions.assertAll(
                    Executable {
                        Assertions.assertEquals(
                            v1id,
                            v2RecordMap[v1id]!!["_airbyte_raw_id"].asText()
                        )
                    },
                    Executable {
                        Assertions.assertEquals(
                            v1Record["_airbyte_emitted_at"].asText(),
                            v2RecordMap[v1id]!!["_airbyte_extracted_at"].asText()
                        )
                    },
                    Executable { Assertions.assertNull(v2RecordMap[v1id]!!["_airbyte_loaded_at"]) }
                )
                var originalData = v1Record["_airbyte_data"]
                if (originalData.isTextual) {
                    originalData = Jsons.deserializeExact(originalData.asText())
                }
                var migratedData = v2RecordMap[v1id]!!["_airbyte_data"]
                if (migratedData.isTextual) {
                    migratedData = Jsons.deserializeExact(migratedData.asText())
                }
                // hacky thing because we only care about the data contents.
                // diffRawTableRecords makes some assumptions about the structure of the blob.
                DIFFER!!.diffFinalTableRecords(
                    java.util.List.of(originalData),
                    java.util.List.of(migratedData)
                )
            }
        )
    }

    @Throws(Exception::class)
    open protected fun dumpV1RawTableRecords(streamId: StreamId): List<JsonNode> {
        return dumpRawTableRecords(streamId)
    }

    @Test
    @Throws(Exception::class)
    fun testCreateTableForce() {
        val createTableNoForce = generator.createTable(incrementalDedupStream, "", false)
        val createTableForce = generator.createTable(incrementalDedupStream, "", true)

        destinationHandler.execute(createTableNoForce)
        Assertions.assertThrows(Exception::class.java) {
            destinationHandler.execute(createTableNoForce)
        }
        // This should not throw an exception
        destinationHandler.execute(createTableForce)
        // This method call ensures assertion than finalTable exists
        getDestinationInitialState(incrementalDedupStream)
    }

    @Test
    @Throws(Exception::class)
    open fun testStateHandling() {
        // Fetch state from an empty destination. This should not throw an error.
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of((incrementalDedupStream)))
                .first()
        // The initial state should not need a soft reset.
        assertFalse(
            initialState!!.destinationState!!.needsSoftReset(),
            "Empty state table should have needsSoftReset = false"
        )

        // Commit a state that now requires a soft reset.
        destinationHandler.commitDestinationStates(
            java.util.Map.of(
                incrementalDedupStream.id,
                initialState.destinationState.withSoftReset(true)
            )
        )
        val updatedState =
            destinationHandler
                .gatherInitialState(java.util.List.of((incrementalDedupStream)))
                .first()
        // When we re-fetch the state, it should now need a soft reset.
        Assertions.assertTrue(
            updatedState.destinationState.needsSoftReset(),
            "After committing an explicit state, expected needsSoftReset = true"
        )

        // Commit a state belonging to a different stream
        destinationHandler.commitDestinationStates(
            java.util.Map.of(
                StreamId("fake", "fake", "fake", "fake", "fake", "some_other_stream"),
                initialState.destinationState.withSoftReset(true)
            )
        )

        // Verify that we can still retrieve the state for the original stream
        val refetchedState =
            destinationHandler
                .gatherInitialState(java.util.List.of((incrementalDedupStream)))
                .first()
        // When we re-fetch the state, it should now need a soft reset.
        Assertions.assertTrue(
            refetchedState.destinationState.needsSoftReset(),
            "After committing an unrelated state, expected needsSoftReset = true"
        )
    }

    @Test
    open fun testLongIdentifierHandling() {
        val randomSuffix = Strings.addRandomSuffix("", "_", 5)
        // Hardcode this value.
        // This comes directly from the config, and currently we don't validate/mangle it.
        // TODO we should eventually switch this to be "a".repeat(512) + randomSuffix
        val rawNamespace = "some_namespace$randomSuffix"
        val finalNamespace = "b".repeat(512) + randomSuffix
        val streamName = "c".repeat(512) + randomSuffix
        // Limiting to total 127 column length for redshift. Postgres is 63.
        // Move it down if BigQuery / Snowflake complains.
        val baseColumnName = "d".repeat(120) + randomSuffix
        val columnName1 = baseColumnName + "1"
        val columnName2 = baseColumnName + "2"

        val catalogParser = CatalogParser(generator, rawNamespace)
        val stream =
            catalogParser
                .parseCatalog(
                    ConfiguredAirbyteCatalog()
                        .withStreams(
                            listOf(
                                ConfiguredAirbyteStream()
                                    .withStream(
                                        AirbyteStream()
                                            .withName(streamName)
                                            .withNamespace(finalNamespace)
                                            .withJsonSchema(
                                                Jsons.jsonNode(
                                                    mapOf(
                                                        "type" to "object",
                                                        "properties" to
                                                            mapOf(
                                                                columnName1 to
                                                                    mapOf("type" to "string"),
                                                                columnName2 to
                                                                    mapOf("type" to "string")
                                                            )
                                                    )
                                                )
                                            )
                                    )
                                    .withSyncMode(SyncMode.INCREMENTAL)
                                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            )
                        )
                )
                .streams[0]

        val streamId = stream.id
        val columnId1: ColumnId =
            stream.columns.filter { columnName1 == it.key.originalName }.keys.first()
        val columnId2: ColumnId =
            stream.columns.filter { columnName2 == it.key.originalName }.keys.first()
        LOGGER.info("Trying to use column names {} and {}", columnId1.name, columnId2.name)

        try {
            createNamespace(rawNamespace)
            createNamespace(finalNamespace)
            createRawTable(streamId)
            insertRawTableRecords(
                streamId,
                listOf(
                    Jsons.jsonNode(
                        mapOf(
                            "_airbyte_raw_id" to "ad3e8c84-e02e-4df4-b146-3d5a007b21b4",
                            "_airbyte_extracted_at" to "2023-01-01T00:00:00Z",
                            "_airbyte_data" to mapOf(columnName1 to "foo", columnName2 to "bar")
                        )
                    )
                )
            )

            val createTable = generator.createTable(stream, "", false)
            destinationHandler.execute(createTable)
            executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "")

            val rawRecords = dumpRawTableRecords(streamId)
            val finalRecords = dumpFinalTableRecords(streamId, "")
            LOGGER.info { "Dumped raw records: $rawRecords" }
            LOGGER.info { "Dumped final records: $finalRecords" }
            assertAll(
                { Assertions.assertEquals(1, rawRecords.size) },
                { Assertions.assertEquals(1, finalRecords.size) },
                // Assume that if we can find the values in the final table, that everything looks
                // right :shrug:
                { Assertions.assertEquals("foo", finalRecords[0].get(columnId1.name).asText()) },
                { Assertions.assertEquals("bar", finalRecords[0].get(columnId2.name).asText()) }
            )
        } finally {
            // do this manually b/c we're using a weird namespace that won't get handled by the
            // @AfterEach method
            teardownNamespace(rawNamespace)
            teardownNamespace(finalNamespace)
        }
    }

    @Throws(Exception::class)
    protected fun createFinalTable(stream: StreamConfig, suffix: String) {
        val createTable = generator.createTable(stream, suffix, false)
        destinationHandler.execute(createTable)
    }

    private fun verifyRecords(
        expectedRawRecordsFile: String,
        actualRawRecords: List<JsonNode>,
        expectedFinalRecordsFile: String,
        actualFinalRecords: List<JsonNode>
    ) {
        Assertions.assertAll(
            Executable {
                DIFFER!!.diffRawTableRecords(
                    BaseTypingDedupingTest.Companion.readRecords(expectedRawRecordsFile),
                    actualRawRecords
                )
            },
            Executable {
                Assertions.assertEquals(
                    0,
                    actualRawRecords
                        .filter { record: JsonNode -> !record.hasNonNull("_airbyte_loaded_at") }
                        .count()
                )
            },
            Executable {
                DIFFER!!.diffFinalTableRecords(
                    BaseTypingDedupingTest.Companion.readRecords(expectedFinalRecordsFile),
                    actualFinalRecords
                )
            }
        )
    }

    private fun verifyRecordCounts(
        expectedRawRecords: Int,
        actualRawRecords: List<JsonNode>,
        expectedFinalRecords: Int,
        actualFinalRecords: List<JsonNode>
    ) {
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    expectedRawRecords,
                    actualRawRecords.size,
                    "Raw record count was incorrect"
                )
            },
            Executable {
                Assertions.assertEquals(
                    0,
                    actualRawRecords
                        .filter { record: JsonNode -> !record.hasNonNull("_airbyte_loaded_at") }
                        .count()
                )
            },
            Executable {
                Assertions.assertEquals(
                    expectedFinalRecords,
                    actualFinalRecords.size,
                    "Final record count was incorrect"
                )
            }
        )
    }

    companion object {
        /**
         * This, along with [.FINAL_TABLE_COLUMN_NAMES_CDC], is the list of columns that should be
         * in the final table. They're useful for generating SQL queries to insert records into the
         * final table.
         */
        @JvmField
        val FINAL_TABLE_COLUMN_NAMES: List<String> =
            listOf(
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta",
                "id1",
                "id2",
                "updated_at",
                "struct",
                "array",
                "string",
                "number",
                "integer",
                "boolean",
                "timestamp_with_timezone",
                "timestamp_without_timezone",
                "time_with_timezone",
                "time_without_timezone",
                "date",
                "unknown"
            )
        @JvmField
        val FINAL_TABLE_COLUMN_NAMES_CDC: List<String> =
            FINAL_TABLE_COLUMN_NAMES + "_ab_cdc_deleted_at"
    }

    private fun readAllTypesInputRecords(
        includeSafeCastRecords: Boolean = supportsSafeCast
    ): List<JsonNode> {
        val baseRecords =
            BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl")
        return if (includeSafeCastRecords) {
            baseRecords +
                BaseTypingDedupingTest.readRecords(
                    "sqlgenerator/safe_cast/alltypes_inputrecords.jsonl"
                )
        } else {
            baseRecords
        }
    }
}
