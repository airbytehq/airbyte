/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mydb

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

@JsonSchemaTitle("MyDb Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "username",
            "password",
        ],
)

@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MyDbSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("1234")
    @JsonPropertyDescription(
        "Port of the database.",
    )
    var port: Int = 1234

    @JsonProperty("username")
    @JsonSchemaTitle("User")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null
}
