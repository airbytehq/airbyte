/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.time.Duration

private val log = KotlinLogging.logger {}

/** Databricks-specific implementation of [SourceConfiguration] */
data class DatabricksSourceConfiguration(
    override val realHost: String,
    override val realPort: Int = 443, // Databricks uses port 443 for JDBC connections
    // We don't need sshTunnel for Databricks, but we keep the field for compatibility.
    override val sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions(
            kotlin.time.Duration.ZERO,
            kotlin.time.Duration.ZERO,
            kotlin.time.Duration.ZERO
        ),
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String> = emptySet(),
    val schema: String? = null,
    val incremental: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
) : JdbcSourceConfiguration {
    override val global = false
    override val maxSnapshotReadDuration: Duration? =
        when (incremental) {
            UserDefinedCursorIncrementalConfiguration -> null
        }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

@Singleton
class DatabricksSourceConfigurationFactory :
    SourceConfigurationFactory<
        DatabricksSourceConfigurationSpecification,
        DatabricksSourceConfiguration,
    > {

    companion object {
        private const val PRIVATE_KEY_FILE_NAME = "rsa_key.p8"
    }

    override fun makeWithoutExceptionHandling(
        pojo: DatabricksSourceConfigurationSpecification,
    ): DatabricksSourceConfiguration {
        val realHost: String = pojo.host
        val jdbcProperties = mutableMapOf<String, String>()

        // Handle credentials based on auth type
        when (val credentials = pojo.credentials) {
            is PersonalAccessTokenCredentialsSpecification -> {
                jdbcProperties["AuthMech"] = "3"
                jdbcProperties["UID"] = "token"
                jdbcProperties["PWD"] = credentials.token
            }
            else ->
                throw ConfigErrorException(
                    "Unsupported credentials type: ${credentials?.javaClass?.name}"
                )
        }

        jdbcProperties["transportMode"] = "http"
        jdbcProperties["ssl"] = "1"
        jdbcProperties["httpPath"] = pojo.http_path

        // Disable Apache Arrow for now as it is causing issue in jdbc
        jdbcProperties["EnableArrow"] = "0"

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

        // Load Databricks JDBC driver
        Class.forName("com.databricks.client.jdbc.Driver")

        val jdbcUrlFmt = "jdbc:databricks://%s:%d"

        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 0)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }
        val maxConcurrency: Int = pojo.concurrency ?: 0
        if ((pojo.concurrency ?: 0) <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }
        val incrementalConfiguration: IncrementalConfiguration =
            UserDefinedCursorIncrementalConfiguration
        return DatabricksSourceConfiguration(
            realHost = realHost,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = setOf(pojo.database),
            schema = pojo.schema,
            incremental = incrementalConfiguration,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }
}
