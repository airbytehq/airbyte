package io.airbyte.integrations.destination.mysql.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class MySQLConfiguration(
    val hostname: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String,
) : DestinationConfiguration()

@Singleton
class MySQLConfigurationFactory :
    DestinationConfigurationFactory<MySQLSpecification, MySQLConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MySQLSpecification
    ): MySQLConfiguration {
        return MySQLConfiguration(
            hostname = pojo.hostname,
            port = pojo.port,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
        )
    }
}
