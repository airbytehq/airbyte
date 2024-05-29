/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.snowflake.*
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import java.nio.file.Path
import java.sql.SQLException
import java.util.*
import javax.sql.DataSource
import kotlin.concurrent.Volatile
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

abstract class AbstractSnowflakeTypingDedupingTest : BaseTypingDedupingTest() {
    private var databaseName: String? = null
    private var database: JdbcDatabase? = null
    // not super happy with this one, but our test classes are not super kotlin-friendly
    private lateinit var dataSource: DataSource

    override val finalMetadataColumnNames: Map<String, String>
        get() = FINAL_METADATA_COLUMN_NAMES

    protected abstract val configPath: String
        get

    override val imageName: String
        get() = "airbyte/destination-snowflake:dev"

    @Throws(SQLException::class)
    override fun generateConfig(): JsonNode? {
        val config = deserialize(readFile(Path.of(configPath)))
        (config as ObjectNode).put("schema", "typing_deduping_default_schema$uniqueSuffix")
        databaseName = config.get(JdbcUtils.DATABASE_KEY).asText()
        dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        database = SnowflakeDatabase.getDatabase(dataSource)
        cleanAirbyteInternalTable(database)
        return config
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = defaultSchema
        }
        val tableName: String = StreamId.concatenateRawTableName(streamNamespace, streamName)
        val schema = rawSchema
        return SnowflakeTestUtils.dumpRawTable(
            database!!, // Explicitly wrap in quotes to prevent snowflake from upcasing
            "\"$schema\".\"$tableName\""
        )
    }

    @Throws(Exception::class)
    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = defaultSchema
        }
        return SnowflakeTestUtils.dumpFinalTable(
            database!!,
            databaseName!!,
            streamNamespace.uppercase(Locale.getDefault()),
            streamName.uppercase(Locale.getDefault())
        )
    }

    @Throws(Exception::class)
    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = defaultSchema
        }
        database!!.execute(
            String.format(
                """
            DROP TABLE IF EXISTS "%s"."%s";
            DROP SCHEMA IF EXISTS "%s" CASCADE
            
            """.trimIndent(),
                rawSchema, // Raw table is still lowercase.
                StreamId.concatenateRawTableName(streamNamespace, streamName),
                streamNamespace.uppercase(Locale.getDefault())
            )
        )
    }

    @Throws(Exception::class)
    override fun globalTeardown() {
        close(dataSource)
    }

    override val sqlGenerator: SqlGenerator
        get() = SnowflakeSqlGenerator(0)

    protected open val rawSchema: String
        /**
         * Subclasses using a config with a nonstandard raw table schema should override this
         * method.
         */
        get() = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE

    /**
     * Run a sync using 3.0.0 (which is the highest version that still creates v2 final tables with
     * lowercased+quoted names). Then run a sync using our current version.
     */
    @Test
    @Throws(Exception::class)
    open fun testFinalTableUppercasingMigration_append() {
        try {
            val catalog =
                ConfiguredAirbyteCatalog()
                    .withStreams(
                        java.util.List.of(
                            ConfiguredAirbyteStream()
                                .withSyncMode(SyncMode.FULL_REFRESH)
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
            runSync(catalog, messages1, "airbyte/destination-snowflake:3.0.0")

            // We no longer have the code to dump a lowercased table, so just move on directly to
            // the new sync

            // Second sync
            val messages2 = readMessages("dat/sync2_messages.jsonl")

            runSync(catalog, messages2)

            val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw_mixed_tzs.jsonl")
            val expectedFinalRecords2 =
                readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
            verifySyncResult(
                expectedRawRecords2,
                expectedFinalRecords2,
                disableFinalTableComparison()
            )
        } finally {
            // manually drop the lowercased schema, since we no longer have the code to do it
            // automatically
            // (the raw table is still in lowercase "airbyte_internal"."whatever", so the
            // auto-cleanup code
            // handles it fine)
            database!!.execute("DROP SCHEMA IF EXISTS \"$streamNamespace\" CASCADE")
        }
    }

    @Test
    @Throws(Exception::class)
    fun testFinalTableUppercasingMigration_overwrite() {
        try {
            val catalog =
                ConfiguredAirbyteCatalog()
                    .withStreams(
                        java.util.List.of(
                            ConfiguredAirbyteStream()
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

            // First sync
            val messages1 = readMessages("dat/sync1_messages.jsonl")
            runSync(catalog, messages1, "airbyte/destination-snowflake:3.0.0")

            // We no longer have the code to dump a lowercased table, so just move on directly to
            // the new sync

            // Second sync
            val messages2 = readMessages("dat/sync2_messages.jsonl")

            runSync(catalog, messages2)

            val expectedRawRecords2 =
                readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl")
            val expectedFinalRecords2 =
                readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
            verifySyncResult(
                expectedRawRecords2,
                expectedFinalRecords2,
                disableFinalTableComparison()
            )
        } finally {
            // manually drop the lowercased schema, since we no longer have the code to do it
            // automatically
            // (the raw table is still in lowercase "airbyte_internal"."whatever", so the
            // auto-cleanup code
            // handles it fine)
            database!!.execute("DROP SCHEMA IF EXISTS \"$streamNamespace\" CASCADE")
        }
    }

    @Test
    @Throws(Exception::class)
    open fun testRemovingPKNonNullIndexes() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
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
        val messages = readMessages("dat/sync_null_pk.jsonl")
        val e =
            Assertions.assertThrows(TestHarnessException::class.java) {
                runSync(catalog, messages, "airbyte/destination-snowflake:3.1.18")
            } // this version introduced non-null PKs to the final tables

        // ideally we would assert on the logged content of the original exception within e, but
        // that is
        // proving to be tricky

        // Second sync
        runSync(catalog, messages) // does not throw with latest version
        Assertions.assertEquals(
            1,
            dumpFinalTableRecords(streamNamespace, streamName).toTypedArray().size
        )
    }

    @Test
    @Throws(Exception::class)
    fun testExtractedAtUtcTimezoneMigration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(java.util.List.of(listOf("id1"), listOf("id2")))
                            .withCursorField(listOf("updated_at"))
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
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.5.11")

        val expectedRawRecords1 =
            readRecords("dat/ltz_extracted_at_sync1_expectedrecords_raw.jsonl")
        val expectedFinalRecords1 =
            readRecords("dat/ltz_extracted_at_sync1_expectedrecords_dedup_final.jsonl")
        verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison())

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw_mixed_tzs.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final_mixed_tzs.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    private val defaultSchema: String
        get() = config!!["schema"].asText()

    companion object {
        @JvmStatic
        val FINAL_METADATA_COLUMN_NAMES: Map<String, String> =
            java.util.Map.of(
                "_airbyte_raw_id",
                "_AIRBYTE_RAW_ID",
                "_airbyte_extracted_at",
                "_AIRBYTE_EXTRACTED_AT",
                "_airbyte_loaded_at",
                "_AIRBYTE_LOADED_AT",
                "_airbyte_data",
                "_AIRBYTE_DATA",
                "_airbyte_meta",
                "_AIRBYTE_META"
            )

        @Volatile private var cleanedAirbyteInternalTable = false

        @Throws(SQLException::class)
        private fun cleanAirbyteInternalTable(database: JdbcDatabase?) {
            if (!cleanedAirbyteInternalTable) {
                synchronized(AbstractSnowflakeTypingDedupingTest::class.java) {
                    if (!cleanedAirbyteInternalTable) {
                        database!!.execute(
                            "DELETE FROM \"airbyte_internal\".\"_airbyte_destination_state\" WHERE \"updated_at\" < current_date() - 7"
                        )
                        cleanedAirbyteInternalTable = true
                    }
                }
            }
        }
    }
}
