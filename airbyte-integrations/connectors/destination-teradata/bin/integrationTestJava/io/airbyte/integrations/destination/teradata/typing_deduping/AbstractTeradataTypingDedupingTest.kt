/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.lang.Exceptions
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.destination.teradata.TeradataDestination
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.protocol.models.StreamDescriptor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.workers.internal.AirbyteDestination
import java.io.IOException
import java.time.Duration
import java.util.*
import java.util.concurrent.Callable
import java.util.concurrent.CompletableFuture
import java.util.concurrent.Executors
import java.util.function.Consumer
import javax.sql.DataSource
import kotlin.random.Random
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * Abstract test class for testing Typing and Deduping behavior of the Teradata destination.
 *
 * This test framework integrates with ClearScape environment provisioning via {@link
 * ClearScapeManager}, supports concurrent syncs, failure handling, and raw/final table state
 * verification.
 *
 * The test is built on top of {@link JdbcTypingDedupingTest} to leverage the standard JDBC testing
 * structure.
 *
 * Subclasses must implement {@link #configFileName} to provide the path to the Teradata environment
 * config.
 */
@Execution(ExecutionMode.SAME_THREAD)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class AbstractTeradataTypingDedupingTest : JdbcTypingDedupingTest() {
    /** Docker image used for the Teradata destination container. */
    override val imageName: String
        get() = "airbyte/destination-teradata:dev"
    /** SQL generator specific to Teradata. */
    override val sqlGenerator: SqlGenerator
        get() = TeradataSqlGenerator()
    /** JDBC-compatible operations for Teradata source data handling. */
    override val sourceOperations: JdbcCompatibleSourceOperations<*>
        get() = TeradataSourceOperations()

    /** Setup logic to run before each test. Initializes random stream and schema names. */
    @BeforeEach
    @Throws(Exception::class)
    fun setupBETeradata() {
        super.setup()
        val schemaName = generateRandomAlphabeticLowercase(10)
        streamNamespace = "tdtest_$schemaName"
        streamName = "test_$schemaName"
    }

    private fun generateRandomAlphabeticLowercase(length: Int): String {
        val chars = ('a'..'z')
        return (1..length)
            .map { chars.random(Random.Default) }
            .joinToString("")
            .lowercase(Locale.getDefault())
    }
    /**
     * Provides a JDBC DataSource for Teradata using the test configuration.
     *
     * @param config the destination config as JsonNode
     * @return the initialized DataSource
     */
    override fun getDataSource(config: JsonNode?): DataSource? {
        val dest: TeradataDestination = TeradataDestination()
        val jdbcConfig = config?.let { dest.toJdbcConfig(it) }
        return DataSourceFactory.create(
            jdbcConfig?.get(JdbcUtils.USERNAME_KEY)?.asText(),
            if (jdbcConfig?.has(JdbcUtils.PASSWORD_KEY) == true)
                jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            TeradataConstants.DRIVER_CLASS,
            jdbcConfig?.get(JdbcUtils.JDBC_URL_KEY)?.asText(),
            config?.let { dest.getConnectionProperties(it) },
            Duration.ofSeconds(10),
        )
    }
    /**
     * Cleans up all resources related to a specific stream and namespace in the Teradata
     * environment.
     *
     * @param streamNamespace the namespace/schema of the stream
     * @param streamName the name of the stream
     */
    @Throws(Exception::class)
    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var namespace = streamNamespace
        if (namespace == null) {
            namespace = getDefaultSchema(config!!)
        }
        val rawTableName =
            nameTransformer.convertStreamName(
                concatenateRawTableName(
                    namespace,
                    streamName,
                ),
            )
        if (isTableExists(database, rawSchema, rawTableName)) {
            database!!.execute(
                java.lang.String.format(
                    "DROP TABLE %s.%s;",
                    rawSchema,
                    rawTableName,
                ),
            )
        }
        if (isSchemaExists(database, namespace)) {
            // Delete drops all everything in database. So no need to drop only given table
            database!!.execute(java.lang.String.format("DELETE DATABASE %s;", namespace))
            database!!.execute(java.lang.String.format("DROP DATABASE %s;", namespace))
        }
    }

    /**
     * Run the first sync from [.incrementalDedup], but repeat the messages many times. Some
     * destinations behave differently with small vs large record count, so this test case tries to
     * exercise that behavior.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 42L])
    @Throws(Exception::class)
    override fun largeDedupSync(inputGenerationId: Long) {
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        val noOfRecords = 50
        // Run a sync with 250 records
        val messages1 = repeatList(noOfRecords, readMessages("dat/sync1_messages.jsonl"))

        runSync(catalog, messages1)

        // The raw table will contain 500 copies of each record
        val expectedRawRecords1 =
            repeatList(noOfRecords, readRecords("dat/sync1_expectedrecords_raw.jsonl"))
        // But the final table should be fully deduped
        val expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl")
        fixGenerationId(expectedRawRecords1, expectedFinalRecords1, inputGenerationId)
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())
    }

    /**
     * Emulates this sequence of events:
     * 1. User runs a normal incremental sync
     * 2. User initiates a truncate refresh, but it fails.
     * 3. User cancels the truncate refresh, and initiates a normal incremental sync.
     * @TestInstance(TestInstance.Lifecycle.PER_CLASS) * In particular, we must retain all records
     * from both the first sync, _and_ the truncate sync's temporary raw table.
     */
    @Test
    @Throws(Exception::class)
    override fun resumeAfterCancelledTruncate() {
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        // Third sync
        runSync(catalog3, readMessages("dat/sync2_messages.jsonl"))

        val expectedRawRecords2 =
            readRecords("dat/sync2_expectedrecords_raw.jsonl").let { baseRecords ->
                val sync2Records =
                    baseRecords.subList(expectedRawRecords1.size, baseRecords.size).onEach {
                        (it as ObjectNode).put(
                            JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                            44,
                        )
                    }
                expectedRawRecords1 + sync2Records
            }
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl").let {
                baseRecords ->
                val sync2Records =
                    baseRecords.subList(expectedFinalRecords1.size, baseRecords.size).onEach {
                        (it as ObjectNode).put(
                            finalMetadataColumnNames.getOrDefault(
                                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                            ),
                            44,
                        )
                    }
                expectedFinalRecords1 + sync2Records
            }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
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
    override fun identicalNameSimultaneousSync() {

        // In Teradata, [Error 3598] [SQLState 40001] Concurrent change conflict on database -- try
        // again is raising when more than one database is trying to crate. So creating databases
        // infornt
        val namespace1 = streamNamespace + "_1"
        createSchemaIfNotExists(database, namespace1)
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        val namespace2 = streamNamespace + "_2"
        createSchemaIfNotExists(database, namespace2)
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
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
        val nTimes = 100
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
                    rawRecords2.size.toLong(),
                )
            },
        )

        if (!disableFinalTableComparison()) {
            Assertions.assertAll(
                Executable {
                    DIFFER!!.diffFinalTableRecords(
                        readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
                        dumpFinalTableRecords(namespace1, streamName),
                    )
                },
                Executable {
                    DIFFER!!.diffFinalTableRecords(
                        readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
                        dumpFinalTableRecords(namespace2, streamName),
                    )
                },
            )
        }
    }
    /** Sends STREAM_STATUS trace messages to the destination for all streams in the catalog. */
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
    /** Pushes a list of Airbyte messages to the destination. */
    protected fun pushMessages(messages: List<AirbyteMessage>, destination: AirbyteDestination) {
        messages.forEach(
            Consumer { message: AirbyteMessage ->
                Exceptions.toRuntime {
                    destination.accept(
                        convertProtocolObject(
                            message,
                            io.airbyte.protocol.models.AirbyteMessage::class.java,
                        )!!,
                    )
                }
            },
        )
    }
    /** Converts protocol object V1 to V0 type using JSON serialization/deserialization. */
    private fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0? {
        return Jsons.`object`(Jsons.jsonNode(v1), klass)
    }
    /** Reads a list of Airbyte messages from a JSONL file and attaches stream metadata. */
    @Throws(IOException::class)
    protected fun readMessages(
        filename: String,
        streamNamespace: String?,
        streamName: String?
    ): List<AirbyteMessage> {
        return BaseTypingDedupingTest.readRecords(filename)
            .map { record: JsonNode -> Jsons.convertValue(record, AirbyteMessage::class.java) }
            .onEach { message: AirbyteMessage ->
                message.record.namespace = streamNamespace
                message.record.stream = streamName
            }
    }

    /**
     * Reads output from the destination in a non-blocking way. Prevents output buffer overflow
     * during tests.
     */

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
                },
            )
        return outputFuture
    }
    /** Utility to repeat a list N times into a flat list. */
    protected fun <T> repeatList(n: Int, list: List<T>): List<T> {
        return Collections.nCopies(n, list).flatMap { obj: List<T> -> obj }
    }
    /** Checks whether a given table exists in the schema. */
    protected fun isTableExists(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): Boolean {
        return (database?.queryInt(
            "SELECT count(1)  FROM DBC.TablesV WHERE TableName = '$tableName'  AND DataBaseName = '$schemaName' ",
        )
            ?: 0) > 0
    }
    /** Checks whether a schema exists in the Teradata database. */
    protected fun isSchemaExists(database: JdbcDatabase?, schemaName: String?): Boolean {
        return (database?.queryInt(
            String.format(
                "SELECT COUNT(1) FROM DBC.DatabasesV WHERE DatabaseName = '%s'",
                schemaName,
            ),
        )
            ?: 0) > 0 // If the result is greater than 0, return true, else false
    }

    /** Creates a schema/database if it does not already exist. */
    protected fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String) {
        if (!isSchemaExists(database, schemaName)) {
            database?.execute(
                String.format(
                    "CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;",
                    schemaName,
                ),
            )
        }
    }
}
