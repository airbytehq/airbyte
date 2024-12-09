package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaExamples
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Oracle source configuration JSON.
 *
 * Use [MySqlSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("MySql Source Spec")
@JsonPropertyOrder(
    value =
    [
        "host",
        "port",
        "database",
        "username",
        "password",
        "jdbc_url_params",
        "ssl",
        //"ssl_mode",
        //"replication_method",
    ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MySqlSourceConfigurationJsonObject : ConfigurationJsonObjectBase() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":0}""")
    @JsonPropertyDescription("The host name of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":1,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("3306")
    @JsonSchemaExamples("3306")
    var port: Int = 3306

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The database name.")
    @JsonSchemaInject(json = """{"order":2}""")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":4,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Parameters (Advanced)")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). For more information read about <a href=\"https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-jdbc-url-format.html\">JDBC URL parameters</a>.",
    )
    @JsonSchemaInject(json = """{"order":5}""")
    var jdbcUrlParams: String? = null

    @JsonProperty("ssl")
    @JsonSchemaTitle("SSL Connection")
    @JsonPropertyDescription("\"Encrypt data using SSL.")
    @JsonSchemaDefault("true")
    @JsonSchemaInject(json = """{"order":6}""")
    var ssl: Boolean = true
}
