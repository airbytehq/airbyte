package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import java.util.Properties

@Factory
class SnowflakeBeansFactory {
    @Singleton fun getConfig(config: DestinationConfiguration) = config as SnowflakeConfiguration

    @Singleton
    fun getSnowflakeClient(config: SnowflakeConfiguration): Connection {
        // Build the Snowflake JDBC URL
        // Format: jdbc:snowflake://<account>.snowflakecomputing.com/?warehouse=<warehouse>&database=<database>&schema=<schema>&role=<role>
        val jdbcUrl = buildString {
            append("jdbc:snowflake://")
            append(config.host)
            append("/?warehouse=")
            append(config.warehouse)
            append("&database=")
            append(config.database)
            append("&schema=")
            append(config.schema)
            append("&role=")
            append(config.role)
        }
        
        // Set up connection properties
        val properties = Properties().apply {
            setProperty("user", config.username)
            setProperty("password", config.password)
            // Additional properties for better performance and compatibility
            setProperty("CLIENT_SESSION_KEEP_ALIVE", "true")
            setProperty("CLIENT_SESSION_KEEP_ALIVE_HEARTBEAT_FREQUENCY", "3600")
            setProperty("APPLICATION", "airbyte-destination-snowflake")
        }
        
        // Create and return the connection
        return DriverManager.getConnection(jdbcUrl, properties)
    }
}
