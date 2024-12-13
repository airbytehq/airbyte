/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import java.net.URI
import java.nio.file.Path

object IcebergV2TestUtil {
    // TODO this is just here as an example, we should remove it + add real configs
    val MINIMAL_CONFIG_PATH: Path = Path.of(getResourceUri("iceberg_dest_v2_minimal_required_config.json"))
    val GLUE_CONFIG_PATH: Path = Path.of("secrets/glue.json")

    private fun getResourceUri(path: String): URI =
        this::class.java.classLoader.getResource(path)?.toURI()
            ?: throw IllegalArgumentException("File not found in resources")
}
