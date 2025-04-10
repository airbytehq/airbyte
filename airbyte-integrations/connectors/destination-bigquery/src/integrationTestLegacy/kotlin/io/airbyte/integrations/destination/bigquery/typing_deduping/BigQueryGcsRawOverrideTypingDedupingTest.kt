/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

class BigQueryGcsRawOverrideTypingDedupingTest : AbstractBigQueryTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/credentials-1s1t-gcs-raw-override.json"

    override val rawDataset: String
        get() = "overridden_raw_dataset"
}
