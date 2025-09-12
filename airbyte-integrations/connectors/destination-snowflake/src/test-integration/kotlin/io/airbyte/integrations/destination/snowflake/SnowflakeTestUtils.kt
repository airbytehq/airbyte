/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import java.nio.file.Files
import java.nio.file.Path

object SnowflakeTestUtils {
    const val INTERNAL_STAGING_CONFIG_DISABLE_TD =
        "secrets/1s1t_disabletd_internal_staging_config.json"
    const val INTERNAL_STAGING_CONFIG_RAW_SCHEMA_OVERRIDE_DISABLE_TD =
        "secrets/1s1t_disabletd_internal_staging_config_raw_schema_override.json"
    const val INTERNAL_STAGING_CREDS = "secrets/1s1t_internal_staging_config.json"
    const val INTERNAL_STAGING_CREDS_RAW_SCHEMA_OVERRIDE =
        "secrets/1s1t_internal_staging_config_raw_schema_override.json"
    const val INSUFFICIENT_PERMISSIONS_CREDS = "secrets/config.json"
    const val QUOTED_IDENTIFIERS_IGNORE_CASE_CREDS = "secrets/1s1t_case_insensitive.json"

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
