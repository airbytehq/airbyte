/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import kotlin.longArrayOf
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class PostgresRawOverrideTypingDedupingTest : PostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig().put("raw_data_schema", "overridden_raw_dataset")
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    override fun disableRawTableComparison(): Boolean {
        return true
    }

    //syncs used to fail when doing this, not anymore
    @Disabled @Test override fun interruptedTruncateWithPriorData() {}

    // this tests that the fully qualified raw table name is lowercased. This is actually not a restriction anymore, so disabling the test.
    @Disabled @Test override fun testMixedCasedSchema() {}

    // fields that are not in the schema are now dropped.
    @Disabled @ParameterizedTest @ValueSource(longs = [0L, 42L]) override fun testIncrementalSyncDropOneColumn(inputGenerationId: Long) {}

    //migrations not supported on most recent version
    @Disabled @Test override fun testMixedCaseRawTableV1V2Migration() {}
    @Disabled @Test override fun testAirbyteMetaAndGenerationIdMigration() {}
    @Disabled @Test override fun testRawTableMetaMigration_append() {}
    @Disabled @Test override fun testRawTableMetaMigration_incrementalDedupe() {}
    @Disabled @Test override fun testAirbyteMetaAndGenerationIdMigrationForOverwrite() {}
}
