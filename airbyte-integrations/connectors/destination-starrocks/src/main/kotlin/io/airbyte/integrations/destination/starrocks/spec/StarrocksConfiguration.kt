/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton

/**
 * Typed, validated StarRocks destination configuration (post-parse view of [StarrocksSpecification]
 * ).
 *
 * - [port] (9030) = MySQL protocol for DDL and `SELECT current_version()`.
 * - [httpPort] (8030) = HTTP Stream Load (used by the load path, issues #9+).
 */
data class StarrocksConfiguration(
    val host: String,
    val port: Int,
    val httpPort: Int,
    val username: String,
    val password: String,
    val database: String,
    val ssl: Boolean,
    val enableJson: Boolean,
    val cdcSoftDelete: Boolean,
    val loadAsJson: Boolean,
    val sslMode: String,
    /**
     * Stream Load body compression: "none"/"gzip"/"zstd". Effective only with the JSON load format
     * on a cluster >= 3.3.2 (validated at check).
     */
    val compression: String = LoadCompression.NONE,
    /** SSH tunnel (jump server) for the JDBC plane; [SshNoTunnelMethod] = direct. Issue #68. */
    val tunnelMethod: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    /** Load over JDBC (batched INSERT/DELETE) instead of HTTP Stream Load — for tunnel/SSL. #68. */
    val loadAsSql: Boolean = false,
    /**
     * Optional StarRocks `replication_num` for tables the connector creates. Null = omit PROPERTIES
     * (cluster default); set to 1 for single-BE shared-nothing clusters. Issue #58.
     */
    val replicationNum: Int? = null,
) : DestinationConfiguration() {
    val resolvedDatabase: String = database.ifEmpty { Defaults.DATABASE_NAME }

    /**
     * JDBC URL (no default schema) for the given host:port. When tunneling, the host:port is the
     * tunnel's local forward; otherwise the configured StarRocks host/port. When ssl is on,
     * `sslMode` selects the verification level (REQUIRED = encrypt only; VERIFY_CA/VERIFY_IDENTITY
     * = verify against the JVM trust store); off = disabled (issue #39).
     */
    fun jdbcUrlFor(jdbcHost: String, jdbcPort: Int): String =
        if (ssl) {
            "jdbc:mysql://$jdbcHost:$jdbcPort/?sslMode=${SslMode.toConnectorJ(sslMode)}"
        } else {
            "jdbc:mysql://$jdbcHost:$jdbcPort/?sslMode=DISABLED"
        }

    /** Direct (untunneled) JDBC URL — convenience for the common no-tunnel path and tests. */
    val jdbcUrl: String
        get() = jdbcUrlFor(host, port)

    object Defaults {
        const val DATABASE_NAME = "default"
    }
}

@Singleton
class StarrocksConfigurationFactory :
    DestinationConfigurationFactory<StarrocksSpecification, StarrocksConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: StarrocksSpecification
    ): StarrocksConfiguration =
        StarrocksConfiguration(
            host = pojo.host,
            port = pojo.port,
            httpPort = pojo.httpPort,
            username = pojo.username,
            password = pojo.password,
            database = pojo.database,
            ssl = pojo.ssl,
            enableJson = pojo.enableJson,
            cdcSoftDelete = CdcDeletionMode.isSoftDelete(pojo.cdcDeletionMode),
            loadAsJson = pojo.loadFormat.isJson,
            sslMode = pojo.sslMode,
            compression = pojo.loadFormat.compression,
            tunnelMethod = pojo.tunnelMethod,
            loadAsSql = LoadMethod.isSql(pojo.loadMethod),
            replicationNum = pojo.replicationNum,
        )
}
