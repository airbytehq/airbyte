/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.netsuite

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.time.Duration

private val log = KotlinLogging.logger {}

/** Netsuite-specific implementation of [SourceConfiguration] */
data class NetsuiteSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
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

    /** Required to inject [NetsuiteSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun netsuiteSourceConfig(
            factory:
                SourceConfigurationFactory<
                    NetsuiteSourceConfigurationSpecification,
                    NetsuiteSourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<NetsuiteSourceConfigurationSpecification>,
        ): NetsuiteSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

@Singleton
class NetsuiteSourceConfigurationFactory :
    SourceConfigurationFactory<
        NetsuiteSourceConfigurationSpecification, NetsuiteSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: NetsuiteSourceConfigurationSpecification,
    ): NetsuiteSourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
        val sshTunnel: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
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
        Class.forName("com.netsuite.jdbc.openaccess.OpenAccessDriver")

        // todo: fix netsuite address.
        // example:
        // jdbc:ns://<ServiceHost>:1708;ServerDataSource=NetSuite2.com;Encrypted=1;NegotiateSSLClose=false;CustomProperties=(AccountID=<accountID>;RoleID=<roleID>);
        val address =
            "%s:%d;ServerDataSource=NetSuite2.com;encrypted=1;NegotiateSSLClose=false;CustomProperties=(AccountID=${pojo.accountId};RoleID=${pojo.roleId})"
        val jdbcUrlFmt = "jdbc:ns://${address}"

        val sshOpts = SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
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
        return NetsuiteSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            // todo: Fix me;
            namespaces = setOf(""),
            incremental = incrementalConfiguration,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }
}
