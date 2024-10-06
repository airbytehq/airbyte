/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode

class PostgresRawOverrideTypingDedupingTest : PostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig().put("raw_data_schema", "overridden_raw_dataset")
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"
}
