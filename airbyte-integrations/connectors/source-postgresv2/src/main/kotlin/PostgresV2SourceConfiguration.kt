/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgresv2

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

data class PostgresV2SourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val jdbcProperties: Map<String, String>,
    override val jdbcUrlFmt: String = "",
    val dbName: String = "",
    override val namespaces: Set<String> = setOf<String>(),
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = Duration.ZERO,
    override val maxConcurrency: Int = 1,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ZERO,
    override val sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions(
            kotlin.time.Duration.ZERO,
            kotlin.time.Duration.ZERO,
            kotlin.time.Duration.ZERO
        ),
) : JdbcSourceConfiguration {

    @Factory
    private class MicronautFactory {
        @Singleton
        fun postgresV2Config(
            factory:
                SourceConfigurationFactory<
                    PostgresV2SourceConfigurationSpecification,
                    PostgresV2SourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<PostgresV2SourceConfigurationSpecification>,
        ): PostgresV2SourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class PostgresV2SourceConfigurationFactory :
    SourceConfigurationFactory<PostgresV2SourceConfigurationSpecification, PostgresV2SourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: PostgresV2SourceConfigurationSpecification
    ): PostgresV2SourceConfiguration {
        val realHost = pojo.host
        val realPort = pojo.port
        val dbName = pojo.database

        val jdbcUrlFmt = "jdbc:postgresql://%s:%s/$dbName";
        val jdbcProperties = mutableMapOf<String, String>()
        val defaultSchema = "public"
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }
        return PostgresV2SourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            dbName = dbName,
            jdbcProperties = jdbcProperties,
            jdbcUrlFmt = jdbcUrlFmt,
            namespaces = pojo.schemas?.toSet() ?: setOf(defaultSchema),
        )
    }
}
