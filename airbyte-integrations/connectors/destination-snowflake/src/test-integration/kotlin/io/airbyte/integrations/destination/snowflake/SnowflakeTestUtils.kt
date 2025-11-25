/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import java.nio.file.Files
import java.nio.file.Path

object SnowflakeTestUtils {
    const val CONFIG_WITH_AUTH_STAGING = "secrets/config_with_auth_staging.json"

    /**
     * This config uses user `INTEGRATION_TEST_USER_DESTINATION_QUOTED_IDENTIFIERS_IGNORE_CASE`,
     * which has QUOTED_IDENTIFIERS_IGNORE_CASE=true.
     *
     * This parameter causes Snowflake to upcase all identifiers, regardless of quoting. We've seen
     * this parameter cause problems in the past (e.g. a simple `select count(*) as "total"` will
     * return a ResultSet with `TOTAL` as the column name rather than `total`), so run all our tests
     * against this config.
     */
    const val CONFIG_WITH_AUTH_STAGING_IGNORE_CASING = "secrets/1s1t_case_insensitive.json"
    const val CONFIG_WITH_AUTH_STAGING_AND_RAW_OVERRIDE =
        "secrets/config_with_auth_staging_and_raw_override.json"

    fun getConfig(configPath: String): String = Files.readString(getConfigPath(configPath))
    fun getConfigPath(configPath: String): Path = Path.of(configPath)
}
