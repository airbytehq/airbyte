/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton

data class MySQLConfiguration(
    val hostname: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String,
    val sslMode: String,
    val tunnelConfig: SshTunnelMethodConfiguration?,
) : DestinationConfiguration() {

    val jdbcUrl: String
        get() = buildJdbcUrl()

    private fun buildJdbcUrl(): String {
        val params = mutableListOf<String>()

        // SSL mode mapping to MySQL JDBC parameter
        when (sslMode) {
            "disabled" -> params.add("sslMode=DISABLED")
            "preferred" -> params.add("sslMode=PREFERRED")
            "required" -> params.add("sslMode=REQUIRED")
            "verify_ca" -> params.add("sslMode=VERIFY_CA")
            "verify_identity" -> params.add("sslMode=VERIFY_IDENTITY")
        }

        // Additional recommended parameters
        params.add("useUnicode=true")
        params.add("characterEncoding=UTF-8")
        params.add("zeroDateTimeBehavior=CONVERT_TO_NULL")
        params.add("allowPublicKeyRetrieval=true")

        val paramString = if (params.isNotEmpty()) "?${params.joinToString("&")}" else ""
        return "jdbc:mysql://$hostname:$port/$database$paramString"
    }

    object Defaults {
        const val PORT = 3306
        const val SSL_MODE = "preferred"
        const val BATCH_SIZE = 10_000
    }
}

@Singleton
class MySQLConfigurationFactory :
    DestinationConfigurationFactory<MySQLSpecification, MySQLConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MySQLSpecification
    ): MySQLConfiguration {
        return MySQLConfiguration(
            hostname = pojo.hostname,
            port = pojo.port,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
            sslMode = pojo.sslMode.value,
            tunnelConfig = pojo.getTunnelMethodValue(),
        )
    }

    fun makeWithOverrides(
        spec: MySQLSpecification,
        overrides: Map<String, String> = emptyMap()
    ): MySQLConfiguration {
        return MySQLConfiguration(
            hostname = overrides.getOrDefault("host", spec.hostname),
            port = overrides["port"]?.toIntOrNull() ?: spec.port,
            database = overrides.getOrDefault("database", spec.database),
            username = overrides.getOrDefault("username", spec.username),
            password = overrides.getOrDefault("password", spec.password),
            sslMode = overrides.getOrDefault("ssl_mode", spec.sslMode.value),
            tunnelConfig = spec.getTunnelMethodValue(),
        )
    }
}
