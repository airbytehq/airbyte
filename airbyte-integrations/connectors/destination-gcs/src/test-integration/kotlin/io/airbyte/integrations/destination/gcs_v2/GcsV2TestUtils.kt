/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import java.nio.file.Files
import java.nio.file.Path

/**
 * Mirror of S3V2TestUtils, minus everything AWS-specific. GCS auth is HMAC-only, so there is no
 * assume-role secret to load and no eager init block (which would fail on a missing file and break
 * the config-independent SpecTest). Each secrets JSON file must contain a valid GCS config
 * (gcs_bucket_name, gcs_bucket_path, gcs_bucket_region, credential HMAC, format). File names MUST
 * match the testSecrets entries in metadata.yaml.
 */
object GcsV2TestUtils {
    const val AVRO_SNAPPY_CONFIG_PATH = "secrets/gcs_dest_v2_avro_snappy_config.json"
    const val AVRO_UNCOMPRESSED_CONFIG_PATH = "secrets/gcs_dest_v2_avro_config.json"
    const val JSONL_CONFIG_PATH = "secrets/gcs_dest_v2_jsonl_config.json"
    const val CSV_CONFIG_PATH = "secrets/gcs_dest_v2_csv_config.json"
    const val CSV_UNCOMPRESSED_CONFIG_PATH = "secrets/gcs_dest_v2_csv_uncompressed_config.json"
    const val PARQUET_SNAPPY_CONFIG_PATH = "secrets/gcs_dest_v2_parquet_snappy_config.json"

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
