/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest
import io.airbyte.commons.json.Jsons.deserialize
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
