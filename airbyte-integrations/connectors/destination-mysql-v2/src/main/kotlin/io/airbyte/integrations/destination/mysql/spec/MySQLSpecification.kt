package io.airbyte.integrations.destination.mysql.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

@Singleton
open class MySQLSpecification : ConfigurationSpecification() {
    @get:JsonProperty("hostname")
    @get:JsonPropertyDescription("Hostname of the MySQL server")
    val hostname: String = ""

    @get:JsonProperty("port")
    @get:JsonPropertyDescription("Port of the MySQL server")
    val port: Int = 3306  // MySQL default port

    @get:JsonProperty("database")
    @get:JsonPropertyDescription("Name of the database")
    val database: String = ""

    @get:JsonProperty("username")
    @get:JsonPropertyDescription("Username for authentication")
    val username: String = ""

    @get:JsonProperty("password")
    @get:JsonPropertyDescription("Password for authentication")
    @get:JsonSchemaInject(json = """{"airbyte_secret": true}""")
    val password: String = ""
}
