/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.iceberg.parquet

import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider

/**
 * Represents a unified Iceberg catalog configuration.
 *
 * This class encapsulates the warehouse location, main branch, and a generic catalog configuration
 * (e.g., Nessie or Glue), providing a standardized way to work with various catalog backends.
 */
@JsonSchemaTitle("Iceberg Catalog Configuration")
@JsonSchemaDescription(
    "A unified configuration object for an Iceberg catalog, including warehouse location, main branch name, and backend-specific settings."
)
data class IcebergCatalogConfiguration(
    @JsonSchemaTitle("Warehouse Location")
    @JsonPropertyDescription("The root location of the data warehouse used by the Iceberg catalog.")
    val warehouseLocation: String,
    @JsonSchemaTitle("Main Branch Name")
    @JsonPropertyDescription("The primary or default branch name in the catalog repository.")
    val mainBranchName: String,
    @JsonSchemaTitle("Catalog Configuration")
    @JsonPropertyDescription(
        "The specific configuration details of the chosen Iceberg catalog type."
    )
    val catalogConfiguration: CatalogConfiguration
)

/**
 * A marker interface for catalog configuration details.
 *
 * Implementations of this interface contain the specific information needed to connect to a
 * particular type of catalog backend.
 */
sealed interface CatalogConfiguration

/**
 * Glue catalog configuration details.
 *
 * Stores information required to connect to an AWS Glue catalog.
 */
@JsonSchemaTitle("Glue Catalog Configuration")
@JsonSchemaDescription("AWS Glue-specific configuration details for connecting an Iceberg catalog.")
data class GlueCatalogConfiguration(
    @JsonSchemaTitle("AWS Account ID")
    @JsonPropertyDescription("The AWS Account ID associated with the Glue service.")
    val glueId: String,
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration,
    @get:JsonSchemaTitle("Database Name")
    @get:JsonPropertyDescription(
        """The Glue database name. This will ONLY be used if the `Destination Namespace` setting for the connection is set to `Destination-defined` or `Source-defined`"""
    )
    val databaseName: String
) : CatalogConfiguration, AWSArnRoleConfigurationProvider

/**
 * Nessie catalog configuration details.
 *
 * Stores information required to connect to a Nessie server.
 */
@JsonSchemaTitle("Nessie Catalog Configuration")
@JsonSchemaDescription("Nessie-specific configuration details for connecting an Iceberg catalog.")
data class NessieCatalogConfiguration(
    @JsonSchemaTitle("Nessie Server URI")
    @JsonPropertyDescription("The base URL of the Nessie server.")
    val serverUri: String,
    @JsonSchemaTitle("Nessie Access Token")
    @JsonPropertyDescription("An optional token for authentication with the Nessie server.")
    val accessToken: String?,
    @get:JsonSchemaTitle("Namespace")
    @get:JsonPropertyDescription(
        """The Nessie namespace to be used in the Table identifier. 
           This will ONLY be used if the `Destination Namespace` setting for the connection is set to
           `Destination-defined` or `Source-defined`"""
    )
    val namespace: String
) : CatalogConfiguration

/**
 * Rest catalog configuration details.
 *
 * Stores information required to connect to a Rest server.
 */
@JsonSchemaTitle("Rest Catalog Configuration")
@JsonSchemaDescription("Rest-specific configuration details for connecting an Iceberg catalog.")
data class RestCatalogConfiguration(
    @JsonSchemaTitle("Rest Server URI")
    @JsonPropertyDescription("The base URL of the Rest server.")
    val serverUri: String,
    @get:JsonSchemaTitle("Namespace")
    @get:JsonPropertyDescription(
        """The namespace to be used in the Table identifier. 
           This will ONLY be used if the `Destination Namespace` setting for the connection is set to
           `Destination-defined` or `Source-defined`"""
    )
    val namespace: String
) : CatalogConfiguration

/**
 * Provides a way to retrieve the unified Iceberg catalog configuration.
 *
 * Classes implementing this interface should supply the IcebergCatalogConfiguration instance
 * representing the fully resolved configuration for the Iceberg catalog.
 */
interface IcebergCatalogConfigurationProvider {
    val icebergCatalogConfiguration: IcebergCatalogConfiguration
}
