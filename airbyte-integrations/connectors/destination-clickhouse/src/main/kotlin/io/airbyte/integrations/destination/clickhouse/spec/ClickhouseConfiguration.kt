/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.spec

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
    val enableJson: Boolean,
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
    ): ClickhouseConfiguration {
        val protocol =
            when (pojo) {
                is ClickhouseSpecificationOss -> pojo.protocol.value
                else -> ClickhouseConnectionProtocol.HTTPS.value
            }

        return ClickhouseConfiguration(
            pojo.hostname,
            pojo.port,
            protocol,
            pojo.database,
            pojo.username,
            pojo.password,
            pojo.enableJson ?: false,
        )
    }

    fun makeWithOverrides(
        spec: ClickhouseSpecification,
        overrides: Map<String, String> = emptyMap()
    ): ClickhouseConfiguration {
        val protocol =
            when (spec) {
                is ClickhouseSpecificationOss -> spec.protocol.value
                else -> ClickhouseConnectionProtocol.HTTPS.value
            }

        return ClickhouseConfiguration(
            hostname = overrides.getOrDefault("hostname", spec.hostname),
            port = overrides.getOrDefault("port", spec.port),
            protocol = overrides.getOrDefault("protocol", protocol),
            database = overrides.getOrDefault("database", spec.database),
            password = overrides.getOrDefault("password", spec.password),
            username = overrides.getOrDefault("username", spec.username),
            enableJson =
                overrides.getOrDefault("enable_json", spec.enableJson.toString()).toBoolean(),
        )
    }
}
