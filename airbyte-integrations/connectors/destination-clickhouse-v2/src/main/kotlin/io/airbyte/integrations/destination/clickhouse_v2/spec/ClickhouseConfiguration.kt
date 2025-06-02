package io.airbyte.integrations.destination.clickhouse_v2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class ClickhouseConfiguration(
    val hostname: String,
    val port: String,
    val database: String,
    val username: String,
    val password: String,
): DestinationConfiguration() {
    val endpoint = "https://$hostname:$port"
    val resolvedDatabase = database.ifEmpty { Defaults.DATABASE_NAME }

    object Defaults {
        const val DATABASE_NAME = "default"
    }
}

@Singleton
class ClickhouseConfigurationFactory :
    DestinationConfigurationFactory<ClickhouseSpecification, ClickhouseConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: ClickhouseSpecification): ClickhouseConfiguration =
        ClickhouseConfiguration(
            pojo.hostname,
            pojo.port,
            pojo.database,
            pojo.username,
            pojo.password,
        )
}
