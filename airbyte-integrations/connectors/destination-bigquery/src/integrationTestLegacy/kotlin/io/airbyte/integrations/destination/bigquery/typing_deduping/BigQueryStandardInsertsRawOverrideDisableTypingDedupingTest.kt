/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class BigQueryStandardInsertsRawOverrideDisableTypingDedupingTest :
    AbstractBigQueryTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/credentials-1s1t-disabletd-standard-raw-override.json"

    override val rawDataset: String
        get() = "overridden_raw_dataset"

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Test
    @Throws(Exception::class)
    fun arst() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withSyncId(42L)
                            .withGenerationId(43L)
                            .withMinimumGenerationId(0L)
                            .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                            .withStream(
                                AirbyteStream()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName)
                                    .withJsonSchema(SCHEMA)
                            )
                    )
                )

        val messages = readMessages("dat/sync1_messages.jsonl")
        runSync(catalog, messages)
        println()
    }

    @Disabled
    @Throws(Exception::class)
    override fun testRemovingPKNonNullIndexes() {
        // Do nothing.
    }

    @Disabled
    @Throws(Exception::class)
    override fun identicalNameSimultaneousSync() {
        // TODO: create fixtures to verify how raw tables are affected. Base tests check for final
        // tables.
    }
}
