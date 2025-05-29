/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

class BigQueryGcsTypingDedupingTest : AbstractBigQueryTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/credentials-1s1t-gcs.json"
}
