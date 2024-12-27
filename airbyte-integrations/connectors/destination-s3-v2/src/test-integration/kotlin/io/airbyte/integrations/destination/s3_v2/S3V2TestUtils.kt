/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
    const val JSON_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_minimal_required_config.json"
    const val JSON_ROOT_LEVEL_FLATTENING_CONFIG_PATH =
        "secrets/s3_dest_v2_jsonl_root_level_flattening_config.json"
    const val JSON_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_gzip_config.json"
    const val JSON_STAGING_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_staging_config.json"
    const val CSV_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_csv_config.json"
    const val CSV_ROOT_LEVEL_FLATTENING_CONFIG_PATH =
        "secrets/s3_dest_v2_csv_root_level_flattening_config.json"
    const val CSV_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_csv_gzip_config.json"
    const val AVRO_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_avro_config.json"
    const val AVRO_BZIP2_CONFIG_PATH = "secrets/s3_dest_v2_avro_bzip2_config.json"
    const val PARQUET_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_parquet_config.json"
    const val PARQUET_SNAPPY_CONFIG_PATH = "secrets/s3_dest_v2_parquet_snappy_config.json"
    const val ENDPOINT_URL_CONFIG_PATH = "secrets/s3_dest_v2_endpoint_url_config.json"
    const val ENDPOINT_EMPTY_URL_CONFIG_PATH = "secrets/s3_dest_v2_endpoint_empty_url_config.json"
    const val AMBIGUOUS_FILEPATH_CONFIG_PATH = "secrets/s3_dest_v2_ambiguous_filepath_config.json"
    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))
}
