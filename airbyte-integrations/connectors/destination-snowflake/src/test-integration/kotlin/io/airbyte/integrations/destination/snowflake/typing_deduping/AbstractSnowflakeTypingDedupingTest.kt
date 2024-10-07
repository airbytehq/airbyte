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
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.sql.SQLException
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.*
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import javax.sql.DataSource
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

abstract class AbstractSnowflakeTypingDedupingTest(
    private val forceUppercaseIdentifiers: Boolean = false,
) : BaseTypingDedupingTest() {
    private lateinit var databaseName: String
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
                // Raw table is still lowercase by default
                if (forceUppercaseIdentifiers) {
                    rawSchema.uppercase()
                } else {
                    rawSchema
                },
                StreamId.concatenateRawTableName(namespaceOrDefault, streamName).let {
                    if (forceUppercaseIdentifiers) it.uppercase() else it
                },
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
                            .withGenerationId(0)
                            .withMinimumGenerationId(0)
                            .withSyncId(0)
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
            { config: JsonNode? ->
                // Defensive to avoid weird behaviors or test failures if the original config is
                // being altered by another thread, thanks jackson for a mutable JsonNode
                val copiedConfig = Jsons.clone(config!!)
                if (config is ObjectNode) {
                    // Opt out of T+D to run old V1 sync
                    (copiedConfig as ObjectNode?)!!.put(
                        "use_1s1t_format",
                        false,
                    )
                }
                copiedConfig
            },
            streamStatus = null
        )

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
    open fun testExtractedAtUtcTimezoneMigration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withGenerationId(0)
                            .withSyncId(0)
                            .withMinimumGenerationId(0)
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
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.5.11", streamStatus = null)

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
    open fun testAirbyteMetaAndGenerationIdMigration() {
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
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.9.1", streamStatus = null)

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
    open fun testAirbyteMetaAndGenerationIdMigrationForOverwrite() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(43L)
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
        runSync(catalog, messages1, "airbyte/destination-snowflake:3.9.1", streamStatus = null)

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_overwrite_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Throws(Exception::class)
    open fun testLargeRecord() {
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

        val messagesFromFile = readMessages("dat/sync1_messages.jsonl")
        val largeValue1 = RandomStringUtils.randomAlphanumeric(8 * 1024 * 1024 + 100)
        val largeValue2 = RandomStringUtils.randomAlphanumeric(8 * 1024 * 1024 + 200)
        // only the address field should be cleared on 1st record
        (messagesFromFile[0].record.data as ObjectNode).put("name", largeValue1)
        (messagesFromFile[0].record.data.get("address") as ObjectNode).put("city", largeValue2)

        // only the name field should be cleared on 1st record
        (messagesFromFile[1].record.data as ObjectNode).put("name", largeValue2)
        (messagesFromFile[1].record.data.get("address") as ObjectNode).put("city", largeValue1)

        runSync(catalog1, listOf(messagesFromFile[0], messagesFromFile[1]))

        val rawTableRecords = dumpRawTableRecords(streamNamespace, streamName)
        assertEquals(rawTableRecords.size, 2)
        for (rawTableRecord in rawTableRecords) {
            val rawTableRecordUpdatedAt = rawTableRecord.get("_airbyte_data").get("updated_at")
            val rawTableAddressFieldValue = rawTableRecord.get("_airbyte_data").get("address")
            val rawTableNameFieldValue = rawTableRecord.get("_airbyte_data").get("name")
            val changesFieldValue = rawTableRecord.get("_airbyte_meta").get("changes").get(0)
            if (rawTableRecordUpdatedAt == messagesFromFile[0].record.data.get("updated_at")) {
                val originalNameFieldValue = messagesFromFile[0].record.data.get("name")
                assert(rawTableAddressFieldValue == null) {
                    "\"address\" field should be null. " +
                        "Instead was ${rawTableAddressFieldValue?.toString()?.length} chars long"
                }
                assertEquals(
                    originalNameFieldValue,
                    rawTableNameFieldValue,
                    "\"name\" field should have contained ${originalNameFieldValue?.toString()?.length} chars. " +
                        "Instead was ${rawTableNameFieldValue?.toString()?.length} chars long"
                )
                assertEquals("address", changesFieldValue.get("field").asText())
            } else if (
                rawTableRecordUpdatedAt == messagesFromFile[1].record.data.get("updated_at")
            ) {
                val originalAddressFieldValue = messagesFromFile[1].record.data.get("address")
                assertEquals(
                    originalAddressFieldValue,
                    rawTableAddressFieldValue,
                    "\"address\" field should have contained ${originalAddressFieldValue?.toString()?.length} chars. " +
                        "Instead was ${rawTableAddressFieldValue?.toString()?.length} chars long"
                )
                assert(rawTableNameFieldValue == null) {
                    "\"name\" field should be null. " +
                        "Instead was ${rawTableNameFieldValue?.toString()?.length} chars long"
                }
                assertEquals("name", changesFieldValue.get("field").asText())
            } else {
                throw RuntimeException("unexpected raw record $rawTableRecord")
            }
            assertEquals(
                changesFieldValue.get("change").asText(),
                AirbyteRecordMessageMetaChange.Change.NULLED.value()
            )
            assertEquals(
                changesFieldValue.get("reason").asText(),
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION.value()
            )
        }
    }

    // Disabling until we can safely fetch generation ID
    @Test
    @Disabled
    override fun interruptedOverwriteWithoutPriorData() {
        super.interruptedOverwriteWithoutPriorData()
    }

    private val defaultSchema: String
        get() = config!!["schema"].asText()

    companion object {
        const val _8mb = 8 * 1_241_24
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
                "_airbyte_generation_id",
                "_AIRBYTE_GENERATION_ID",
            )

        private val cleanedAirbyteInternalTable = AtomicBoolean(false)
        private val threadId = AtomicInteger(0)

        @Throws(SQLException::class)
        private fun cleanAirbyteInternalTable(database: JdbcDatabase?) {
            if (
                database!!
                    .queryJsons("SHOW PARAMETERS LIKE 'QUOTED_IDENTIFIERS_IGNORE_CASE';")
                    .first()
                    .get("value")
                    .asText()
                    .toBoolean()
            ) {
                return
            }

            if (!cleanedAirbyteInternalTable.getAndSet(true)) {
                val cleanupCutoffHours = 6
                LOGGER.info { "tableCleaner running" }
                val executor =
                    Executors.newSingleThreadExecutor {
                        val thread = Executors.defaultThreadFactory().newThread(it)
                        thread.name =
                            "airbyteInternalTableCleanupThread-${threadId.incrementAndGet()}"
                        thread.isDaemon = true
                        thread
                    }
                executor.execute {
                    database.execute(
                        "DELETE FROM \"airbyte_internal\".\"_airbyte_destination_state\" WHERE \"updated_at\" < timestampadd('hours', -$cleanupCutoffHours, current_timestamp())",
                    )
                }
                executor.execute {
                    database.execute(
                        "DELETE FROM \"AIRBYTE_INTERNAL\".\"_AIRBYTE_DESTINATION_STATE\" WHERE \"UPDATED_AT\" < timestampadd('hours', -$cleanupCutoffHours, current_timestamp())",
                    )
                }
                executor.execute {
                    val schemaList =
                        database.queryJsons(
                            "SHOW SCHEMAS IN DATABASE INTEGRATION_TEST_DESTINATION;",
                        )
                    LOGGER.info(
                        "tableCleaner found ${schemaList.size} schemas in database INTEGRATION_TEST_DESTINATION"
                    )
                    schemaList
                        .associate {
                            it.get("name").asText() to Instant.parse(it.get("created_on").asText())
                        }
                        .filter {
                            it.value.isBefore(
                                Instant.now().minus(cleanupCutoffHours.toLong(), ChronoUnit.HOURS)
                            )
                        }
                        .filter {
                            it.key.startsWith("SQL_GENERATOR", ignoreCase = true) ||
                                it.key.startsWith("TDTEST", ignoreCase = true) ||
                                it.key.startsWith("TYPING_DEDUPING", ignoreCase = true)
                        }
                        .forEach {
                            executor.execute {
                                database.execute(
                                    "DROP SCHEMA INTEGRATION_TEST_DESTINATION.\"${it.key}\" /* created at ${it.value} */;"
                                )
                            }
                        }
                }
                for (schemaName in
                    listOf("AIRBYTE_INTERNAL", "airbyte_internal", "overridden_raw_dataset")) {
                    executor.execute {
                        val sql =
                            "SHOW TABLES IN schema INTEGRATION_TEST_DESTINATION.\"$schemaName\";"
                        val tableList = database.queryJsons(sql)
                        LOGGER.info {
                            "tableCleaner found ${tableList.size} tables in schema $schemaName"
                        }
                        tableList
                            .associate {
                                it.get("name").asText() to
                                    Instant.parse(it.get("created_on").asText())
                            }
                            .filter {
                                it.value.isBefore(Instant.now().minus(6, ChronoUnit.HOURS)) &&
                                    it.key.startsWith("TDTEST", ignoreCase = true)
                            }
                            .forEach {
                                executor.execute {
                                    database.execute(
                                        "DROP TABLE INTEGRATION_TEST_DESTINATION.\"$schemaName\".\"${it.key}\" /* created at ${it.value} */;"
                                    )
                                }
                            }
                    }
                }
            }
        }
    }
}
