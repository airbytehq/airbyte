/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class ClickhouseConfiguration(
    val hostname: String,
    val port: String,
    val protocol: String,
    val database: String,
    val username: String,
    val password: String,
) : DestinationConfiguration() {
    val endpoint = "$protocol://$hostname:$port"
    val resolvedDatabase = database.ifEmpty { Defaults.DATABASE_NAME }

    object Defaults {
        const val DATABASE_NAME = "default"
    }
}

@Singleton
class ClickhouseConfigurationFactory :
    DestinationConfigurationFactory<ClickhouseSpecification, ClickhouseConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: ClickhouseSpecification
    ): ClickhouseConfiguration =
        ClickhouseConfiguration(
            pojo.hostname,
            pojo.port,
            pojo.protocol.value,
            pojo.database,
            pojo.username,
            pojo.password,
        )

    fun makeWithOverrides(
        spec: ClickhouseSpecification,
        overrides: Map<String, String> = emptyMap()
    ): ClickhouseConfiguration {
        return ClickhouseConfiguration(
            hostname = overrides.getOrDefault("hostname", spec.hostname),
            port = overrides.getOrDefault("port", spec.port),
            protocol = overrides.getOrDefault("protocol", spec.protocol.value),
            database = overrides.getOrDefault("database", spec.database),
            password = overrides.getOrDefault("password", spec.password),
            username = overrides.getOrDefault("username", spec.username),
        )
    }
}
