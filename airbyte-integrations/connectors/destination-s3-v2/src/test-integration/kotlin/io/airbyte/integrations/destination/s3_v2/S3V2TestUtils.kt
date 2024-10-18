/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
    const val JSON_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_minimal_required_config.json"
    const val JSON_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_gzip_config.json"
    fun getConfig(configPath: String) = Files.readString(Path.of(configPath))
}
