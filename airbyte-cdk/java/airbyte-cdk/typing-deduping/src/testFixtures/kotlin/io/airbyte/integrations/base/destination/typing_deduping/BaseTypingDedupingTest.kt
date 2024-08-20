/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.lang.Exceptions
import io.airbyte.commons.resources.MoreResources
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.StreamDescriptor
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.internal.AirbyteDestination
import io.airbyte.workers.internal.DefaultAirbyteDestination
import io.airbyte.workers.process.AirbyteIntegrationLauncher
import io.airbyte.workers.process.DockerProcessFactory
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import java.util.concurrent.Callable
import java.util.concurrent.CompletableFuture
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.function.Function
import kotlin.test.assertFails
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

private val LOGGER = KotlinLogging.logger {}
/**
 * This is loosely based on standard-destination-tests's DestinationAcceptanceTest class. The
 * sync-running code is copy-pasted from there.
 *
 * All tests use a single stream, whose schema is defined in `resources/schema.json`. Each test case
 * constructs a ConfiguredAirbyteCatalog dynamically.
 *
 * For sync modes which use a primary key, the stream provides a composite key of (id1, id2). For
 * sync modes which use a cursor, the stream provides an updated_at field. The stream also has an
 * _ab_cdc_deleted_at field.
 */
// If you're running from inside intellij, you must run your specific subclass to get concurrent
// execution.
@Execution(ExecutionMode.CONCURRENT)
abstract class BaseTypingDedupingTest {
    protected var DIFFER: RecordDiffer? = null

    private var randomSuffix: String? = null
    protected var config: JsonNode? = null
        private set
    protected var streamNamespace: String? = null
    protected var streamName: String = "dummy"
    private var streamsToTearDown: MutableList<AirbyteStreamNameNamespacePair>? = null

    protected abstract val imageName: String
        /** @return the docker image to run, e.g. `"airbyte/destination-bigquery:dev"`. */
        get

    /**
     * Get the destination connector config. Subclasses may use this method for other setup work,
     * e.g. opening a connection to the destination.
     *
     * Subclasses should _not_ start testcontainers in this method; that belongs in a BeforeAll
     * method. The tests in this class are intended to be run concurrently on a shared database and
     * will not interfere with each other.
     *
     * Sublcasses which need access to the config may use [.getConfig].
     */
    @Throws(Exception::class) protected abstract fun generateConfig(): JsonNode?

    /**
     * For a given stream, return the records that exist in the destination's raw table. Each record
     * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...",
     * "_airbyte_loaded_at": "...", "_airbyte_data": {fields...}}.
     *
     * The `_airbyte_data` column must be an [com.fasterxml.jackson.databind.node.ObjectNode] (i.e.
     * it cannot be a string value).
     *
     * streamNamespace may be null, in which case you should query from the default namespace.
     */
    @Throws(Exception::class)
    protected abstract fun dumpRawTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode>

    /**
     * Utility method for tests to check if table exists
     *
     * @param streamNamespace
     * @param streamName
     * @return
     * @throws Exception
     */
    protected fun checkTableExists(streamNamespace: String?, streamName: String?): Boolean {
        // Implementation is specific to destination's tests.
        return true
    }

    /**
     * For a given stream, return the records that exist in the destination's final table. Each
     * record must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...",
     * "_airbyte_meta": {...}, "field1": ..., "field2": ..., ...}. If the destination renames (e.g.
     * upcases) the airbyte fields, this method must revert that naming to use the exact strings
     * "_airbyte_raw_id", etc.
     *
     * For JSON-valued columns, there is some nuance: a SQL null should be represented as a missing
     * entry, whereas a JSON null should be represented as a
     * [com.fasterxml.jackson.databind.node.NullNode]. For example, in the JSON blob {"name": null},
     * the `name` field is a JSON null, and the `address` field is a SQL null.
     *
     * The corresponding SQL looks like `INSERT INTO ... (name, address) VALUES ('null' :: jsonb,
     * NULL)`.
     *
     * streamNamespace may be null, in which case you should query from the default namespace.
     */
    @Throws(Exception::class)
    abstract fun dumpFinalTableRecords(streamNamespace: String?, streamName: String): List<JsonNode>

