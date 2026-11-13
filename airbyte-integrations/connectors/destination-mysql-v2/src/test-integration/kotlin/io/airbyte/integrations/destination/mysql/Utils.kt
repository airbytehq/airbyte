/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import java.nio.file.Path

object Utils {
    fun getConfigPath(configFilename: String): Path {
        return Path.of("src/test-integration/resources/$configFilename")
    }
}
