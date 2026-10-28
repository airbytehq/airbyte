/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration

@JsonSchemaTitle("REST Catalog")
class RestCatalogSpec(
    @JsonProperty("catalog_type")
    @JsonSchemaTitle("Catalog Type")
    override val catalogType: Type = Type.REST,
    @get:JsonProperty("server_uri")
    @get:JsonSchemaTitle("REST Server URI")
    @get:JsonPropertyDescription("The base URL of the Iceberg REST catalog.")
    val serverUri: String,
    @get:JsonProperty("namespace")
    @get:JsonSchemaTitle("Default Namespace")
    @get:JsonPropertyDescription(
        "The default namespace for destination-defined tables. Defaults to the top-level namespace.",
    )
    val namespace: String? = null,
    @get:JsonSchemaTitle("Warehouse")
    @get:JsonPropertyDescription(
        "Optional catalog warehouse identifier, such as a Unity Catalog catalog name. Overrides Warehouse Location for REST requests.",
    )
    @get:JsonProperty("warehouse")
    val warehouse: String? = null,
    @get:JsonSchemaTitle("Bearer Token")
    @get:JsonPropertyDescription(
        "Optional bearer token. Do not combine with OAuth client credentials.",
    )
    @get:JsonProperty("token")
    @get:JsonSchemaInject(json = """{"airbyte_secret":true}""")
    val token: String? = null,
    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription("Optional OAuth client ID. Requires client_secret.")
    @get:JsonProperty("client_id")
    val clientId: String? = null,
    @get:JsonSchemaTitle("Client Secret")
    @get:JsonPropertyDescription("Optional OAuth client secret. Requires client_id.")
    @get:JsonProperty("client_secret")
    @get:JsonSchemaInject(json = """{"airbyte_secret":true}""")
    val clientSecret: String? = null,
    @get:JsonSchemaTitle("OAuth2 Server URI")
    @get:JsonPropertyDescription("Optional OAuth2 token endpoint URI.")
    @get:JsonProperty("oauth2_server_uri")
    val oauth2ServerUri: String? = null,
    @get:JsonSchemaTitle("OAuth Scope")
    @get:JsonPropertyDescription("Optional OAuth scope, such as all-apis for Databricks.")
    @get:JsonProperty("scope")
    val scope: String? = null,
) : GcsCatalogType(catalogType) {
    fun toConfiguration(defaultNamespace: String) =
        RestCatalogConfiguration(
            serverUri,
            namespace ?: defaultNamespace,
            warehouse,
            token,
            clientId,
            clientSecret,
            oauth2ServerUri,
            scope,
        )
}
