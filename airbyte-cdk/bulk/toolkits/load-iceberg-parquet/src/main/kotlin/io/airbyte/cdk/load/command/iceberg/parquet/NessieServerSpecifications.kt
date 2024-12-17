/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.iceberg.parquet

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Interface defining specifications for connecting to a Nessie server. This includes details such
 * as server URI, authentication tokens, and repository settings.
 */
interface NessieServerSpecifications {

    /**
     * The URI of the Nessie server.
     *
     * This field is required and specifies the base URL used to connect to the Nessie server.
     * Example: `https://nessie-server.example.com`
     */
    @get:JsonSchemaTitle("Nessie Server URI")
    @get:JsonPropertyDescription(
        "The URI of the Nessie server, required to establish a connection."
    )
    @get:JsonProperty("server_uri")
    val serverUri: String

    /**
     * Access token for authenticating with the Nessie server.
     *
     * This field is optional and can be used for secure authentication. Example:
     * `a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY`
     */
    @get:JsonSchemaTitle("Nessie Access Token")
    @get:JsonPropertyDescription("Optional token for authenticating with the Nessie server.")
    @get:JsonProperty("access_token")
    @get:JsonSchemaInject(
        json =
            """{
            "examples": ["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],
            "airbyte_secret": true
        }""",
    )
    val accessToken: String?

    /**
     * The warehouse location for the Nessie server.
     *
     * Specifies the physical or logical location of the data warehouse managed by Nessie. Example:
     * `s3://my-bucket/warehouse/`
     */
    @get:JsonSchemaTitle("Nessie Warehouse Location")
    @get:JsonPropertyDescription(
        "The location of the data warehouse associated with the Nessie repository."
    )
    @get:JsonProperty("warehouse_location")
    val warehouseLocation: String

    /**
     * The name of the main branch in the Nessie repository.
     *
     * Specifies the default or primary branch name in the Nessie repository. Example: `main`
     */
    @get:JsonSchemaTitle("Nessie Main Branch Name")
    @get:JsonPropertyDescription("The name of the main branch in the Nessie repository.")
    @get:JsonProperty("main_branch_name")
    val mainBranchName: String

    fun toNessieServerConfiguration(): NessieServerConfiguration {
        return NessieServerConfiguration(serverUri, accessToken, warehouseLocation, mainBranchName)
    }
}

data class NessieServerConfiguration(
    val serverUri: String,
    val accessToken: String?,
    val warehouseLocation: String,
    val mainBranchName: String
)

interface NessieServerConfigurationProvider {
    val nessieServerConfiguration: NessieServerConfiguration
}
