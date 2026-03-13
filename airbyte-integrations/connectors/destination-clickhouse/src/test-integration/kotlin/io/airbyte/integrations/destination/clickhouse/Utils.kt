/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseAirbyteClient
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path

val log = KotlinLogging.logger {}

object Utils {
    fun getConfigPath(relativePath: String): Path =
        Path.of(
            this::class.java.classLoader.getResource(relativePath)?.toURI()
                ?: throw IllegalArgumentException("Resource $relativePath could not be found")
        )

    fun specToConfig(spec: ConfigurationSpecification): ClickhouseConfiguration {
        val configOverrides = mutableMapOf<String, String>()
        return ClickhouseConfigurationFactory()
            .makeWithOverrides(spec as ClickhouseSpecificationOss, configOverrides)
    }

    fun getClickhouseClient(spec: ConfigurationSpecification): Client {
        val config = specToConfig(spec)
        return getClickhouseClient(config)
    }

    fun getClickhouseClient(config: ClickhouseConfiguration): Client {
        return Client.Builder()
            .setPassword(config.password)
            .setUsername(config.username)
            .addEndpoint(config.endpoint)
            .setDefaultDatabase(config.resolvedDatabase)
            .retryOnFailures(ClientFaultCause.None)
            .build()
    }

    fun getClickhouseAirbyteClient(spec: ConfigurationSpecification): ClickhouseAirbyteClient {
        return ClickhouseAirbyteClient(
            getClickhouseClient(spec),
            ClickhouseSqlGenerator(),
            DefaultTempTableNameGenerator(),
        )
    }
}
