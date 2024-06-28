/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class PostgresRawOverrideDisableTypingDedupingTest : PostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig()
            .put("raw_data_schema", "overridden_raw_dataset")
            .put("disable_type_dedupe", true)
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Disabled @Test override fun identicalNameSimultaneousSync() {}

    @Disabled @Test override fun testVarcharLimitOver64K() {}
}
