/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Doris Destination Specification")
class DorisSpecification : ConfigurationSpecification() {

    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("Hostname or IP address of the Doris FE node.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"order": 0, "group": "connection"}""")
    val host: String = ""

    @get:JsonSchemaTitle("HTTP Port")
    @get:JsonPropertyDescription(
        "HTTP port of the Doris FE node for Stream Load data ingestion. Default: 8030."
    )
    @get:JsonProperty("http_port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": 8030, "group": "connection"}""")
    val httpPort: Int = 8030

    @get:JsonSchemaTitle("Query Port")
    @get:JsonPropertyDescription(
        "MySQL protocol port of the Doris FE node for DDL operations. Default: 9030."
    )
    @get:JsonProperty("query_port")
    @get:JsonSchemaInject(json = """{"order": 2, "default": 9030, "group": "connection"}""")
    val queryPort: Int = 9030

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the Doris database to write data into.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 3, "group": "connection"}""")
    val database: String = ""

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username for the Doris database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 4, "default": "root", "group": "connection"}""")
    val username: String = "root"

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password for the Doris database.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(
        json = """{"order": 5, "airbyte_secret": true, "default": "", "group": "connection"}"""
    )
    val password: String = ""

    @get:JsonSchemaTitle("Batch Max Rows")
    @get:JsonPropertyDescription(
        "Maximum number of records per batch before flushing to Doris. Default: 100000."
    )
    @get:JsonProperty("batch_max_rows")
    @get:JsonSchemaInject(json = """{"order": 6, "default": 100000, "group": "advanced"}""")
    val batchMaxRows: Long? = 100_000L

    @get:JsonSchemaTitle("Batch Max Bytes")
    @get:JsonPropertyDescription(
        "Maximum size in bytes per batch before flushing to Doris. Default: 50MB (52428800)."
    )
    @get:JsonProperty("batch_max_bytes")
    @get:JsonSchemaInject(json = """{"order": 7, "default": 52428800, "group": "advanced"}""")
    val batchMaxBytes: Long? = 50_000_000L

    @get:JsonSchemaTitle("Batch Flush Interval (ms)")
    @get:JsonPropertyDescription(
        "Maximum time in milliseconds to wait before flushing a batch. Default: 10000."
    )
    @get:JsonProperty("batch_flush_interval_ms")
    @get:JsonSchemaInject(json = """{"order": 8, "default": 10000, "group": "advanced"}""")
    val batchFlushIntervalMs: Long? = 10_000L

    @get:JsonSchemaTitle("Flush Queue Size")
    @get:JsonPropertyDescription(
        "Maximum number of buffered batches before applying backpressure. Default: 5."
    )
    @get:JsonProperty("flush_queue_size")
    @get:JsonSchemaInject(json = """{"order": 9, "default": 5, "group": "advanced"}""")
    val flushQueueSize: Int? = 5

    @get:JsonSchemaTitle("Enable Gzip Compression")
    @get:JsonPropertyDescription(
        "Whether to compress data with gzip before sending to Doris via Stream Load."
    )
    @get:JsonProperty("enable_gzip")
    @get:JsonSchemaInject(json = """{"order": 10, "default": false, "group": "advanced"}""")
    val enableGzip: Boolean? = false
}

@Singleton
class DorisSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
