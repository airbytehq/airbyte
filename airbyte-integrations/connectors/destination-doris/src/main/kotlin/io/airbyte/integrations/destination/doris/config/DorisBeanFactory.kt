/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.config

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.doris.spec.DorisConfiguration
import io.airbyte.integrations.destination.doris.spec.DorisConfigurationFactory
import io.airbyte.integrations.destination.doris.spec.DorisSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import kotlin.time.Duration.Companion.milliseconds
import org.apache.http.client.config.RequestConfig
import org.apache.http.config.ConnectionConfig
import org.apache.http.impl.NoConnectionReuseStrategy
import org.apache.http.impl.client.CloseableHttpClient
import org.apache.http.impl.client.DefaultRedirectStrategy
import org.apache.http.impl.client.HttpClients
import org.apache.http.protocol.HttpRequestExecutor
import org.apache.http.protocol.RequestContent

@Factory
class DorisBeanFactory {

    @Singleton
    fun dorisConfiguration(
        configFactory: DorisConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<DorisSpecification>,
    ): DorisConfiguration {
        return configFactory.makeWithoutExceptionHandling(specFactory.get())
    }

    @Singleton
    fun aggregatePublishingConfig(config: DorisConfiguration) =
        AggregatePublishingConfig(
            maxRecordsPerAgg = config.batchMaxRows,
            maxEstBytesPerAgg = config.batchMaxBytes,
            stalenessDeadlinePerAgg = config.batchFlushIntervalMs.milliseconds,
            maxBufferedAggregates = config.flushQueueSize,
        )

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    @Named("dorisHttpClient")
    fun httpClient(): CloseableHttpClient {
        val connectTimeout = 30 * 1000
        val connectionConfig =
            ConnectionConfig.custom()
                .setCharset(java.nio.charset.StandardCharsets.UTF_8)
                .setMalformedInputAction(java.nio.charset.CodingErrorAction.REPLACE)
                .setUnmappableInputAction(java.nio.charset.CodingErrorAction.REPLACE)
                .build()

        // Same approach as Flink Doris Connector's HttpUtil:
        // Override DefaultRedirectStrategy to allow PUT redirects (Doris FE 307 -> BE)
        return HttpClients.custom()
            .setDefaultConnectionConfig(connectionConfig)
            .setRequestExecutor(HttpRequestExecutor(connectTimeout))
            .setRedirectStrategy(
                object : DefaultRedirectStrategy() {
                    override fun isRedirectable(method: String): Boolean = true
                }
            )
            .setRetryHandler { _, _, _ -> false }
            .setConnectionReuseStrategy(NoConnectionReuseStrategy.INSTANCE)
            .setDefaultRequestConfig(
                RequestConfig.custom()
                    .setConnectTimeout(connectTimeout)
                    .setConnectionRequestTimeout(connectTimeout)
                    .setSocketTimeout(10 * 60 * 1000)
                    .build()
            )
            .addInterceptorLast(RequestContent(true))
            .build()
    }

    @Singleton
    @Named("dorisJdbcConnection")
    fun jdbcConnection(config: DorisConfiguration): Connection {
        Class.forName("com.mysql.cj.jdbc.Driver")
        val conn =
            DriverManager.getConnection(
                config.jdbcUrl,
                config.username,
                config.password,
            )
        conn.createStatement().use { it.execute("SET time_zone = '+00:00'") }
        return conn
    }
}
