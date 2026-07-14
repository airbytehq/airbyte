/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.integrations.destination.gcs_v2.GcsV2TestUtils.BASE_CONFIG_PATH
import io.airbyte.integrations.destination.gcs_v2.GcsV2TestUtils.getConfigWithFormat
import java.nio.file.Files
import java.nio.file.Path

/**
 * Test utilities for destination-gcs v2 integration tests.
 *
 * Uses a single base config file (`secrets/config.json`) containing GCS credentials (bucket name,
 * bucket path, bucket region, HMAC key) and injects the `format` section in-memory per test. This
 * eliminates the need for per-format secret files — only one GSM secret is required in CI.
 *
 * The base config intentionally omits the `format` field; each test calls [getConfigWithFormat]
 * with one of the format constants below.
 */
object GcsV2TestUtils {
    private val mapper = ObjectMapper()

    /** Path to the single base config with GCS credentials (no format field). */
    const val BASE_CONFIG_PATH = "secrets/config.json"

    // -- Format JSON templates --------------------------------------------------
    // Each constant is a valid JSON string for the `format` field of the GCS v2 spec.

    /** Avro with Snappy internal codec. */
    const val AVRO_SNAPPY_FORMAT =
        """{"format_type":"Avro","compression_codec":{"codec":"snappy"}}"""

    /** Avro with no compression. */
    const val AVRO_UNCOMPRESSED_FORMAT =
        """{"format_type":"Avro","compression_codec":{"codec":"no compression"}}"""

    /** JSONL with the CDK default compression (GZIP) -> `.jsonl.gz`. */
    const val JSONL_FORMAT = """{"format_type":"JSONL"}"""

    /** JSONL with explicit "No Compression" -> `.jsonl`. */
    const val JSONL_UNCOMPRESSED_FORMAT =
        """{"format_type":"JSONL","compression":{"compression_type":"No Compression"}}"""

    /** CSV with the CDK default compression (GZIP) -> `.csv.gz`. */
    const val CSV_FORMAT = """{"format_type":"CSV","flattening":"No flattening"}"""

    /** CSV with explicit "No Compression" -> `.csv`. */
    const val CSV_UNCOMPRESSED_FORMAT =
        """{"format_type":"CSV","flattening":"No flattening","compression":{"compression_type":"No Compression"}}"""

    /** Parquet with Snappy internal codec -> `.parquet`. */
    const val PARQUET_SNAPPY_FORMAT = """{"format_type":"Parquet","compression_codec":"SNAPPY"}"""

    /** Reads a file as a UTF-8 string. */
    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))

    /**
     * Reads the base config from [BASE_CONFIG_PATH] and injects the given [formatJson] as the
     * `format` field. Returns the complete config as a JSON string.
     */
    fun getConfigWithFormat(formatJson: String): String {
        val config = mapper.readTree(getConfig(BASE_CONFIG_PATH)) as ObjectNode
        config.set<JsonNode>("format", mapper.readTree(formatJson))
        return mapper.writeValueAsString(config)
    }
}
