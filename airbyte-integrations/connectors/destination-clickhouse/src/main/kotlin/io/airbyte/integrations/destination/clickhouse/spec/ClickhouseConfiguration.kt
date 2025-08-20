/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton

data class ClickhouseConfiguration(
    val hostname: String,
    val port: String,
    val protocol: String,
    val database: String,
    val username: String,
    val password: String,
    val enableJson: Boolean,
    val tunnelConfig: SshTunnelMethodConfiguration?,
    val recordWindowSize: Long?,
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
            hostname = pojo.hostname,
            port = pojo.port,
            protocol = protocol,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
            enableJson = pojo.enableJson ?: false,
            tunnelConfig = pojo.getTunnelMethodValue(),
            recordWindowSize = pojo.recordWindowSize,
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
            tunnelConfig = spec.getTunnelMethodValue(),
            recordWindowSize = spec.recordWindowSize,
        )
    }
}
