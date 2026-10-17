/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import java.nio.file.Files
import java.nio.file.Path

object DevNull2TestUtils {
    val configPath: Path = Path.of("test_configs/config.json")
    fun configContents(): String = Files.readString(configPath, Charsets.UTF_8)
}
