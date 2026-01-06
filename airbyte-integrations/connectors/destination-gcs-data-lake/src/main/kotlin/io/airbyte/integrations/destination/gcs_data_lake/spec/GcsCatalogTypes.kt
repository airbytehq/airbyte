/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "catalog_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = BigLakeCatalogSpec::class, name = "BIGLAKE"),
    JsonSubTypes.Type(value = PolarisCatalogSpec::class, name = "POLARIS"),
)
@JsonSchemaTitle("Catalog Type")
sealed class GcsCatalogType(@JsonSchemaTitle("Catalog Type") open val catalogType: Type) {
    enum class Type(@get:JsonValue val typeName: String) {
        BIGLAKE("BIGLAKE"),
        POLARIS("POLARIS"),
    }
}

@JsonSchemaTitle("BigLake Catalog")
@JsonSchemaDescription("Configuration for Google Cloud BigLake Iceberg catalog.")
class BigLakeCatalogSpec(
    @JsonSchemaTitle("Catalog Type")
    @JsonProperty("catalog_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val catalogType: Type = Type.BIGLAKE,
    @get:JsonSchemaTitle("Catalog Name")
    @get:JsonPropertyDescription(
        "The name of the BigLake catalog. This should match the catalog you created in BigLake metastore."
    )
    @get:JsonProperty("catalog_name")
    @JsonSchemaInject(json = """{"examples": ["integration-test-biglake", "default"], "order":1}""")
    val catalogName: String,
) : GcsCatalogType(catalogType)

@JsonSchemaTitle("Polaris Catalog")
@JsonSchemaDescription("Configuration for Apache Polaris Iceberg catalog.")
class PolarisCatalogSpec(
    @JsonSchemaTitle("Catalog Type")
    @JsonProperty("catalog_type")
    @JsonSchemaInject(json = """{"order":0}""")
    override val catalogType: Type = Type.POLARIS,
    @get:JsonSchemaTitle("Polaris Server URI")
    @get:JsonPropertyDescription(
        "The base URL of the Polaris server. For example: http://localhost:8181/api/catalog"
    )
    @get:JsonProperty("server_uri")
    @JsonSchemaInject(json = """{"order":1}""")
    val serverUri: String,
    @get:JsonSchemaTitle("Polaris Catalog Name")
    @get:JsonPropertyDescription(
        "The name of the catalog in Polaris. This corresponds to the catalog name created via the Polaris Management API."
    )
    @get:JsonProperty("catalog_name")
    @JsonSchemaInject(json = """{"order":2}""")
    val catalogName: String,
    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription("The OAuth Client ID for authenticating with the Polaris server.")
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(
        json = """{"examples": ["abc123clientid"], "airbyte_secret": true, "order":3}"""
    )
    val clientId: String,
    @get:JsonSchemaTitle("Client Secret")
    @get:JsonPropertyDescription(
        "The OAuth Client Secret for authenticating with the Polaris server."
    )
    @get:JsonProperty("client_secret")
    @get:JsonSchemaInject(
        json = """{"examples": ["secretkey123"], "airbyte_secret": true, "order":4}"""
    )
    val clientSecret: String,
) : GcsCatalogType(catalogType)
