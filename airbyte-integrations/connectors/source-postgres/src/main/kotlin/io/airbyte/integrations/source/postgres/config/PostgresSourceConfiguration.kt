/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.config

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.*

private val log = KotlinLogging.logger {}

/** Postgres-specific implementation of [SourceConfiguration] */
data class PostgresSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    // TODO: Initialize parameters with prepareThreshold=0 to mitigate pgbouncer errors
    //  https://github.com/airbytehq/airbyte/issues/24796
    // mapOf(PREPARE_THRESHOLD, "0", TCP_KEEP_ALIVE, "true")
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    val incremental: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    val cdc: CdcIncrementalConfiguration? = incremental as? CdcIncrementalConfiguration

    override val global: Boolean = cdc != null
    override val maxSnapshotReadDuration: Duration? = cdc?.initialLoadTimeout
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
    val shutdownTimeout: Duration,
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class PostgresSourceConfigurationFactory :
    SourceConfigurationFactory<
        PostgresSourceConfigurationSpecification, PostgresSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: PostgresSourceConfigurationSpecification,
    ): PostgresSourceConfiguration {
        val encodedDatabaseName = URLEncoder.encode(pojo.database, StandardCharsets.UTF_8)
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }
        // Parse URL parameters.
        val pattern = "^([^=]+)=(.*)$".toRegex()
        for (pair in (pojo.jdbcUrlParams ?: "").trim().split("&".toRegex())) {
            if (pair.isBlank()) {
                continue
            }
            val result: MatchResult? = pattern.matchEntire(pair)
            if (result == null) {
                log.warn { "ignoring invalid JDBC URL param '$pair'" }
            } else {
                val key: String = result.groupValues[1].trim()
                val urlEncodedValue: String = result.groupValues[2].trim()
                jdbcProperties[key] = URLDecoder.decode(urlEncodedValue, StandardCharsets.UTF_8)
            }
        }
        val incrementalConfiguration: IncrementalConfiguration =
            when (val inc = pojo.getIncrementalConfigurationSpecificationValue()) {
                UserDefinedCursorConfigurationSpecification ->
                    UserDefinedCursorIncrementalConfiguration
                is CdcCursorConfigurationSpecification ->
                    CdcIncrementalConfiguration(
                        initialLoadTimeout =
                            Duration.ofHours(inc.initialLoadTimeoutHours!!.toLong()),
                        invalidCdcCursorPositionBehavior =
                            when (inc.invalidCdcCursorPositionBehavior) {
                                "Fail sync" -> InvalidCdcCursorPositionBehavior.FAIL_SYNC
                                "Re-sync data" -> InvalidCdcCursorPositionBehavior.RESET_SYNC
                                else ->
                                    throw ConfigErrorException(
                                        "Unknown value ${inc.invalidCdcCursorPositionBehavior}"
                                    )
                            },
                        shutdownTimeout =
                            Duration.ofSeconds(inc.debeziumShutdownTimeoutSeconds!!.toLong()),
                    )
            }
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 0)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }
        // TODO: add SSL config to JDBC URL
        // TODO: require SSL not disabled in cloud
        // TODO: only use username from <username>@azure.com when checking privileges
        return PostgresSourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = pojo.getTunnelMethodValue(),
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties()),
            jdbcUrlFmt = "jdbc:postgresql://${pojo.host}:${pojo.port}/$encodedDatabaseName",
            jdbcProperties = jdbcProperties,
            namespaces = pojo.schemas?.toSet() ?: setOf("public"),
            incremental = incrementalConfiguration,
            maxConcurrency = pojo.concurrency ?: 1,
            checkpointTargetInterval = checkpointTargetInterval,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }
}
