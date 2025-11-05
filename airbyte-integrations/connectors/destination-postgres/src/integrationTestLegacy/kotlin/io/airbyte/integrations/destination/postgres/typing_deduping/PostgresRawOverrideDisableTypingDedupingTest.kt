/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class PostgresRawOverrideDisableTypingDedupingTest : PostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig()
            .put("raw_data_schema", "overridden_raw_dataset")
            .put("disable_type_dedupe", true)
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    // when disable_type_dedupe = true, we only output to raw table
    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    override fun disableRawTableComparison(): Boolean {
        return false
    }

    @Disabled @Test override fun identicalNameSimultaneousSync() {}

    @Disabled @Test override fun testVarcharLimitOver64K() {}

    // this test assumes that fields that are not in the schema will show up
    // on the raw table. This is only true for older versions of the connector.
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun testIncrementalSyncDropOneColumn(inputGenerationId: Long) {}

    // disabling dedup tests since dedup not supported when setting `disable_type_dedupe` to true.
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun incrementalDedup(inputGenerationId: Long) {}
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun largeDedupSync(inputGenerationId: Long) {}
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun incrementalDedupDefaultNamespace(inputGenerationId: Long) {}
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun incrementalDedupChangeCursor(inputGenerationId: Long) {}
    @Disabled @ParameterizedTest @ValueSource(longs = []) override fun incrementalDedupIdenticalName() {}
}
