/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.config

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.integrations.destination.firebolt.client.FireboltAirbyteClient
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

/** Micronaut factory for creating and wiring Firebolt destination beans. */
@Factory
class FireboltBeanFactory {

    @Singleton
    fun fireboltConfiguration(
        configFactory: FireboltConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<FireboltSpecification>
    ): FireboltConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /** Creates the HikariCP DataSource for Firebolt connections. */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun fireboltDataSource(config: FireboltConfiguration): HikariDataSource {
        val hikariConfig = HikariConfig()
        hikariConfig.driverClassName = "com.firebolt.FireboltDriver"
        hikariConfig.jdbcUrl = buildJdbcUrl(config)
        hikariConfig.maximumPoolSize = 10
        hikariConfig.connectionTimeout = 30_000
        return HikariDataSource(hikariConfig)
    }

    /** Creates the Firebolt SQL client. */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun fireboltAirbyteClient(dataSource: HikariDataSource): FireboltAirbyteClient {
        return FireboltAirbyteClient(dataSource)
    }

    /** CDK dataflow aggregate publishing thresholds. */
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig =
        AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000_000L,
            maxEstBytesPerAgg = 150_000_000L,
            maxEstBytesAllAggregates = 1_500_000_000L,
            maxBufferedAggregates = 10,
        )

    private fun buildJdbcUrl(config: FireboltConfiguration): String {
        val base = "jdbc:firebolt:${config.database}"
        val params = mutableListOf(
            "client_id=${encode(config.clientId)}",
            "client_secret=${encode(config.clientSecret)}",
            "account=${encode(config.account)}",
        )
        config.engine?.let { params.add("engine=${encode(it)}") }
        config.host?.let { params.add("host=${encode(it)}") }
        config.jdbcUrlParams?.let { params.add(it) }
        return "$base?${params.joinToString("&")}"
    }

    private fun encode(value: String): String =
        URLEncoder.encode(value, StandardCharsets.UTF_8)
}
