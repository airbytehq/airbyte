/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.iceberg.parquet

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Interface defining the specifications for configuring an Iceberg catalog.
 *
 * This includes general warehouse information as well as details about the primary branch and the
 * specific type of catalog (e.g., Nessie or Glue). Implementations of this interface should provide
 * the necessary configuration to connect to and use an Iceberg catalog in different environments.
 */
@JsonSchemaTitle("Iceberg Catalog Specifications")
@JsonSchemaDescription(
    "Defines the configurations required to connect to an Iceberg catalog, including warehouse location, main branch name, and catalog type specifics."
)
interface IcebergCatalogSpecifications {

    /**
     * The warehouse location.
     *
     * Specifies the physical or logical location of the data warehouse that the Iceberg catalog
     * uses. For example: `s3://my-bucket/warehouse/`
     */
    @get:JsonSchemaTitle("Warehouse Location")
    @get:JsonPropertyDescription(
        "The root location of the data warehouse used by the Iceberg catalog."
    )
    @get:JsonProperty("warehouse_location")
    val warehouseLocation: String

    /**
     * The name of the main branch in the Nessie repository (or the equivalent main branch in other
     * catalog types).
     *
     * Specifies the default or primary branch name in the catalog repository. For example: `main`
     */
    @get:JsonSchemaTitle("Main Branch Name")
    @get:JsonPropertyDescription("The primary or default branch name in the catalog repository.")
    @get:JsonProperty("main_branch_name")
    val mainBranchName: String

    /**
     * The catalog type.
     *
     * Indicates the type of catalog used (e.g., Nessie or Glue) and provides configuration details
     * specific to that type.
     */
    @get:JsonSchemaTitle("Catalog Type")
    @get:JsonPropertyDescription(
        "Specifies the type of Iceberg catalog (e.g., NESSIE or GLUE) and its associated configuration."
    )
    @get:JsonProperty("catalog_type")
    val catalogType: CatalogType

    /**
     * Converts the current specifications into a common Iceberg catalog configuration object.
     *
     * @return A unified IcebergCatalogConfiguration containing all necessary configuration details.
     */
    fun toIcebergCatalogConfiguration(): IcebergCatalogConfiguration {
        val catalogConfiguration =
            when (catalogType) {
                is GlueCatalogSpecification ->
                    GlueCatalogConfiguration((catalogType as GlueCatalogSpecification).glueId)
                is NessieCatalogSpecification ->
                    NessieCatalogConfiguration(
                        (catalogType as NessieCatalogSpecification).serverUri,
                        (catalogType as NessieCatalogSpecification).accessToken
                    )
            }

        return IcebergCatalogConfiguration(warehouseLocation, mainBranchName, catalogConfiguration)
    }
}

/**
 * A sealed class representing different catalog types for Iceberg.
 *
 * The catalog type determines which underlying service or system (e.g., Nessie or Glue) is used to
 * store and manage Iceberg table metadata.
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "catalog_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = NessieCatalogSpecification::class, name = "NESSIE"),
    JsonSubTypes.Type(value = GlueCatalogSpecification::class, name = "GLUE"),
)
@JsonSchemaTitle("Iceberg Catalog Type")
@JsonSchemaDescription(
    "Determines the specific implementation used by the Iceberg catalog, such as NESSIE or GLUE."
)
sealed class CatalogType(@JsonSchemaTitle("Catalog Type") open val catalogType: Type) {
    /** Enumeration of possible catalog types. */
    enum class Type(@get:JsonValue val catalogTypeName: String) {
        NESSIE("NESSIE"),
        GLUE("GLUE"),
    }
}

/**
 * Nessie catalog specifications.
 *
 * Provides configuration details required to connect to a Nessie server and manage Iceberg table
 * metadata.
 */
@JsonSchemaTitle("Nessie Catalog")
@JsonSchemaDescription("Configuration details for connecting to a Nessie-based Iceberg catalog.")
class NessieCatalogSpecification(
    @JsonSchemaTitle("Catalog Type")
    @JsonProperty("catalog_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val catalogType: Type = Type.NESSIE,

    /**
     * The URI of the Nessie server.
     *
     * This is required to establish a connection. For example: `https://nessie-server.example.com`
     */
    @get:JsonSchemaTitle("Nessie Server URI")
    @get:JsonPropertyDescription(
        "The base URL of the Nessie server used to connect to the Nessie catalog."
    )
    @get:JsonProperty("server_uri")
    @JsonSchemaInject(json = """{"order":1}""")
    val serverUri: String,

    /**
     * Access token for authenticating with the Nessie server.
     *
     * This is optional and used for secure authentication. For example:
     * `a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY`
     */
    @get:JsonSchemaTitle("Nessie Access Token")
    @get:JsonPropertyDescription("Optional token for authentication with the Nessie server.")
    @get:JsonProperty("access_token")
    @get:JsonSchemaInject(
        json =
            """{
            "examples": ["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],
            "airbyte_secret": true,
            "order":2
        }""",
    )
    val accessToken: String?
) : CatalogType(catalogType)

/**
 * Glue catalog specifications.
 *
 * Provides configuration details required to connect to the AWS Glue catalog service and manage
 * Iceberg table metadata.
 */
@JsonSchemaTitle("Glue Catalog")
@JsonSchemaDescription("Configuration details for connecting to an AWS Glue-based Iceberg catalog.")
class GlueCatalogSpecification(
    @JsonSchemaTitle("Catalog Type")
    @JsonProperty("catalog_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val catalogType: Type = Type.GLUE,

    /**
     * The AWS Account ID for the Glue service.
     *
     * Specifies the target AWS Account where the Glue catalog is hosted.
     */
    @get:JsonSchemaTitle("AWS Account ID")
    @get:JsonPropertyDescription(
        "The AWS Account ID associated with the Glue service used by the Iceberg catalog."
    )
    @get:JsonProperty("glue_id")
    @JsonSchemaInject(json = """{"order":1}""")
    val glueId: String,
) : CatalogType(catalogType)

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
    val glueId: String
) : CatalogConfiguration

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
    val accessToken: String?
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
