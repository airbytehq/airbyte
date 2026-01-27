/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.config

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.internal.ServerSettings
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.ssh.startTunnelAndGetEndpoint
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.temporal.ChronoUnit

@Factory
class ClickhouseBeanFactory {
    /**
     * The endpoint the client connects through.
     *
     * Either the raw clickhouse instance endpoint or an SSH tunnel.
     */
    @Singleton
    @Named("resolvedEndpoint")
    fun resolvedEndpoint(config: ClickhouseConfiguration): String {
        val baseEndpoint =
            startTunnelAndGetEndpoint(config.tunnelConfig, config.hostname, config.port.toInt())
        return "${config.protocol}://$baseEndpoint"
    }

    @Singleton
    fun clickhouseClient(
        config: ClickhouseConfiguration,
        @Named("resolvedEndpoint") endpoint: String,
    ): Client {
        val builder =
            Client.Builder()
                .addEndpoint(endpoint)
                .setUsername(config.username)
                .setPassword(config.password)
                .compressClientRequest(true)
                .setClientName("airbyte-v2")
                .setConnectTimeout(5, ChronoUnit.MINUTES)

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

    @Singleton
    fun aggregatePublishingConfig(clickhouseConfiguration: ClickhouseConfiguration) =
        AggregatePublishingConfig(
            maxRecordsPerAgg = clickhouseConfiguration.resolvedRecordWindowSize,
        )
}
