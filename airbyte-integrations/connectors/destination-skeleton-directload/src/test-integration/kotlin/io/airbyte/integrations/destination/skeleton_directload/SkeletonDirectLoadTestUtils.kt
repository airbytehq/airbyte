/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload

import java.nio.file.Files
import java.nio.file.Path

object SkeletonDirectLoadTestUtils {
    val mainConfigPath: Path = Path.of("test_configs/main.json")
    fun configContents(configPath: Path): String = Files.readString(configPath, Charsets.UTF_8)
}
