/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.microsoft.sqlserver.jdbc.SQLServerDataSource
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.createTunnelSession
import io.micronaut.context.ApplicationContext
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import javax.sql.DataSource
import org.apache.sshd.common.util.net.SshdSocketAddress

@Factory
class DataSourceFactory {

    @Singleton
    fun dataSource(config: MSSQLConfiguration): DataSource {
        val sqlServerDataSource = config.toSQLServerDataSource()
        val dataSource = HikariDataSource()
        dataSource.dataSource = sqlServerDataSource
        dataSource.connectionTimeout = 60000
        dataSource.connectionTestQuery = "SELECT 1"
        dataSource.maximumPoolSize = 10
        dataSource.minimumIdle = 0
        dataSource.idleTimeout = 60000
        dataSource.leakDetectionThreshold = 0
        return dataSource
    }
}

fun MSSQLConfiguration.toSQLServerDataSource(): SQLServerDataSource {
    data class HostAndPort(
        val host: String,
        val port: Int,
    )

    val hostAndPort: HostAndPort =
        if (ssh != null) {
            when (ssh) {
                is SshKeyAuthTunnelMethod,
                is SshPasswordAuthTunnelMethod -> {
                    val remote = SshdSocketAddress(host.trim(), port)
                    val sshConnectionOptions: SshConnectionOptions =
                        SshConnectionOptions.fromAdditionalProperties(emptyMap())
                    val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                    HostAndPort(tunnel.address.hostName, tunnel.address.port)
                }
                else -> {
                    HostAndPort(host.trim(), port)
                }
            }
        } else {
            HostAndPort(host.trim(), port)
        }
    val connectionString =
        StringBuilder()
            .apply {
                append(
                    "jdbc:sqlserver://${hostAndPort.host}:${hostAndPort.port};databaseName=${database}"
                )

                when (sslMethod) {
                    is EncryptedVerify -> {
                        append(";encrypt=true")
                        sslMethod.trustStoreName?.let { append(";trustStoreName=$it") }
                        sslMethod.trustStorePassword?.let { append(";trustStorePassword=$it") }
                        sslMethod.hostNameInCertificate?.let {
                            append(";hostNameInCertificate=$it")
                        }
                    }
                    is EncryptedTrust -> {
                        append(";encrypt=true;trustServerCertificate=true")
                    }
                    is Unencrypted -> {
                        append(";encrypt=false")
                    }
                }

                jdbcUrlParams?.let { append(";$it") }
            }
            .toString()

    return SQLServerDataSource().also {
        it.url = connectionString
        it.user = user
        password?.let(it::setPassword)
    }
}

// Indirection to abstract the fact that we are leveraging micronaut to manage the datasource
// and avoid clients interacting directly with the application context to retrieve a datasource.
@Singleton
class MSSQLDataSourceFactory(private val applicationContext: ApplicationContext) {
    fun getDataSource(config: MSSQLConfiguration): DataSource =
        applicationContext.createBean(DataSource::class.java, config)

    fun disposeDataSource(dataSource: DataSource) {
        applicationContext.destroyBean(dataSource)
    }
}
