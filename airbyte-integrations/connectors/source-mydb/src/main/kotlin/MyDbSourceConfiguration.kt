/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mydb

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

data class MyDbSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val jdbcProperties: Map<String, String>,
    override val jdbcUrlFmt: String = "",
    override val namespaces: Set<String> = setOf<String>(),
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = Duration.ZERO,
    override val maxConcurrency: Int = 1,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ZERO,
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
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
        fun mydbSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MyDbSourceConfigurationSpecification,
                    MyDbSourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<MyDbSourceConfigurationSpecification>,
        ): MyDbSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class MyDbSourceConfigurationFactory :
    SourceConfigurationFactory<MyDbSourceConfigurationSpecification, MyDbSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MyDbSourceConfigurationSpecification
    ): MyDbSourceConfiguration {
        val realHost = pojo.host
        val realPort = pojo.port
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }
        return MyDbSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            jdbcProperties = jdbcProperties,
        )
    }
}
