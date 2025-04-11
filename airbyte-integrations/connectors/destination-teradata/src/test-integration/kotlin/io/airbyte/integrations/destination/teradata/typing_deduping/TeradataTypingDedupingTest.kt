/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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
import io.airbyte.commons.map.MoreMaps
import io.airbyte.commons.resources.MoreResources
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.destination.teradata.TeradataBaseTest
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
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.internal.AirbyteDestination
import java.io.IOException
import java.time.Duration
import java.util.ArrayList
import java.util.concurrent.Callable
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.function.Consumer
import javax.sql.DataSource
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.fail
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

@Execution(ExecutionMode.SAME_THREAD)
open class TeradataTypingDedupingTest : JdbcTypingDedupingTest() {

    override val imageName: String
        get() = "airbyte/destination-teradata:dev"

    override val sqlGenerator: SqlGenerator
        get() = TeradataSqlGenerator()

    override val sourceOperations: JdbcCompatibleSourceOperations<*>
        get() = TeradataSourceOperations()

    override fun getBaseConfig(): ObjectNode {
        return TeradataBaseTest.configJson as ObjectNode
    }

    override fun getDataSource(config: JsonNode?): DataSource? {
        val jdbcConfig = config?.let { dest.toJdbcConfig(it) }
        return DataSourceFactory.create(
            jdbcConfig?.get(JdbcUtils.USERNAME_KEY)?.asText(),
            if (jdbcConfig?.has(JdbcUtils.PASSWORD_KEY) == true)
                jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            TeradataConstants.DRIVER_CLASS,
            jdbcConfig?.get(JdbcUtils.JDBC_URL_KEY)?.asText(),
            config?.let { getConnectionProperties(it) },
            Duration.ofSeconds(10),
        )
    }

    @Test
    @Throws(Exception::class)
    override fun interruptedOverwriteWithoutPriorData() {
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

        val expectedRawRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    override fun interruptedTruncateWithPriorData() {
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
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())
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
                                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
                            ),
                            44,
                        )
                    }
                expectedFinalRecords1 + sync2Records
            }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    /**
     * Run the first sync from [.incrementalDedup], but repeat the messages many times. Some
     * destinations behave differently with small vs large record count, so this test case tries to
     * exercise that behavior.
     */
    @ParameterizedTest
    @ValueSource(longs = [0L, 1L])
    @Throws(Exception::class)
    @Timeout(12000)
    override fun largeDedupSync(inputGenerationId: Long) {
        super.largeDedupSync(inputGenerationId)
    }

    @Test
    @Throws(Exception::class)
    override fun identicalNameSimultaneousSync() {
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
        val outFuture1 = destinationOutputFuture(sync1)

        // Write some messages to both syncs. Write data to sync 2 to try and force a
        // flush.
        pushMessages(messages1, sync1)

        pushStatusMessages(catalog1, sync1, AirbyteStreamStatus.COMPLETE)
        endSync(sync1, outFuture1)
        val sync2 = startSync(catalog2)
        val outFuture2 = destinationOutputFuture(sync2)
        // using less numbers here to avoid running out of memory
        val nTimes = 10000
        for (i in 0..nTimes - 1) {
            pushMessages(messages2, sync2)
        }
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

    @Throws(Exception::class)
    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDefaultSchema(config!!)
        }
        if (isSchemaExists(database, streamNamespace)) {
            // Delete drops all everything in database. So no need to drop only given table
            // database!!.execute(java.lang.String.format("DELETE DATABASE %s;", streamNamespace))
            // database!!.execute(java.lang.String.format("DROP DATABASE %s;", streamNamespace))
        }
    }

    private fun isSchemaExists(database: JdbcDatabase?, schemaName: String?): Boolean {
        return (database?.queryInt(
            String.format(
                "SELECT COUNT(1) FROM DBC.Databases WHERE DatabaseName = '%s'",
                schemaName,
            )
        )
            ?: 0) > 0 // If the result is greater than 0, return true, else false
    }

    private fun getConnectionProperties(config: JsonNode): Map<String, String> {
        val customProperties =
            JdbcUtils.parseJdbcParameters(
                config,
                JdbcUtils.JDBC_URL_PARAMS_KEY,
            )
        val defaultProperties = getDefaultConnectionProperties(config)
        return MoreMaps.merge(customProperties, defaultProperties)
    }

    private fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        return dest.getDefaultConnectionProperties(config)
    }

    companion object {
        private val dest: TeradataDestination = TeradataDestination()
        var base: TeradataBaseTest = TeradataBaseTest()
        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        @Timeout(1200)
        fun initEnvironment(): Unit {
            base.init("secrets/typing_config.json")
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

        @JvmStatic
        @AfterAll
        @Throws(
            ExecutionException::class,
            InterruptedException::class,
            Exception::class,
        )
        fun cleanupEnvironment(): Unit {
            base.clean()
        }
    }
}
