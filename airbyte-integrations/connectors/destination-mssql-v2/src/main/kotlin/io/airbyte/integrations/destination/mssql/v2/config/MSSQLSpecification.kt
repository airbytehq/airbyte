/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("MSSQL V2 Destination Specification")
class MSSQLSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("The host name of the MSSQL database.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"order":0}""")
    val host: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("The port of the MSSQL database.")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"minimum":0,"maximum":65536,"examples":["1433"],"order":1}""")
    val port: Int = 1433

    @get:JsonSchemaTitle("DB Name")
    @get:JsonPropertyDescription("The name of the MSSQL database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order":2}""")
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        "The default schema tables are written to if the source does not specify a namespace. The usual value for this field is \"public\"."
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(json = """{"examples":["public"],"default":"public","order":3}""")
    val schema: String = "public"

    @get:JsonSchemaTitle("User")
    @get:JsonPropertyDescription("The username which is used to access the database.")
    @get:JsonProperty("user")
    @get:JsonSchemaInject(json = """{"order":4}""")
    val user: String? = null

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("The password associated with this username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"airbyte_secret":true,"order":5}""")
    val password: String? = null

    @get:JsonSchemaTitle("JDBC URL Params")
    @get:JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3)."
    )
    @get:JsonProperty("jdbc_url_params")
    @get:JsonSchemaInject(json = """{""order":6""")
    val jdbcUrlParams: String? = null

    @get:JsonSchemaTitle("Raw Table Schema Name")
    @get:JsonPropertyDescription("The schema to write raw tables into (default: airbyte_internal)")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"default":"airbyte_internal","order":5}""")
    val rawDataSchema: String = "airbyte_internal"
}

@Singleton
class MSSQLSpecificationExtension : DestinationSpecificationExtension {

    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP
        )
    override val supportsIncremental = true
}
