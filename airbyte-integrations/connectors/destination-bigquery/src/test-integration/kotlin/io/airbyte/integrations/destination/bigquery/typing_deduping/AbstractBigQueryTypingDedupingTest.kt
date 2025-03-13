/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.BigQueryDestination.Companion.getBigQuery
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getDatasetId
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import java.io.IOException
import java.nio.file.Path
import java.util.function.Function
import java.util.stream.Collectors
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class AbstractBigQueryTypingDedupingTest : BaseTypingDedupingTest() {
    private var bq: BigQuery? = null

    protected abstract val configPath: String
        get

    @Throws(IOException::class)
    public override fun generateConfig(): JsonNode? {
        val datasetId = "typing_deduping_default_dataset$uniqueSuffix"
        val stagingPath = "test_path$uniqueSuffix"
        val config =
            BigQueryDestinationTestUtils.createConfig(Path.of(configPath), datasetId, stagingPath)
        bq = getBigQuery(config!!)
        return config
    }

    override val imageName: String
        get() = "airbyte/destination-bigquery:dev"

    @Throws(InterruptedException::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDatasetId(config!!)
        }
        val result =
            bq!!.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM " +
                        rawDataset +
                        "." +
                        StreamId.concatenateRawTableName(streamNamespace, streamName)
                )
            )
        return BigQuerySqlGeneratorIntegrationTest.Companion.toJsonRecords(result)
    }

    @Throws(InterruptedException::class)
    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDatasetId(config!!)
        }
        val result =
            bq!!.query(QueryJobConfiguration.of("SELECT * FROM $streamNamespace.$streamName"))
        return BigQuerySqlGeneratorIntegrationTest.Companion.toJsonRecords(result)
    }

    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDatasetId(config!!)
        }
        // bq.delete simply returns false if the table/schema doesn't exist (e.g. if the connector
        // failed to
        // create it)
        // so we don't need to do any existence checks here.
        bq!!.delete(
            TableId.of(rawDataset, StreamId.concatenateRawTableName(streamNamespace, streamName))
        )
        bq!!.delete(DatasetId.of(streamNamespace), BigQuery.DatasetDeleteOption.deleteContents())
    }

    override val sqlGenerator: SqlGenerator
        get() = BigQuerySqlGenerator(config!![BigQueryConsts.CONFIG_PROJECT_ID].asText(), null)

    @Test
    @Throws(Exception::class)
    fun testV1V2Migration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of<ConfiguredAirbyteStream>(
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
                                    .withJsonSchema(Companion.SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")

        runSync(
            catalog,
            messages1,
            "airbyte/destination-bigquery:1.10.2",
            { config: JsonNode? ->
                // Defensive to avoid weird behaviors or test failures if the original config is
                // being altered by
                // another thread, thanks jackson for a mutable JsonNode
                val copiedConfig: JsonNode = Jsons.clone<JsonNode>(config!!)
                if (config is ObjectNode) {
                    // Opt out of T+D to run old V1 sync
                    (copiedConfig as ObjectNode).put("use_1s1t_format", false)
                }
                copiedConfig
            }
        )

        // The record differ code is already adapted to V2 columns format, use the post V2 sync
        // to verify that append mode preserved all the raw records and final records.

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")

        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_v1v2_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_v1v2_fullrefresh_append_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Throws(Exception::class)
    open fun testRemovingPKNonNullIndexes() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of<ConfiguredAirbyteStream>(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withPrimaryKey(
                                java.util.List.of<List<String>>(
                                    listOf<String>("id1"),
                                    listOf<String>("id2")
                                )
                            )
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(Companion.SCHEMA)
                            )
                    )
                )

        // First sync
        val messages = readMessages("dat/sync_null_pk.jsonl")
        val e =
            Assertions.assertThrows(TestHarnessException::class.java) {
                runSync(catalog, messages, "airbyte/destination-bigquery:2.0.20")
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
    fun testAirbyteMetaAndGenerationIdMigration() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of<ConfiguredAirbyteStream>(
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
                                    .withJsonSchema(Companion.SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        // We don't want to send a stream status message, because this version of
        // destination-bigquery will
        // crash.
        runSync(
            catalog,
            messages1,
            "airbyte/destination-bigquery:2.4.20",
            Function.identity(),
            null
        )

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
            record.set<JsonNode>(
                JavaBaseConstants.COLUMN_NAME_AB_META,
                deserialize(
                    """
                            {"errors": []}
                            
                            """.trimIndent()
                )
            )
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
        }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())

        // Verify that we didn't trigger a soft reset.
        // There should be two unique loaded_at values in the raw table.
        // (only do this if T+D is enabled to begin with; otherwise loaded_at will just be null)
        if (!disableFinalTableComparison()) {
            val actualRawRecords2 = dumpRawTableRecords(streamNamespace, streamName)
            val loadedAtValues =
                actualRawRecords2
                    .stream()
                    .map<JsonNode>(
                        Function<JsonNode, JsonNode> { record: JsonNode ->
                            record.get(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)
                        }
                    )
                    .collect(Collectors.toSet<JsonNode>())
            Assertions.assertEquals(
                2,
                loadedAtValues.size,
                "Expected two different values for loaded_at. If there is only 1 value, then we incorrectly triggered a soft reset. If there are more than 2, then something weird happened?"
            )
        }
    }

    @Test
    fun testGenerationIdMigrationForOverwrite() {
        // First sync
        val catalog1 =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withSyncId(41L)
                            .withGenerationId(42L)
                            .withMinimumGenerationId(0L)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(
            catalog1,
            messages1,
            "airbyte/destination-bigquery:2.4.20",
            // Old connector version can't handle TRACE messages; disable the
            // stream status message
            streamStatus = null,
        )

        // Second sync
        val catalog2 =
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
                                    .withJsonSchema(SCHEMA),
                            ),
                    ),
                )
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog2, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_overwrite_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    // Disabling until we can safely fetch generation ID
    @Test
    @Disabled
    override fun interruptedOverwriteWithoutPriorData() {
        super.interruptedOverwriteWithoutPriorData()
    }

    protected open val rawDataset: String
        /**
         * Subclasses using a config with a nonstandard raw table dataset should override this
         * method.
         */
        get() = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
}
