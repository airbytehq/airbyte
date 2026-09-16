/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.integrations.destination.gcs_v2.GcsV2TestUtils.getConfigWithFormat
import java.nio.file.Files
import java.nio.file.Path

/**
 * Test utilities: reads `secrets/config.json` (GCS credentials without format) and injects a format
 * section in-memory per test via [getConfigWithFormat].
 */
object GcsV2TestUtils {
    private val mapper = ObjectMapper()

    const val BASE_CONFIG_PATH = "secrets/config.json"

    // Format JSON templates for the `format` spec field.

    const val AVRO_SNAPPY_FORMAT =
        """{"format_type":"Avro","compression_codec":{"codec":"snappy"}}"""

    const val AVRO_UNCOMPRESSED_FORMAT =
        """{"format_type":"Avro","compression_codec":{"codec":"no compression"}}"""

    const val JSONL_FORMAT = """{"format_type":"JSONL"}"""

    const val JSONL_UNCOMPRESSED_FORMAT =
        """{"format_type":"JSONL","compression":{"compression_type":"No Compression"}}"""

    const val CSV_FORMAT = """{"format_type":"CSV","flattening":"No flattening"}"""

    const val CSV_UNCOMPRESSED_FORMAT =
        """{"format_type":"CSV","flattening":"No flattening","compression":{"compression_type":"No Compression"}}"""

    const val PARQUET_SNAPPY_FORMAT = """{"format_type":"Parquet","compression_codec":"SNAPPY"}"""

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))

    /** Reads the base config and injects [formatJson] as the `format` field. */
    fun getConfigWithFormat(formatJson: String): String {
        val config = mapper.readTree(getConfig(BASE_CONFIG_PATH)) as ObjectNode
        config.set<JsonNode>("format", mapper.readTree(formatJson))
        return mapper.writeValueAsString(config)
    }
}
