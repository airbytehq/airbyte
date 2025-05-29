/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

class SnowflakeInternalStagingDisableTypingDedupingTest : AbstractSnowflakeTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/1s1t_disabletd_internal_staging_config.json"

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Throws(Exception::class)
    override fun testRemovingPKNonNullIndexes() {
        // Do nothing.
    }

    @Throws(Exception::class)
    override fun identicalNameSimultaneousSync() {
        // TODO: create fixtures to verify how raw tables are affected. Base tests check for final
        // tables.
    }
}
