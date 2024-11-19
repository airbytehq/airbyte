/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import java.nio.file.Files
import java.nio.file.Path

object IcebergV2TestUtil {
    // TODO this is just here as an example, we should remove it + add real configs
    private val resource =
        this::class.java.classLoader.getResource("iceberg_dest_v2_minimal_required_config.json")
            ?: throw IllegalArgumentException("File not found in resources")
    val PATH: Path = Path.of(resource.toURI())

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
