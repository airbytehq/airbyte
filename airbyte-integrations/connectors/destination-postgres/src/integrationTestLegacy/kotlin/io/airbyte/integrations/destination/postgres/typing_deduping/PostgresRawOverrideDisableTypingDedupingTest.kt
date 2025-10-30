/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import kotlin.collections.forEach
import kotlin.longArrayOf
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

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Disabled @Test override fun identicalNameSimultaneousSync() {}

    @Disabled @Test override fun testVarcharLimitOver64K() {}

    @Disabled @Test override fun interruptedTruncateWithPriorData() {}

//    @Disabled @ParameterizedTest @ValueSource(longs = [0L, 42L]) override fun testIncrementalSyncDropOneColumn(inputGenerationId: Long) {}
}