    /**
     * Delete any resources in the destination associated with this stream AND its namespace. We
     * need this because we write raw tables to a shared `airbyte` namespace, which we can't drop
     * wholesale. Must handle the case where the table/namespace doesn't exist (e.g. if the
     * connector crashed without writing any data).
     *
     * In general, this should resemble `DROP TABLE IF EXISTS
     * airbyte.<streamNamespace>_<streamName>; DROP SCHEMA IF EXISTS <streamNamespace>`.
     */
    @Throws(Exception::class)
    protected abstract fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String)

    protected abstract val sqlGenerator: SqlGenerator
        get

    /**
     * Destinations which need to clean up resources after an entire test finishes should override
     * this method. For example, if you want to gracefully close a database connection, you should
     * do that here.
     */
    @Throws(Exception::class) protected open fun globalTeardown() {}

    val rawMetadataColumnNames: Map<String, String>
        /** Conceptually identical to [.getFinalMetadataColumnNames], but for the raw table. */
        get() = HashMap()

    open val finalMetadataColumnNames: Map<String, String>
        /**
         * If the destination connector uses a nonstandard schema for the final table, override this
         * method. For example, destination-snowflake upcases all column names in the final tables.
         *
         * You only need to add mappings for the airbyte metadata column names (_airbyte_raw_id,
         * _airbyte_extracted_at, etc.). The test framework automatically populates mappings for the
         * primary key and cursor using the SqlGenerator.
         */
        get() = HashMap()

    @get:Synchronized
    protected val uniqueSuffix: String
        /**
         * @return A suffix which is different for each concurrent test, but stable within a single
         * test.
         */
        get() {
            if (randomSuffix == null) {
                randomSuffix =
                    "_" + RandomStringUtils.randomAlphabetic(10).lowercase(Locale.getDefault())
            }
            return randomSuffix!!
        }

    /**
     * Override this method only when skipping T&D and only compare raw tables and skip final table
     * comparison. For every other case it should always return false.
     *
     * @return
     */
    protected open fun disableFinalTableComparison(): Boolean {
        return false
    }

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        config = generateConfig()
        streamNamespace = "tdtest_$uniqueSuffix"
        streamName = "test_$uniqueSuffix"
        streamsToTearDown = ArrayList()

        val generator = sqlGenerator
        DIFFER =
            RecordDiffer(
                rawMetadataColumnNames,
                finalMetadataColumnNames,
                generator.buildColumnId("id1") to AirbyteProtocolType.INTEGER,
                generator.buildColumnId("id2") to AirbyteProtocolType.INTEGER,
                generator.buildColumnId("updated_at") to
                    AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
                generator.buildColumnId("old_cursor") to AirbyteProtocolType.INTEGER
            )

        LOGGER.info("Using stream namespace {} and name {}", streamNamespace, streamName)
    }

    @AfterEach
    @Throws(Exception::class)
    fun teardown() {
        for (streamId in streamsToTearDown!!) {
            teardownStreamAndNamespace(streamId.namespace, streamId.name)
        }
        globalTeardown()
    }

    /**
     * Starting with an empty destination, execute a full refresh overwrite sync. Verify that the
     * records are written to the destination table. Then run a second sync, and verify that the
     * records are overwritten.
     */
    @Throws(Exception::class)
    @Test
    open fun truncateRefresh() {
        val catalog1 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(43)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog1, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        val catalog2 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(44)
                            .withMinimumGenerationId(44)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        runSync(catalog2, messages2)

        val expectedRawRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_with_new_gen_id_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords(
                "dat/sync2_expectedrecords_fullrefresh_overwrite_with_new_gen_id_final.jsonl"
            )
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Starting with an empty destination, execute a full refresh append sync. Verify that the
     * records are written to the destination table. Then run a second sync, and verify that the old
     * and new records are all present.
     */
    @Throws(Exception::class)
    @Test
    open fun mergeRefresh() {
        val catalog1 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog1, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        val catalog2 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(44)
                            .withMinimumGenerationId(0)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        runSync(catalog2, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_with_new_gen_id_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_with_new_gen_id_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    open fun interruptedMergeRefresh(inputGenerationId: Long) {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_with_new_gen_id_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_with_new_gen_id_final.jsonl")
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Starting with an empty destination, execute an incremental append sync.
     *
     * This is (not so secretly) identical to [.fullRefreshAppend], and uses the same set of
     * expected records. Incremental as a concept only exists in the source. From the destination's
     * perspective, we only care about the destination sync mode.
     */
    @Throws(Exception::class)
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    fun incrementalAppend(inputGenerationId: Long) {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0) // These two lines are literally the only
                            // difference between this test and
                            // fullRefreshAppend
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Starting with an empty destination, execute an incremental dedup sync. Verify that the
     * records are written to the destination table. Then run a second sync, and verify that the
     * raw/final tables contain the correct records.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    fun incrementalDedup(inputGenerationId: Long) {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Run the first sync from [.incrementalDedup], but repeat the messages many times. Some
     * destinations behave differently with small vs large record count, so this test case tries to
     * exercise that behavior.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    open fun largeDedupSync(inputGenerationId: Long) {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // Run a sync with 25K copies of the input messages
        val messages1 = repeatList(25000, readMessages("dat/sync1_messages.jsonl"))

        runSync(catalog, messages1)

        // The raw table will contain 25K copies of each record
        val expectedRawRecords1 =
            repeatList(25000, readRecords("dat/sync1_expectedrecords_raw.jsonl"))
        // But the final table should be fully deduped
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())
    }

    /** Identical to [.incrementalDedup], except that the stream has no namespace. */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    fun incrementalDedupDefaultNamespace(inputGenerationId: Long) {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream() // NB: we don't call `withNamespace` here
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl", null, streamName)

        runSync(catalog, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(
            expectedRawRecords1,
            expectedFinalRecords1,
            null,
            streamName,
            disableFinalTableComparison()
        )

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl", null, streamName)

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)
        verifySyncResult(
            expectedRawRecords2,
            expectedFinalRecords2,
            null,
            streamName,
            disableFinalTableComparison()
        )
    }

    @Test
    @Disabled("Not yet implemented")
    @Throws(Exception::class)
    fun testLineBreakCharacters() {
        // TODO verify that we can handle strings with interesting characters
        // build an airbyterecordmessage using something like this, and add it to the input
        // messages:
        Jsons.jsonNode(
            ImmutableMap.builder<Any, Any>()
                .put("id", 1)
                .put("currency", "USD\u2028")
                .put(
                    "date",
                    "2020-03-\n31T00:00:00Z\r"
                ) // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores
                // 10.1 as "10" which
                // fails destination tests
                .put("HKD", 10.1)
                .put("NZD", 700.1)
                .build()
        )
    }

    /**
     * Run a sync, then remove the `name` column from the schema and run a second sync. Verify that
     * the final table doesn't contain the `name` column after the second sync.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    fun testIncrementalSyncDropOneColumn(inputGenerationId: Long) {
        val stream =
            AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA)
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(inputGenerationId)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(stream)
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(catalog, messages1)

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        val trimmedSchema = SCHEMA.deepCopy<JsonNode>()
        (trimmedSchema["properties"] as ObjectNode).remove("name")
        stream.jsonSchema = trimmedSchema

        runSync(catalog, messages2)

        // The raw data is unaffected by the schema, but the final table should not have a `name`
        // column.
        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        expectedFinalRecords2.forEach { record: JsonNode ->
            (record as ObjectNode).remove(sqlGenerator.buildColumnId("name").name)
        }
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)

        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Disabled("Not yet implemented")
    @Throws(Exception::class)
    fun testSyncUsesAirbyteStreamNamespaceIfNotNull() {
        // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using a stream with null
        // namespace:
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(43)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(null)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )
    }

    // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using two streams with the
    // same
    // name but different namespace
    // TODO maybe we don't even need the single-stream versions...
    /**
     * Identical to [.incrementalDedup], except there are two streams with the same name and
     * different namespace.
     */
    @Test
    @Throws(Exception::class)
    fun incrementalDedupIdenticalName() {
        val namespace1 = streamNamespace + "_1"
        val namespace2 = streamNamespace + "_2"
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(namespace1)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(namespace2)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 =
            readMessages("dat/sync1_messages.jsonl", namespace1, streamName) +
                readMessages("dat/sync1_messages2.jsonl", namespace2, streamName)

        runSync(catalog, messages1)

        verifySyncResult(
            readRecords("dat/sync1_expectedrecords_raw.jsonl"),
            readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
            namespace1,
            streamName,
            disableFinalTableComparison()
        )
        verifySyncResult(
            readRecords("dat/sync1_expectedrecords_raw2.jsonl"),
            readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
            namespace2,
            streamName,
            disableFinalTableComparison()
        )

        // Second sync
        val messages2 =
            readMessages("dat/sync2_messages.jsonl", namespace1, streamName) +
                readMessages("dat/sync2_messages2.jsonl", namespace2, streamName)
        runSync(catalog, messages2)

        verifySyncResult(
            readRecords("dat/sync2_expectedrecords_raw.jsonl"),
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl"),
            namespace1,
            streamName,
            disableFinalTableComparison()
        )
        verifySyncResult(
            readRecords("dat/sync2_expectedrecords_raw2.jsonl"),
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final2.jsonl"),
            namespace2,
            streamName,
            disableFinalTableComparison()
        )
    }

    /**
     * Run two syncs at the same time. They each have one stream, which has the same name for both
     * syncs but different namespace. This should work fine. This test is similar to
     * [.incrementalDedupIdenticalName], but uses two separate syncs instead of one sync with two
     * streams.
     *
     * Note that destination stdout is a bit misleading: The two syncs' stdout _should_ be
     * interleaved, but we're just dumping the entire sync1 stdout, and then the entire sync2
     * stdout.
     */
    @Test
    @Throws(Exception::class)
    open fun identicalNameSimultaneousSync() {
        val namespace1 = streamNamespace + "_1"
        val catalog1 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(namespace1)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        val namespace2 = streamNamespace + "_2"
        val catalog2 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(namespace2)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        val messages1 = readMessages("dat/sync1_messages.jsonl", namespace1, streamName)
        val messages2 = readMessages("dat/sync1_messages2.jsonl", namespace2, streamName)

        // Start two concurrent syncs
        val sync1 = startSync(catalog1)
        val sync2 = startSync(catalog2)
        val outFuture1 = destinationOutputFuture(sync1)
        val outFuture2 = destinationOutputFuture(sync2)

        // Write some messages to both syncs. Write a lot of data to sync 2 to try and force a
        // flush.
        pushMessages(messages1, sync1)
        val nTimes = 100000
        for (i in 0..nTimes - 1) {
            pushMessages(messages2, sync2)
        }
        pushStatusMessages(catalog1, sync1, AirbyteStreamStatus.COMPLETE)
        endSync(sync1, outFuture1)
        // Write some more messages to the second sync. It should not be affected by the first
        // sync's
        // shutdown.
        for (i in 0..nTimes - 1) {
            pushMessages(messages2, sync2)
        }
        pushStatusMessages(catalog2, sync2, AirbyteStreamStatus.COMPLETE)
        endSync(sync2, outFuture2)

        // For simplicity, just assert on raw record count.
        // Seems safe to assume that if we have the right number of records on both tables,
        // that we wrote the data correctly.
        val rawRecords1 = dumpRawTableRecords(namespace1, streamName)
        val rawRecords2 = dumpRawTableRecords(namespace2, streamName)
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(messages1.size.toLong(), rawRecords1.size.toLong())
            },
            Executable {
                Assertions.assertEquals(
                    2 * nTimes * messages2.size.toLong(),
                    rawRecords2.size.toLong()
                )
            },
        )

        if (!disableFinalTableComparison()) {
            Assertions.assertAll(
                Executable {
                    DIFFER!!.diffFinalTableRecords(
                        readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
                        dumpFinalTableRecords(namespace1, streamName)
                    )
                },
                Executable {
                    DIFFER!!.diffFinalTableRecords(
                        readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
                        dumpFinalTableRecords(namespace2, streamName)
                    )
                }
            )
        }
    }

    @Test
    @Disabled("Not yet implemented")
    @Throws(Exception::class)
    fun testSyncNotFailsWithNewFields() {
        // TODO duplicate this test for each sync mode. Run a sync, then add a new field to the
        // schema, then
        // run another sync
        // We might want to write a test that verifies more general schema evolution (e.g. all valid
        // evolutions)
    }

    /**
     * Change the cursor column in the second sync to a column that doesn't exist in the first sync.
     * Verify that we overwrite everything correctly.
     *
     * This essentially verifies that the destination connector correctly recognizes NULL cursors as
     * older than non-NULL cursors.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    fun incrementalDedupChangeCursor(inputGenerationId: Long) {
        val mangledSchema = SCHEMA.deepCopy<JsonNode>()
        (mangledSchema["properties"] as ObjectNode).remove("updated_at")
        (mangledSchema["properties"] as ObjectNode).set<JsonNode>(
            "old_cursor",
            Jsons.deserialize(
                """
            {"type": "integer"}
            
            """.trimIndent()
            )
        )
        val configuredStream =
            ConfiguredAirbyteStream()
                .withSyncId(42)
                .withGenerationId(inputGenerationId)
                .withMinimumGenerationId(0)
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(listOf("old_cursor"))
                .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                .withStream(
                    AirbyteStream()
                        .withNamespace(streamNamespace)
                        .withName(streamName)
                        .withJsonSchema(mangledSchema)
                )
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(java.util.List.of(configuredStream))

        // First sync
        val messages1 = readMessages("dat/sync1_cursorchange_messages.jsonl")

        runSync(catalog, messages1)

        val expectedRawRecords1 =
            readRecords("dat/sync1_cursorchange_expectedrecords_dedup_raw.jsonl")
        val expectedFinalRecords1 =
            readRecords("dat/sync1_cursorchange_expectedrecords_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        configuredStream.stream.jsonSchema = SCHEMA
        configuredStream.cursorField = listOf("updated_at")

        runSync(catalog, messages2)

        val expectedRawRecords2 =
            readRecords("dat/sync2_cursorchange_expectedrecords_incremental_dedup_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_cursorchange_expectedrecords_incremental_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords2, expectedFinalRecords2, inputGenerationId)
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Disabled("Not yet implemented")
    @Throws(Exception::class)
    fun testSyncWithLargeRecordBatch() {
        // TODO duplicate this test for each sync mode. Run a single sync with many records
        /*
         * copied from DATs: This serves to test MSSQL 2100 limit parameters in a single query. this means
         * that for Airbyte insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100
         * params
         *
         * this maybe needs configuration per destination to specify that limit?
         */
    }

    @Test
    @Disabled("Not yet implemented")
    @Throws(Exception::class)
    fun testDataTypes() {
        // TODO duplicate this test for each sync mode. See DataTypeTestArgumentProvider for what
        // this test
        // does in DAT-land
        // we probably don't want to do the exact same thing, but the general spirit of testing a
        // wide range
        // of values for every data type is approximately correct
        // this test probably needs some configuration per destination to specify what values are
        // supported?
    }

    @Test
    fun testDisableTypingDeduping() {
        assumeTrue(disableFinalTableComparison(), "Skipping test because T+D is enabled.")

        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(43)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages1)

        assertFails(
            "Expected final table to not exist, but we were able to read records from it."
        ) { dumpFinalTableRecords(streamNamespace, streamName) }
    }

    @Test
    open fun interruptedTruncateWithPriorData() {
        val catalog0 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(41)
                            .withMinimumGenerationId(41)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )
        runSync(
            catalog0,
            readMessages("dat/sync1_messages.jsonl") + readMessages("dat/sync2_messages.jsonl")
        )

        val expectedRawRecords0 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords0 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        fixGenerationId(expectedRawRecords0, expectedFinalRecords0, 41)
        verifySyncResult(expectedRawRecords0, expectedFinalRecords0, disableFinalTableComparison())

        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            // notice we changed the generationId and the minimumGenerationId
                            .withGenerationId(43)
                            .withMinimumGenerationId(43)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync. We make it fail.
        try {
            runSync(catalog, readMessages("dat/sync1_messages.jsonl"), streamStatus = null)
            fail("sync should have errored out!")
        } catch (e: TestHarnessException) {}

        // raw and final table should have been left alone as is
        verifySyncResult(expectedRawRecords0, expectedFinalRecords0, disableFinalTableComparison())

        // notice we re-write the same records we wrote earlier
        runSync(catalog, readMessages("dat/sync1_messages.jsonl"))

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        verifySyncResult(
            expectedRawRecords1 + expectedRawRecords1,
            expectedFinalRecords1 + expectedFinalRecords1,
            disableFinalTableComparison()
        )
    }

    @Test
    @Throws(Exception::class)
    open fun interruptedOverwriteWithoutPriorData() {
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(43)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        runSync(catalog, readMessages("dat/sync1_messages.jsonl"))

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        runSync(catalog, readMessages("dat/sync2_messages.jsonl"))

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Emulates this sequence of events:
     * 1. User runs a normal incremental sync
     * 2. User initiates a truncate refresh, but it fails.
     * 3. User cancels the truncate refresh, and initiates a normal incremental sync.
     *
     * In particular, we must retain all records from both the first sync, _and_ the truncate sync's
     * temporary raw table.
     */
    @Test
    @Throws(Exception::class)
    open fun resumeAfterCancelledTruncate() {
        val catalog1 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // Normal sync
        runSync(catalog1, readMessages("dat/sync1_messages.jsonl"))

        val expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl")
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        val catalog2 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            // Generation ID is incremented
                            .withGenerationId(44)
                            .withMinimumGenerationId(44)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )
        // Interrupted truncate sync
        assertThrows<Exception> {
            runSync(
                catalog2,
                readMessages("dat/sync2_messages.jsonl"),
                streamStatus = AirbyteStreamStatus.INCOMPLETE,
            )
        }

        // We should still have the exact same records as after the initial sync
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        val catalog3 =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            // Same generation as the truncate sync, but now with
                            // min gen = 0
                            .withGenerationId(44)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // Third sync
        runSync(catalog3, readMessages("dat/sync2_messages.jsonl"))

        // We wrote the sync2 records twice, so expect duplicates.
        // But we didn't write the sync1 records twice, so filter those out in a dumb way.
        // Also override the generation ID to the correct value on the sync2 records,
        // but leave the sync1 records with their original generation.
        val expectedRawRecords2 =
            readRecords("dat/sync2_expectedrecords_raw.jsonl").let { baseRecords ->
                val sync2Records =
                    baseRecords.subList(expectedRawRecords1.size, baseRecords.size).onEach {
                        (it as ObjectNode).put(
                            JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                            44,
                        )
                    }
                expectedRawRecords1 + sync2Records + sync2Records
            }
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl").let {
                baseRecords ->
                val sync2Records =
                    baseRecords.subList(expectedFinalRecords1.size, baseRecords.size).onEach {
                        (it as ObjectNode).put(
                            finalMetadataColumnNames.getOrDefault(
                                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
                            ),
                            44,
                        )
                    }
                expectedFinalRecords1 + sync2Records + sync2Records
            }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    open val manyStreamCount = 20

    @Test
    open fun testManyStreamsCompletion() {
        var streams = mutableListOf<ConfiguredAirbyteStream>()
        val messages = mutableListOf<AirbyteMessage>()
        for (i in 0..manyStreamCount) {
            val currentStreamName = streamName + "_" + i
            streams.add(
                ConfiguredAirbyteStream()
                    .withSyncId(42)
                    .withGenerationId(43)
                    .withMinimumGenerationId(43)
                    .withSyncMode(SyncMode.FULL_REFRESH)
                    .withCursorField(listOf("updated_at"))
                    .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                    .withStream(
                        AirbyteStream()
                            .withNamespace(streamNamespace)
                            .withName(currentStreamName)
                            .withJsonSchema(SCHEMA)
                    )
            )
            messages.addAll(
                readMessages("dat/sync1_messages.jsonl", streamNamespace, currentStreamName)
            )
        }
        val catalog = io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog().withStreams(streams)

        assertDoesNotThrow { runSync(catalog, messages) }
        // we just make sure it completes
    }

    private fun <T> repeatList(n: Int, list: List<T>): List<T> {
        return Collections.nCopies(n, list).flatMap { obj: List<T> -> obj }
    }

    @Throws(Exception::class)
    protected fun verifySyncResult(
        expectedRawRecords: List<JsonNode>,
        expectedFinalRecords: List<JsonNode>,
        disableFinalTableComparison: Boolean
    ) {
        verifySyncResult(
            expectedRawRecords,
            expectedFinalRecords,
            streamNamespace,
            streamName,
            disableFinalTableComparison
        )
    }

    @Throws(Exception::class)
    private fun verifySyncResult(
        expectedRawRecords: List<JsonNode>,
        expectedFinalRecords: List<JsonNode>,
        streamNamespace: String?,
        streamName: String,
        disableFinalTableComparison: Boolean
    ) {
        val actualRawRecords = dumpRawTableRecords(streamNamespace, streamName)

        if (disableFinalTableComparison) {
            DIFFER!!.diffRawTableRecords(expectedRawRecords, actualRawRecords)
        } else {
            val actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName)
            DIFFER!!.verifySyncResult(
                expectedRawRecords,
                actualRawRecords,
                expectedFinalRecords,
                actualFinalRecords
            )
        }
    }

    /*
     * !!!!!! WARNING !!!!!! The code below was mostly copypasted from DestinationAcceptanceTest. If you
     * make edits here, you probably want to also edit there.
     */
    /**
     * @param streamStatus After pushing all the messages in [messages], push a stream status
     * message for each stream. If this parameter is `null`, then instead do NOT push any status
     * messages.
     */
    @JvmOverloads
    @Throws(Exception::class)
    protected fun runSync(
        catalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>,
        imageName: String = this.imageName,
        configTransformer: Function<JsonNode?, JsonNode?> = Function.identity(),
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE
    ) {
        val destination = startSync(catalog, imageName, configTransformer)
        val outputFuture = destinationOutputFuture(destination)
        pushMessages(messages, destination)
        if (streamStatus != null) {
            pushStatusMessages(catalog, destination, streamStatus)
        }
        endSync(destination, outputFuture)
    }

    private fun pushStatusMessages(
        catalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        destination: AirbyteDestination,
        streamStatus: AirbyteStreamStatus
    ) {
        catalog.streams.forEach {
            destination.accept(
                io.airbyte.protocol.models
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace(it.stream.namespace)
                                            .withName(it.stream.name),
                                    )
                                    .withStatus(streamStatus),
                            ),
                    ),
            )
        }
    }

    // In the background, read messages from the destination until it terminates. We need to clear
    // stdout in real time, to prevent the buffer from filling up and blocking the destination.
    private fun destinationOutputFuture(
        destination: AirbyteDestination
    ): CompletableFuture<List<io.airbyte.protocol.models.AirbyteMessage>> {
        val outputFuture = CompletableFuture<List<io.airbyte.protocol.models.AirbyteMessage>>()
        Executors.newSingleThreadExecutor()
            .submit<Void>(
                Callable<Void> {
                    val destinationMessages:
                        MutableList<io.airbyte.protocol.models.AirbyteMessage> =
                        ArrayList()
                    while (!destination.isFinished()) {
                        // attemptRead isn't threadsafe, we read stdout fully here.
                        // i.e. we shouldn't call attemptRead anywhere else.
                        destination.attemptRead().ifPresent {
                            e: io.airbyte.protocol.models.AirbyteMessage ->
                            destinationMessages.add(e)
                        }
                    }
                    outputFuture.complete(destinationMessages)
                    null
                }
            )
        return outputFuture
    }

    /**
     *
     * @param catalog
     * @param imageName
     * @param configTransformer
     * - test specific config overrides or additions can be performed with this function
     * @return
     * @throws Exception
     */
    @Throws(Exception::class)
    protected fun startSync(
        catalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        imageName: String = this.imageName,
        configTransformer: Function<JsonNode?, JsonNode?> = Function.identity()
    ): AirbyteDestination {
        synchronized(this) {
            catalog.streams.forEach(
                Consumer { s: ConfiguredAirbyteStream ->
                    streamsToTearDown!!.add(
                        AirbyteStreamNameNamespacePair.fromAirbyteStream(s.stream)
                    )
                }
            )
        }

        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        val jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
        val localRoot = Files.createTempDirectory(testDir, "output")
        val processFactory: ProcessFactory =
            DockerProcessFactory(
                workspaceRoot,
                workspaceRoot.toString(),
                localRoot.toString(),
                "host",
                emptyMap()
            )
        val transformedConfig = configTransformer.apply(config)
        val destinationConfig =
            WorkerDestinationConfig()
                .withConnectionId(UUID.randomUUID())
                .withCatalog(convertProtocolObject(catalog, ConfiguredAirbyteCatalog::class.java))
                .withDestinationConnectionConfiguration(transformedConfig)

        val destination: AirbyteDestination =
            DefaultAirbyteDestination(
                integrationLauncher =
                    AirbyteIntegrationLauncher(
                        "0",
                        0,
                        imageName,
                        processFactory,
                        null,
                        null,
                        false,
                        EnvVariableFeatureFlags()
                    )
            )

        destination.start(destinationConfig, jobRoot, emptyMap())

        return destination
    }

    @Throws(Exception::class)
    protected fun endSync(
        destination: AirbyteDestination,
        destinationOutputFuture: CompletableFuture<List<io.airbyte.protocol.models.AirbyteMessage>>
    ) {
        destination.notifyEndOfInput()
        // TODO Eventually we'll want to somehow extract the state messages while a sync is running,
        // to
        // verify checkpointing.
        destinationOutputFuture.get()
        destination.close()
    }

    protected fun readMessages(filename: String): List<AirbyteMessage> {
        return Companion.readMessages(filename, streamNamespace, streamName)
    }

    protected fun readRecords(filename: String): List<JsonNode> {
        return Companion.readRecords(filename)
    }

    fun fixGenerationId(
        rawRecords: List<JsonNode>,
        finalRecords: List<JsonNode>,
        generationId: Long
    ) {
        rawRecords.forEach {
            (it as ObjectNode).put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId)
        }
        finalRecords.forEach {
            (it as ObjectNode).put(
                finalMetadataColumnNames.getOrDefault(
                    JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                    JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
                ),
                generationId
            )
        }
    }

    val schema: JsonNode = SCHEMA

    companion object {
        @JvmStatic val SCHEMA: JsonNode

        init {
            try {
                SCHEMA = Jsons.deserialize(MoreResources.readResource("dat/schema.json"))
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }

        @Throws(IOException::class)
        fun readRecords(filename: String): List<JsonNode> {
            return MoreResources.readResource(filename)
                .lines()
                .map { obj: String -> obj.trim { it <= ' ' } }
                .filter { line: String -> !line.isEmpty() }
                .filter { line: String -> !line.startsWith("//") }
                .map { jsonString: String -> Jsons.deserializeExact(jsonString) }
        }

        @Throws(IOException::class)
        protected fun readMessages(
            filename: String,
            streamNamespace: String?,
            streamName: String?
        ): List<AirbyteMessage> {
            return readRecords(filename)
                .map { record: JsonNode -> Jsons.convertValue(record, AirbyteMessage::class.java) }
                .onEach { message: AirbyteMessage ->
                    message.record.namespace = streamNamespace
                    message.record.stream = streamName
                }
        }

        protected fun pushMessages(
            messages: List<AirbyteMessage>,
            destination: AirbyteDestination
        ) {
            messages.forEach(
                Consumer { message: AirbyteMessage ->
                    Exceptions.toRuntime {
                        destination.accept(
                            convertProtocolObject(
                                message,
                                io.airbyte.protocol.models.AirbyteMessage::class.java
                            )!!
                        )
                    }
                }
            )
        }

        private fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0? {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)
        }
    }
}
