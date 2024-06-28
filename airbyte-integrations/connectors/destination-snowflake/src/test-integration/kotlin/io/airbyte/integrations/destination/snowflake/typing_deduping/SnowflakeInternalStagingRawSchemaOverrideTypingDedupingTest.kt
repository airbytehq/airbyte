/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

class SnowflakeInternalStagingRawSchemaOverrideTypingDedupingTest :
    AbstractSnowflakeTypingDedupingTest() {
    override val configPath: String
        get() = "secrets/1s1t_internal_staging_config_raw_schema_override.json"

    override val rawSchema: String
        get() = "overridden_raw_dataset"
}
