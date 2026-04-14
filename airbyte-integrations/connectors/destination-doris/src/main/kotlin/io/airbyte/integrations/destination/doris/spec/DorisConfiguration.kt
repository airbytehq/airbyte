/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class DorisConfiguration(
    val host: String,
    val httpPort: Int,
    val queryPort: Int,
    val database: String,
    val username: String,
    val password: String,
    val batchMaxRows: Long,
    val batchMaxBytes: Long,
    val batchFlushIntervalMs: Long,
    val flushQueueSize: Int,
    val enableGzip: Boolean,
) : DestinationConfiguration() {

    /** Stream Load URL prefix */
    val feHttpUrl: String
        get() = "${Defaults.HTTP_PROTOCOL}://$host:$httpPort"

    /** JDBC URL for DDL operations via MySQL protocol */
    val jdbcUrl: String
        get() = "jdbc:mysql://$host:$queryPort"

    object Defaults {
        const val HTTP_PROTOCOL = "http"
        const val BATCH_MAX_ROWS = 100_000L
        const val BATCH_MAX_BYTES = 50_000_000L
        const val BATCH_FLUSH_INTERVAL_MS = 10_000L
        const val FLUSH_QUEUE_SIZE = 5
    }
}

@Singleton
class DorisConfigurationFactory :
    DestinationConfigurationFactory<DorisSpecification, DorisConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: DorisSpecification): DorisConfiguration {
        return DorisConfiguration(
            host = pojo.host,
            httpPort = pojo.httpPort,
            queryPort = pojo.queryPort,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
            batchMaxRows = pojo.batchMaxRows ?: DorisConfiguration.Defaults.BATCH_MAX_ROWS,
            batchMaxBytes = pojo.batchMaxBytes ?: DorisConfiguration.Defaults.BATCH_MAX_BYTES,
            batchFlushIntervalMs = pojo.batchFlushIntervalMs
                    ?: DorisConfiguration.Defaults.BATCH_FLUSH_INTERVAL_MS,
            flushQueueSize = pojo.flushQueueSize ?: DorisConfiguration.Defaults.FLUSH_QUEUE_SIZE,
            enableGzip = pojo.enableGzip ?: false,
        )
    }

    fun makeWithOverrides(
        spec: DorisSpecification,
        overrides: Map<String, String> = emptyMap()
    ): DorisConfiguration {
        return DorisConfiguration(
            host = overrides.getOrDefault("host", spec.host),
            httpPort = overrides.getOrDefault("http_port", spec.httpPort.toString()).toInt(),
            queryPort = overrides.getOrDefault("query_port", spec.queryPort.toString()).toInt(),
            database = overrides.getOrDefault("database", spec.database),
            username = overrides.getOrDefault("username", spec.username),
            password = overrides.getOrDefault("password", spec.password),
            batchMaxRows = spec.batchMaxRows ?: DorisConfiguration.Defaults.BATCH_MAX_ROWS,
            batchMaxBytes = spec.batchMaxBytes ?: DorisConfiguration.Defaults.BATCH_MAX_BYTES,
            batchFlushIntervalMs = spec.batchFlushIntervalMs
                    ?: DorisConfiguration.Defaults.BATCH_FLUSH_INTERVAL_MS,
            flushQueueSize = spec.flushQueueSize ?: DorisConfiguration.Defaults.FLUSH_QUEUE_SIZE,
            enableGzip = spec.enableGzip ?: false,
        )
    }
}
