/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import org.junit.jupiter.api.Disabled

class BigQueryGcsRawOverrideDisableTypingDedupingTest : AbstractBigQueryTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/credentials-1s1t-disabletd-gcs-raw-override.json"

    override val rawDataset: String
        get() = "overridden_raw_dataset"

    override fun disableFinalTableComparison(): Boolean {
        return true
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
