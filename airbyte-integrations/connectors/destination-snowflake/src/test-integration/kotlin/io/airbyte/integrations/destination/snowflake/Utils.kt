/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import java.nio.file.Path

object Utils {
    fun getConfigPath(resourceName: String): Path {
        return Path.of(resourceName)
    }
}
