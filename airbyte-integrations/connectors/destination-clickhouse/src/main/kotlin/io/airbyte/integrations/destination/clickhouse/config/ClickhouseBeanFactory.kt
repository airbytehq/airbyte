/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.config

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.internal.ServerSettings
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import org.apache.sshd.common.util.net.SshdSocketAddress

// TODO this is super hacky - optional also doesn't work
sealed interface Maybe<out T>

@JvmInline value class Some<T>(val value: T) : Maybe<T>

data object None : Maybe<Nothing>

@Factory
class ClickhouseBeanFactory {
    @Singleton
    fun tunnel(config: ClickhouseConfiguration): Maybe<TunnelSession> {
        return when (val ssh = config.tunnelConfig) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(config.hostname, config.port.toInt())
                val sshConnectionOptions: SshConnectionOptions =
                    SshConnectionOptions.fromAdditionalProperties(emptyMap())
                Some(createTunnelSession(remote, ssh, sshConnectionOptions))
            }
            else -> None
        }
    }

    @Singleton
    fun clickhouseClient(
        config: ClickhouseConfiguration,
        tunnel: Maybe<TunnelSession>,
    ): Client {
        val endpoint =
            if (tunnel is Some)
                "${config.protocol}://${tunnel.value.address.hostName}:${tunnel.value.address.port}"
            else config.endpoint

        val builder =
            Client.Builder()
                .addEndpoint(endpoint)
                .setUsername(config.username)
                .setPassword(config.password)
                .compressClientRequest(true)
                .setClientName("airbyte-v2")

        if (config.enableJson) {
            builder
                // allow experimental JSON type
                .serverSetting("allow_experimental_json_type", "1")
                // allow JSON transcoding as a string. We need this to be able to provide a string
                // as a JSON input.
                .serverSetting(ServerSettings.INPUT_FORMAT_BINARY_READ_JSON_AS_STRING, "1")
                .serverSetting(ServerSettings.OUTPUT_FORMAT_BINARY_WRITE_JSON_AS_STRING, "1")
        }

        return builder.build()
    }

    @Singleton
    fun clickhouseConfiguration(
        configFactory: ClickhouseConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<ClickhouseSpecification>,
    ): ClickhouseConfiguration {
        val spec = specFactory.get()

        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()
}
