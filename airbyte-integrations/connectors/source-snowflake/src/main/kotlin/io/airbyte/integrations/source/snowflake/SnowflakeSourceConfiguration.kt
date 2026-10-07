/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
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
import java.nio.file.Files
import java.nio.file.Path
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
                jdbcProperties["private_key_file"] = createPrivateKeyFile(credentials.privateKey)
                credentials.privateKeyPassword?.let { jdbcProperties["private_key_file_pwd"] = it }
            }
            is ProgrammaticAccessTokenCredentialsSpecification -> {
                // The Snowflake JDBC driver does not require (or use) a username for the
                // programmatic_access_token authenticator; the token identifies the user.
                jdbcProperties["token"] = credentials.programmaticAccessToken
                jdbcProperties["authenticator"] = "programmatic_access_token"
            }
            else ->
                throw ConfigErrorException(
                    "Unsupported credentials type: ${credentials?.javaClass?.name}"
                )
        }

        jdbcProperties["db"] = pojo.database
        jdbcProperties["warehouse"] = pojo.warehouse

        // Fail at login when the configured warehouse, database or schema does not exist or is not
        // authorized. Without this the session opens anyway and CHECK passes, because SHOW commands
        // and LIMIT 0 probes run without a warehouse; the first real query then fails.
        jdbcProperties["validateDefaultParameters"] = "true"
        // The driver probes the AWS, Azure and GCP instance-metadata endpoints on every new
        // connection (telemetry only; no supported auth method needs it) and waits up to 1 s per
        // probe. The CDK opens a connection per query, so this saves ~2 s each.
        jdbcProperties["disablePlatformDetection"] = "true"
        // The Schema option is an exact name. By default the driver treats `_` and `%` in the
        // schema argument of getTables/getColumns/getPrimaryKeys as LIKE wildcards: it then runs
        // `show ... in database` over every schema and filters client-side (12 minutes for a check
        // on
        // a large account), over-matches other schemas (SCHEMA_A also matched SCHEMAXA) and returns
        // their columns and primary keys as duplicates (airbytehq/airbyte#87000, #86998).
        jdbcProperties["ENABLE_WILDCARDS_IN_SHOW_METADATA_COMMANDS"] = "false"

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

    /**
     * Writes the private key to an owner-only temporary file (the driver only accepts a file path)
     * and returns its absolute path. The file is removed when the JVM exits.
     */
    private fun createPrivateKeyFile(fileValue: String): String {
        try {
            val path: Path = Files.createTempFile("snowflake-rsa-key", ".p8")
            path.toFile().deleteOnExit()
            Files.writeString(path, fileValue, StandardCharsets.UTF_8)
            return path.toAbsolutePath().toString()
        } catch (e: Exception) {
            throw RuntimeException("Failed to create file for private key", e)
        }
    }
}
