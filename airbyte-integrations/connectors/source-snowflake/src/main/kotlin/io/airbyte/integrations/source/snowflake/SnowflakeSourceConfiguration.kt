/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

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

/** Snowflake-specific implementation of [SourceConfiguration] */
data class SnowflakeSourceConfiguration(
    override val realHost: String,
    override val realPort: Int = 443, // Snowflake uses port 443 for JDBC connections
    // We don't need sshTunnel for Snowflake, but we keep the field for compatibility.
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
class SnowflakeSourceConfigurationFactory :
    SourceConfigurationFactory<
        SnowflakeSourceConfigurationSpecification,
        SnowflakeSourceConfiguration,
    > {

    companion object {
        private const val PRIVATE_KEY_FILE_NAME = "rsa_key.p8"
    }

    override fun makeWithoutExceptionHandling(
        pojo: SnowflakeSourceConfigurationSpecification,
    ): SnowflakeSourceConfiguration {
        val realHost: String = pojo.host
        val jdbcProperties = mutableMapOf<String, String>()

        // Handle credentials based on auth type
        when (val credentials = pojo.credentials) {
            is UsernamePasswordCredentialsSpecification -> {
                jdbcProperties["user"] = credentials.username
                jdbcProperties["password"] = credentials.password
            }
            is KeyPairCredentialsSpecification -> {
                jdbcProperties["user"] = credentials.username
                createPrivateKeyFile(credentials.privateKey)
                jdbcProperties["private_key_file"] = PRIVATE_KEY_FILE_NAME
                credentials.privateKeyPassword?.let { jdbcProperties["private_key_file_pwd"] = it }
            }
            else ->
                throw ConfigErrorException(
                    "Unsupported credentials type: ${credentials?.javaClass?.name}"
                )
        }

        jdbcProperties["db"] = pojo.database
        jdbcProperties["warehouse"] = pojo.warehouse

        // Disable Apache Arrow for now as it is causing issue in jdbc
        jdbcProperties["enableArrow"] = "false"

        pojo.schema?.let { jdbcProperties["schema"] = it }
        pojo.role.let { jdbcProperties["role"] = it }

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

        // Load Snowflake JDBC driver
        Class.forName("net.snowflake.client.jdbc.SnowflakeDriver")

        val jdbcUrlFmt = "jdbc:snowflake://%s"

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
        return SnowflakeSourceConfiguration(
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

    private fun createPrivateKeyFile(fileValue: String) {
        try {
            java.io.File(PRIVATE_KEY_FILE_NAME).writeText(fileValue, StandardCharsets.UTF_8)
        } catch (e: Exception) {
            throw RuntimeException("Failed to create file for private key", e)
        }
    }
}
