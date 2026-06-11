/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.iceberg.parquet

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Hive (Hive Metastore) catalog support for the Iceberg toolkit.
 *
 * This file is kept separate from the upstream [IcebergCatalogSpecifications] /
 * [IcebergCatalogConfiguration] files to minimize merge conflicts when syncing from
 * airbytehq/airbyte. Because [CatalogType] / [CatalogConfiguration] are `sealed`, these
 * subtypes must live in the same module + package as the sealed declarations, but living
 * in their own file keeps the additive footprint in the upstream files to a few lines
 * (the enum value, the `@JsonSubTypes` entry, and the `when` branch).
 *
 * Mirrors the behaviour of the destination-iceberg (Spark) connector's HiveCatalogConfig:
 * a Hive Metastore thrift URI plus a default database, with table data stored on S3 via
 * Iceberg's S3FileIO.
 */
@JsonSchemaTitle("Hive Catalog")
@JsonSchemaDescription(
    "Configuration details for connecting to a Hive Metastore-based Iceberg catalog."
)
class HiveCatalogSpecification(
    @JsonSchemaTitle("Catalog Type")
    @JsonProperty("catalog_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val catalogType: Type = Type.HIVE,

    /**
     * The Hive Metastore thrift URI, e.g. `thrift://hive-metastore:9083`. Required to connect to
     * the metastore.
     */
    @get:JsonSchemaTitle("Hive Metastore thrift URI")
    @get:JsonPropertyDescription(
        "The Hive Metastore thrift URI used to connect to the Hive catalog. Must start with \"thrift://\"."
    )
    @get:JsonProperty("hive_thrift_uri")
    @JsonSchemaInject(json = """{"examples": ["thrift://host:9083"], "order":1}""")
    val hiveThriftUri: String,

    /**
     * The default database used when building the Table identifier.
     *
     * This database name will only be used if the stream namespace is null, meaning when the
     * `Destination Namespace` setting for the connection is set to `Destination-defined` or
     * `Source-defined`.
     */
    @get:JsonSchemaTitle("Default database")
    @get:JsonPropertyDescription(
        """The Hive database name. This will ONLY be used if the `Destination Namespace` setting for the connection is set to `Destination-defined` or `Source-defined`"""
    )
    @get:JsonProperty("database_name", defaultValue = "default")
    @JsonSchemaInject(json = """{"examples": ["default"], "order":2}""")
    val databaseName: String = "default",
) : CatalogType(catalogType)

/**
 * Hive catalog configuration details.
 *
 * Stores information required to connect to a Hive Metastore.
 */
@JsonSchemaTitle("Hive Catalog Configuration")
@JsonSchemaDescription(
    "Hive Metastore-specific configuration details for connecting an Iceberg catalog."
)
data class HiveCatalogConfiguration(
    @JsonSchemaTitle("Hive Metastore thrift URI")
    @JsonPropertyDescription("The Hive Metastore thrift URI, e.g. thrift://host:9083.")
    val hiveThriftUri: String,
    @get:JsonSchemaTitle("Database Name")
    @get:JsonPropertyDescription(
        """The Hive database name. This will ONLY be used if the `Destination Namespace` setting for the connection is set to `Destination-defined` or `Source-defined`"""
    )
    val databaseName: String,
) : CatalogConfiguration
