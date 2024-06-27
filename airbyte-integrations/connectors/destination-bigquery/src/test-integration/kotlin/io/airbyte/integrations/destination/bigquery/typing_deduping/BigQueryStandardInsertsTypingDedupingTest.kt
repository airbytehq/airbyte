/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import org.junit.jupiter.api.Test

class BigQueryStandardInsertsTypingDedupingTest : AbstractBigQueryTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/credentials-1s1t-standard.json"

    @Test
    override fun incrementalDedupDefaultNamespace() {
        super.incrementalDedupDefaultNamespace()
    }
}
