/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.motherduck.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
open class MotherDuckSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("MotherDuck Access Token")
    @get:JsonPropertyDescription(
        "Enter your MotherDuck access token. You can find your token at https://app.motherduck.com/ under Settings > Access Tokens."
    )
    @get:JsonProperty("motherduck_api_key")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 0, "airbyte_secret": true}""")
    val motherduckApiKey: String = ""

    @get:JsonSchemaTitle("Database Path")
    @get:JsonPropertyDescription(
        "The path to your MotherDuck database. Use 'md:' to connect to the default database, 'md:<database_name>' for a specific MotherDuck database, or a file path for a local DuckDB file."
    )
    @get:JsonProperty("destination_path")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 1, "examples": ["md:", "md:my_database", "/local/path/to/file.duckdb"]}"""
    )
    val destinationPath: String = "md:"

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        "Enter the name of the default schema. Defaults to 'main' if not specified."
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 2, "examples": ["main", "airbyte_schema"]}"""
    )
    val schema: String = "main"

    @get:JsonSchemaTitle("Airbyte Internal Table Schema Name")
    @get:JsonPropertyDescription(
        """Airbyte will use this schema for various internal tables. Defaults to "airbyte_internal"."""
    )
    @get:JsonProperty("raw_data_schema")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 3}""")
    val internalTableSchema: String? = null
}

@Singleton
class MotherDuckSpecificationExtension : DestinationSpecificationExtension {
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
