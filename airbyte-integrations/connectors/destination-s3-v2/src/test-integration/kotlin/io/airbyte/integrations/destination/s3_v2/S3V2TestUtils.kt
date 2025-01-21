/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.ValidatedJsonUtils
import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
    const val JSON_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_minimal_required_config.json"
    const val JSON_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_gzip_config.json"
    const val CSV_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_csv_config.json"
    const val CSV_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_csv_gzip_config.json"
    fun getConfig(configPath: String): S3V2Specification =
        ValidatedJsonUtils.parseOne(
            S3V2Specification::class.java,
            Files.readString(Path.of(configPath)),
        )
}
