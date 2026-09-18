/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.destination.starrocks.http.StreamLoadClient
import io.airbyte.integrations.destination.starrocks.spec.LoadCompression
import io.airbyte.integrations.destination.starrocks.spec.StarrocksConfiguration
import io.airbyte.integrations.destination.starrocks.sql.quoteIdent
import io.airbyte.integrations.destination.starrocks.tunnel.StarrocksSshTunnel
import io.airbyte.integrations.destination.starrocks.version.StarrocksVersionGate
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import java.util.UUID

/**
 * Whether the configured load method is compatible with the tunnel setting. An SSH tunnel only
 * forwards the JDBC connection; Stream Load's HTTP data plane (with its FE->BE 307 redirect) cannot
 * traverse it, so a tunnel requires the SQL load method (#68).
 */
internal fun tunnelLoadMethodCompatible(
    tunnelMethod: SshTunnelMethodConfiguration,
    loadAsSql: Boolean,
): Boolean = tunnelMethod is SshNoTunnelMethod || loadAsSql

/**
 * `check` for StarRocks. Validates BOTH planes the connector uses, so that a passing check actually
 * implies a working sync:
 * 1. Control plane (MySQL protocol, `port` 9030): connect, read `current_version()`, apply the
 * ```
 *    connector's feature gating ([StarrocksVersionGate]).
 * ```
 * 2. Data plane (HTTP Stream Load, `http_port` 8030): create a throwaway table, Stream Load one
 * row,
 * ```
 *    and drop it — exercising http_port reachability, Basic-auth, and INSERT privilege. Previously
 *    `check` only opened JDBC, so it could pass while every write failed (issue #44).
 * ```
 * CDK 1.0.13 [DestinationChecker] is non-parameterized: the config is injected and `check()` takes
 * no arguments. Any thrown exception becomes the FAILED connection-status message.
 */
@Singleton
class StarrocksChecker(
    private val config: StarrocksConfiguration,
    private val tunnel: StarrocksSshTunnel,
) : DestinationChecker {

    override fun check() {
        // When an SSH tunnel is configured it opens on bean construction — so a passing check also
        // proves the bastion + tunnel work. Connect over the (possibly tunneled) JDBC endpoint.
        DriverManager.getConnection(
                config.jdbcUrlFor(tunnel.jdbcHost, tunnel.jdbcPort),
                config.username,
                config.password,
            )
            .use { conn ->
                val version =
                    conn.createStatement().use { stmt ->
                        stmt.executeQuery("SELECT current_version()").use { rs ->
                            require(rs.next()) {
                                "StarRocks check failed: current_version() returned no rows"
                            }
                            rs.getString(1)
                        }
                    }
                require(!version.isNullOrBlank()) { "StarRocks check failed: empty version string" }
                StarrocksVersionGate.validate(version)

                require(tunnelLoadMethodCompatible(config.tunnelMethod, config.loadAsSql)) {
                    "StarRocks check failed: an SSH tunnel only forwards the JDBC connection, but the Stream " +
                        "Load data plane is HTTP and cannot be tunneled. Set the load method to 'SQL'."
                }

                if (config.loadAsSql) {
                    validateSqlLoad(conn)
                } else {
                    // Compression is a Stream Load (JSON) feature; fail fast if requested on too
                    // old a cluster.
                    if (LoadCompression.isEnabled(config.compression)) {
                        require(StarrocksVersionGate.capabilities(version).compression) {
                            "StarRocks check failed: JSON compression '${config.compression}' requires StarRocks " +
                                ">= ${StarrocksVersionGate.MIN_COMPRESSION}; detected $version. Use an uncompressed JSON format."
                        }
                    }
                    validateStreamLoad(conn)
                }
            }
    }

    /**
     * DDL for the throwaway check table. Mirrors the real createTable's `replication_num` (issue
     * #58) so a passing check implies a *creatable* real table: a single-BE shared-nothing cluster
     * (which needs `replication_num=1`) fails here instead of passing and then breaking the first
     * sync. Unset => no PROPERTIES => FE default, matching
     * [io.airbyte.integrations.destination.starrocks.sql.StarrocksSqlGenerator.createTable].
     */
    private fun checkTableDdl(qualified: String): String {
        val props = config.replicationNum?.let { " PROPERTIES(\"replication_num\"=\"$it\")" } ?: ""
        return "CREATE TABLE IF NOT EXISTS $qualified (${quoteIdent("id")} INT NOT NULL) " +
            "DUPLICATE KEY(${quoteIdent("id")}) DISTRIBUTED BY HASH(${quoteIdent("id")}) BUCKETS 1$props"
    }

    /**
     * Round-trips one row through a JDBC INSERT into a throwaway table, then drops it (SQL load).
     */
    private fun validateSqlLoad(conn: Connection) {
        val database = config.resolvedDatabase
        val table = "_airbyte_check_${UUID.randomUUID().toString().replace("-", "")}"
        val qualified = "${quoteIdent(database)}.${quoteIdent(table)}"
        conn.createStatement().use { stmt ->
            stmt.execute("CREATE DATABASE IF NOT EXISTS ${quoteIdent(database)}")
            stmt.execute(checkTableDdl(qualified))
        }
        try {
            conn.prepareStatement("INSERT INTO $qualified (${quoteIdent("id")}) VALUES (?)").use {
                ps ->
                ps.setString(1, "1")
                ps.executeUpdate()
            }
        } finally {
            conn.createStatement().use { it.execute("DROP TABLE IF EXISTS $qualified") }
        }
    }

    /** Round-trips one row through Stream Load into a throwaway table, then drops it. */
    private fun validateStreamLoad(conn: Connection) {
        val database = config.resolvedDatabase
        val table = "_airbyte_check_${UUID.randomUUID().toString().replace("-", "")}"
        val qualified = "${quoteIdent(database)}.${quoteIdent(table)}"

        conn.createStatement().use { stmt ->
            stmt.execute("CREATE DATABASE IF NOT EXISTS ${quoteIdent(database)}")
            stmt.execute(checkTableDdl(qualified))
        }
        try {
            val response =
            // Stream Load stays HTTP regardless of `ssl` (StarRocks' http_port is plain HTTP even
            // on TLS-enabled clusters; `ssl` is for the JDBC control plane only).
            StreamLoadClient(config.host, config.httpPort, config.username, config.password)
                    .streamLoad(
                        database = database,
                        table = table,
                        label = "airbyte-check-${UUID.randomUUID()}",
                        headers =
                            mapOf("format" to "CSV", "column_separator" to ",", "columns" to "id"),
                        body = "1\n".toByteArray(),
                    )
            require(response.isSuccess) {
                "StarRocks check failed: Stream Load probe to $qualified did not succeed " +
                    "(status=${response.status}, message=${response.message}). Verify http_port " +
                    "(${config.httpPort}) reachability, credentials, and INSERT privilege."
            }
        } finally {
            conn.createStatement().use { it.execute("DROP TABLE IF EXISTS $qualified") }
        }
    }
}
