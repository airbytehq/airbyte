/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.command.iceberg.parquet

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

enum class TimeColumnType {
    TIME,
    STRING,
}

interface IcebergTimeSpecification {
    @get:JsonProperty("time_column_type", required = false)
    @get:JsonSchemaTitle("Time Column Type")
    @get:JsonPropertyDescription(
        "Store time columns as TIME (default) or ISO-8601 STRING for Spark/Databricks readers, which do not support Iceberg time. Changing existing TIME columns to STRING requires a full refresh.",
    )
    @get:JsonSchemaInject(json = """{"default":"TIME"}""")
    val timeColumnType: TimeColumnType?
        get() = TimeColumnType.TIME
}
