/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import java.nio.file.Files
import java.nio.file.Path

object SnowflakeTestUtils {
    const val CONFIG_WITH_AUTH_STAGING = "secrets/config_with_auth_staging.json"
    const val CONFIG_WITH_AUTH_STAGING_AND_RAW_OVERRIDE =
        "secrets/config_with_auth_staging_and_raw_override.json"

    fun getConfig(configPath: String): String = Files.readString(getConfigPath(configPath))
    fun getConfigPath(configPath: String): Path = Path.of(configPath)
}
