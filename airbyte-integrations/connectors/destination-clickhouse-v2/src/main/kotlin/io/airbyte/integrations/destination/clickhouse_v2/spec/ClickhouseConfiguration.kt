package io.airbyte.integrations.destination.clickhouse_v2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration

data class ClickhouseConfiguration(
    val hostname: String,
    val port: String,
    val protocol: String,
    val database: String,
    val username: String,
    val password: String,
): DestinationConfiguration() {
    val endpoint = "$protocol://$hostname:$port"
    val resolvedDatabase = database.ifEmpty { Defaults.DATABASE_NAME }

    object Defaults {
        const val DATABASE_NAME = "default"
    }
}
