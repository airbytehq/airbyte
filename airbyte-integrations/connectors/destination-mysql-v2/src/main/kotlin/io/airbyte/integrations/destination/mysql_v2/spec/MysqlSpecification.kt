package io.airbyte.integrations.destination.mysql_v2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

@Singleton
open class MysqlSpecification : ConfigurationSpecification() {
    @get:JsonProperty("host")
    @get:JsonPropertyDescription("Hostname of the MySQL database server")
    val host: String = ""

    @get:JsonProperty("port")
    @get:JsonPropertyDescription("Port of the MySQL database server")
    val port: Int = 3306

    @get:JsonProperty("database")
    @get:JsonPropertyDescription("Name of the target database")
    val database: String = ""

    @get:JsonProperty("username")
    @get:JsonPropertyDescription("Username for authentication")
    val username: String = ""

    @get:JsonProperty("password")
    @get:JsonPropertyDescription("Password for authentication")
    val password: String = ""

    @get:JsonProperty("ssl")
    @get:JsonPropertyDescription("Whether to use SSL for the connection. Defaults to false.")
    val ssl: Boolean = false

    @get:JsonProperty("ssl_mode")
    @get:JsonPropertyDescription(
        """SSL mode for the connection. Options are:
        - DISABLED: No SSL
        - PREFERRED: Use SSL if available (default)
        - REQUIRED: Require SSL
        - VERIFY_CA: Require SSL and verify CA
        - VERIFY_IDENTITY: Require SSL, verify CA and hostname"""
    )
    val sslMode: SslMode? = SslMode.PREFERRED

    @get:JsonProperty("jdbc_url_params")
    @get:JsonPropertyDescription(
        "Additional JDBC URL parameters (e.g., 'connectTimeout=10000&socketTimeout=60000')"
    )
    val jdbcUrlParams: String? = null

    @get:JsonProperty("batch_size")
    @get:JsonPropertyDescription(
        "Number of records to batch before flushing to the database. Default is 5000."
    )
    val batchSize: Int = 5000
}

enum class SslMode(@get:JsonValue val value: String) {
    DISABLED("DISABLED"),
    PREFERRED("PREFERRED"),
    REQUIRED("REQUIRED"),
    VERIFY_CA("VERIFY_CA"),
    VERIFY_IDENTITY("VERIFY_IDENTITY")
}
