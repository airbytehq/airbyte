/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.destination.redshift.RedshiftDestination
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.List
import java.util.Random
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.conf.Settings
import org.jooq.impl.DSL
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class AbstractRedshiftTypingDedupingTest : JdbcTypingDedupingTest() {
    override val imageName: String
        get() = "airbyte/destination-redshift:dev"

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun getDataSource(config: JsonNode?): DataSource? {
        return RedshiftDestination().getDataSource(config!!)
    }

    override val sourceOperations: JdbcCompatibleSourceOperations<*>
        get() = RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations()

    override val sqlGenerator: SqlGenerator
        get() =
            object : RedshiftSqlGenerator(RedshiftSQLNameTransformer(), false) {
                override val dslContext: DSLContext
                    // Override only for tests to print formatted SQL. The actual implementation
                    // should use unformatted
                    get() = DSL.using(dialect, Settings().withRenderFormatted(true))
            }

    @Test
    @Disabled(
        "Redshift connector 2.4.3 and below are rendered useless with " +
            "Redshift cluster version https://docs.aws.amazon.com/redshift/latest/mgmt/cluster-versions.html#cluster-version-181 " +
            "due to metadata calls hanging. We cannot run this test anymore"
    )
    @Throws(Exception::class)
    fun testRawTableMetaMigration_append() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(schema)
                            )
                    )
                )

        // First sync without _airbyte_meta
        val messages1 = readMessages("dat/sync1_messages_before_meta.jsonl")
        runSync(catalog, messages1, "airbyte/destination-redshift:2.1.10")
        // Second sync
        val messages2 = readMessages("dat/sync2_messages_after_meta.jsonl")
        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_mixed_meta_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Disabled(
        "Redshift connector 2.4.3 and below are rendered useless with " +
            "Redshift cluster version https://docs.aws.amazon.com/redshift/latest/mgmt/cluster-versions.html#cluster-version-181 " +
            "due to metadata calls hanging. We cannot run this test anymore"
    )
    @Throws(Exception::class)
    fun testRawTableMetaMigration_incrementalDedupe() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("updated_at"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withPrimaryKey(List.of(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(schema)
                            )
                    )
                )

        // First sync without _airbyte_meta
        val messages1 = readMessages("dat/sync1_messages_before_meta.jsonl")
        runSync(catalog, messages1, "airbyte/destination-redshift:2.1.10")
        // Second sync
        val messages2 = readMessages("dat/sync2_messages_after_meta.jsonl")
        runSync(catalog, messages2)

        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl")
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_incremental_dedup_meta_final.jsonl")
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())
    }

    @Test
    @Throws(Exception::class)
    fun testRawTableLoadWithSuperVarcharLimitation() {
        val record1 =
            """
                           {"type": "RECORD",
                             "record":{
                               "emitted_at": 1000,
                               "data": {
                                 "id1": 1,
                                 "id2": 200,
                                 "updated_at": "2000-01-01T00:00:00Z",
                                 "_ab_cdc_deleted_at": null,
                                 "name": "PLACE_HOLDER",
                                 "address": {"city": "San Francisco", "state": "CA"}}
                             }
                           }
                           
                           """.trimIndent()
        val record2 =
            """
                           {"type": "RECORD",
                             "record":{
                               "emitted_at": 1000,
                               "data": {
                                 "id1": 2,
                                 "id2": 201,
                                 "updated_at": "2000-01-01T00:00:00Z",
                                 "_ab_cdc_deleted_at": null,
                                 "name": "PLACE_HOLDER",
                                 "address": {"city": "New York", "state": "NY"}}
                             }
                           }
                           
                           """.trimIndent()
        val largeString1 =
            generateRandomString(RedshiftSuperLimitationTransformer.REDSHIFT_VARCHAR_MAX_BYTE_SIZE)
        val largeString2 =
            generateRandomString(
                RedshiftSuperLimitationTransformer.REDSHIFT_VARCHAR_MAX_BYTE_SIZE + 2
            )
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    List.of(
                        ConfiguredAirbyteStream()
                            .withSyncId(42)
                            .withGenerationId(43)
                            .withMinimumGenerationId(0)
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(schema)
                            )
                    )
                )
        val message1 = deserialize(record1, AirbyteMessage::class.java)
        message1.record.namespace = streamNamespace
        message1.record.stream = streamName
        (message1.record.data as ObjectNode).put("name", largeString1)
        val message2 = deserialize(record2, AirbyteMessage::class.java)
        message2.record.namespace = streamNamespace
        message2.record.stream = streamName
        (message2.record.data as ObjectNode).put("name", largeString2)

        // message1 should be preserved which is just on limit, message2 should be nulled.
        runSync(catalog, List.of(message1, message2))

        // Add verification.
        val expectedRawRecords = readRecords("dat/sync1_recordnull_expectedrecords_raw.jsonl")
        val expectedFinalRecords = readRecords("dat/sync1_recordnull_expectedrecords_final.jsonl")
        // Only replace for first record, second record should be nulled by transformer.
        (expectedRawRecords[0]["_airbyte_data"] as ObjectNode).put("name", largeString1)
        (expectedFinalRecords[0] as ObjectNode).put("name", largeString1)
        verifySyncResult(expectedRawRecords, expectedFinalRecords, disableFinalTableComparison())
    }

    @Test
    @Throws(Exception::class)
    fun testGenerationIdMigrationForAppend() {
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
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        // First sync
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(
            catalog,
            messages1,
            "airbyte/destination-redshift:3.1.1",
            // Old connector version can't handle TRACE messages; disable the
            // stream status message
            streamStatus = null,
        )

        // Second sync
        val messages2 = readMessages("dat/sync2_messages.jsonl")
        runSync(catalog, messages2)

        // The first 5 records in these files were written by the old version,
        // which does not write _airbyte_generation_id to the raw/final tables,
        // and does not write sync_id to _airbyte_meta.
        // So modify the expected records to reflect those differences.
        val expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl")
        for (i in 0..4) {
            val record = expectedRawRecords2[i] as ObjectNode
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
            (record.get(JavaBaseConstants.COLUMN_NAME_AB_META) as ObjectNode).remove(
                JavaBaseConstants.AIRBYTE_META_SYNC_ID_KEY
            )
        }
        val expectedFinalRecords2 =
            readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl")
        for (i in 0..4) {
            val record = expectedFinalRecords2[i] as ObjectNode
            record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
            (record.get(JavaBaseConstants.COLUMN_NAME_AB_META) as ObjectNode).remove(
                JavaBaseConstants.AIRBYTE_META_SYNC_ID_KEY
            )
        }
        verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison())

        // Verify that we didn't trigger a soft reset.
        // There should be two unique loaded_at values in the raw table.
        // (only do this if T+D is enabled to begin with; otherwise loaded_at will just be null)
        if (!disableFinalTableComparison()) {
            val actualRawRecords2 = dumpRawTableRecords(streamNamespace, streamName)
            val loadedAtValues =
                actualRawRecords2
                    .map { record: JsonNode ->
                        record.get(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)
                    }
                    .toSet()
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
                                    .withJsonSchema(BaseTypingDedupingTest.Companion.SCHEMA),
                            ),
                    ),
                )
        val messages1 = readMessages("dat/sync1_messages.jsonl")
        runSync(
            catalog1,
            messages1,
            "airbyte/destination-redshift:3.1.1",
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
                                    .withJsonSchema(BaseTypingDedupingTest.Companion.SCHEMA),
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

    protected fun generateRandomString(totalLength: Int): String {
        return RANDOM.ints('a'.code, 'z'.code + 1)
            .limit(totalLength.toLong())
            .collect(
                { StringBuilder() },
                { obj: java.lang.StringBuilder, codePoint: Int -> obj.appendCodePoint(codePoint) },
                { obj: java.lang.StringBuilder, s: java.lang.StringBuilder? -> obj.append(s) }
            )
            .toString()
    }

    companion object {
        private val RANDOM = Random()
    }
}
