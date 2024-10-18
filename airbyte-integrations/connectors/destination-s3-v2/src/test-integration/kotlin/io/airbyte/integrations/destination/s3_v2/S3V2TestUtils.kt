/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.ValidatedJsonUtils
import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
    val JSON_UNCOMPRESSED_CONFIG_PATH = Path.of("secrets/s3_dest_v2_minimal_required_config.json")
    val JSON_GZIP_CONFIG_PATH = Path.of("secrets/s3_dest_v2_jsonl_gzip_config.json")
    fun readConfig(configPath: Path): String = Files.readString(configPath)
    fun parseConfig(config: String): S3V2Specification =
        ValidatedJsonUtils.parseOne(
            S3V2Specification::class.java,
            config,
        )
    fun readParsedConfig(configPath: Path): S3V2Specification =
        parseConfig(readConfig(configPath))
}
