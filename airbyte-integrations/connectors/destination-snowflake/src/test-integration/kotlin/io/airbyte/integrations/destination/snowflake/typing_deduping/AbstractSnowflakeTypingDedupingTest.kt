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
import io.airbyte.commons.json.Jsons
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
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
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
        dataSource =
            SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        database = SnowflakeDatabaseUtils.getDatabase(dataSource)
        cleanAirbyteInternalTable(database)
        return config
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        var namespaceOrDefault = streamNamespace
        if (namespaceOrDefault == null) {
            namespaceOrDefault = defaultSchema
        }
        val tableName: String = StreamId.concatenateRawTableName(namespaceOrDefault, streamName)
        val schema = rawSchema
        return SnowflakeTestUtils.dumpRawTable(
            database!!, // Explicitly wrap in quotes to prevent snowflake from upcasing
            "\"$schema\".\"$tableName\"",
        )
    }

    @Throws(Exception::class)
    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        var namespaceOrDefault = streamNamespace
        if (namespaceOrDefault == null) {
            namespaceOrDefault = defaultSchema
        }
        return SnowflakeTestUtils.dumpFinalTable(
            database!!,
            databaseName!!,
            namespaceOrDefault.uppercase(Locale.getDefault()),
            streamName.uppercase(Locale.getDefault()),
        )
    }

    @Throws(Exception::class)
    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var namespaceOrDefault = streamNamespace
        if (namespaceOrDefault == null) {
            namespaceOrDefault = defaultSchema
        }
        database!!.execute(
            String.format(
                """
            DROP TABLE IF EXISTS "%s"."%s";
            DROP SCHEMA IF EXISTS "%s" CASCADE
            
            """.trimIndent(),
                rawSchema, // Raw table is still lowercase.
                StreamId.concatenateRawTableName(namespaceOrDefault, streamName),
                namespaceOrDefault.uppercase(Locale.getDefault()),
            ),
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages = readMessages("dat/sync_null_pk.jsonl")
        Assertions.assertThrows(TestHarnessException::class.java) {
            runSync(catalog, messages, "airbyte/destination-snowflake:3.1.18")
        } // this version introduced non-null PKs to the final tables

        // ideally we would assert on the logged content of the original exception within e, but
        // that is
        // proving to be tricky

        // Second sync
        // Running with last known version without Meta&GenID columns. Because the V1V2 migrator
        // will no longer
        // trigger changes to add meta or genid. Explicit Meta-GenID columns are added with a
        // another migrator.
        runSync(catalog, messages) // does not throw with latest version
        Assertions.assertEquals(
            1,
            dumpFinalTableRecords(streamNamespace, streamName).toTypedArray().size,
        )
    }

    @Test
    open fun testV1V2Migration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(
            catalog,
            messages1,
            "airbyte/destination-snowflake:2.1.7",
        ) { config: JsonNode? ->
            // Defensive to avoid weird behaviors or test failures if the original config is being
            // altered by
            // another thread, thanks jackson for a mutable JsonNode
            val copiedConfig = Jsons.clone(config!!)
            if (config is ObjectNode) {
                // Opt out of T+D to run old V1 sync
                (copiedConfig as ObjectNode?)!!.put(
                    "use_1s1t_format",
                    false,
                )
            }
            copiedConfig
        }

        // The record differ code is already adapted to V2 columns format, use the post V2 sync
        // to verify that append mode preserved all the raw records and final records.

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 =
            BaseTypingDedupingTest.readRecords("dat/sync2_expectedrecords_v1v2_raw.jsonl")
        val expectedFinalRecords2 =
            BaseTypingDedupingTest.readRecords(
                "dat/sync2_expectedrecords_v1v2_fullrefresh_append_final.jsonl",
            )
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.5.11")

        // The dumpRawTable code already accounts for Meta and GenID columns, so we cannot use it
        // to verify expected records. We will rely on the second sync to verify raw and final
        // tables.

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw_mixed_tzs.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_incremental_dedup_final_mixed_tzs.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    fun testAirbyteMetaAndGenerationIdMigration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(BaseTypingDedupingTest.Companion.SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.9.1")

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog, messages2)

        // The first 5 records in these files were written by the old version, and have
        // several differences with the new records:
        // In raw tables: no _airbyte_meta or _airbyte_generation_id at all
        // In final tables: no generation ID, and airbyte_meta still uses the old `{errors: [...]}`
        // structure
        // So modify the expected records to reflect those differences.
        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        for (i in 0..4) {
            val record = expectedRawRecords2[i] as ObjectNode
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_META)
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
        }
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        for (i in 0..4) {
            val record = expectedFinalRecords2[i] as ObjectNode
            record.set<ObjectNode>(
                JavaBaseConstants.COLUMN_NAME_AB_META.uppercase(),
                deserialize(
                    """
                    {"errors": []}
                    """.trimIndent(),
                ),
            )
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID.uppercase())
        }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())

        // Verify that we didn't trigger a soft reset.
        // There should be two unique loaded_at values in the raw table.
        // (only do this if T+D is enabled to begin with; otherwise loaded_at will just be null)
        if (!disableFinalTableComparison()) {
            val actualRawRecords2 = dumpRawTableRecords(streamNamespace, streamName)
            val loadedAtValues: Set<JsonNode> =
                actualRawRecords2
                    .map { record: JsonNode -> record[JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT] }
                    .toSet()
            assertEquals(
                2,
                loadedAtValues.size,
                "Expected two different values for loaded_at. If there is only 1 value, then we incorrectly triggered a soft reset. If there are more than 2, then something weird happened?",
            )
        }
    }

    @Test
    fun testAirbyteMetaAndGenerationIdMigrationForOverwrite() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(BaseTypingDedupingTest.Companion.SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.9.1")

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_overwrite_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    fun testAirbyteMetaAndGenerationIdMigrationForOverwrite310Broken() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(BaseTypingDedupingTest.Companion.SCHEMA),
                            ),
                    ),
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.9.1")

        // Second sync
        // This throws exception due to a broken migration in connector
        assertThrows(TestHarnessException::class.java) {
            runSync(catalog, messages1, "airbyte/destination-snowflake:3.10.0")
        }

        // Third sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_overwrite_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
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
                "_AIRBYTE_META",
            )

        @Volatile private var cleanedAirbyteInternalTable = false

        @Throws(SQLException::class)
        private fun cleanAirbyteInternalTable(database: JdbcDatabase?) {
            if (!cleanedAirbyteInternalTable) {
                synchronized(AbstractSnowflakeTypingDedupingTest::class.java) {
                    if (!cleanedAirbyteInternalTable) {
                        database!!.execute(
                            "DELETE FROM \"airbyte_internal\".\"_airbyte_destination_state\" WHERE \"updated_at\" < current_date() - 7",
                        )
                        cleanedAirbyteInternalTable = true
                    }
                }
            }
        }
    }
}
