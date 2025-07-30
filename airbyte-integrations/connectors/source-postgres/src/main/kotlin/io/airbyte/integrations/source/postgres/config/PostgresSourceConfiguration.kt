package io.airbyte.integrations.source.postgres.config

import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
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
        throw NotImplementedError()
    }
}
