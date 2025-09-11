/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import java.nio.file.Files
import java.nio.file.Path

object SnowflakeTestUtils {
    const val KEYPAIR_AUTH_CONFIG_PATH = "secrets/snowflake_keypair_auth.json"
    const val USERNAME_AUTH_CONFIG_PATH = "secrets/snowflake_username_auth.json"

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
