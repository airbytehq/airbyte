/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg_v2

import java.nio.file.Files
import java.nio.file.Path

object IcebergV2TestUtil {
    // TODO this is just here as an example, we should remove it + add real configs
    const val SOME_RANDOM_S3_CONFIG = "secrets/s3_dest_v2_minimal_required_config.json"
    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
