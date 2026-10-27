/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.CloudHostCheck
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection

class PostgresSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
    val postgresSourceConfig: PostgresSourceConfiguration,
    private val featureFlags: Set<FeatureFlag>,
) : MetadataQuerier by base {

    override fun extraChecks() {
        base.extraChecks()
        validateCloudSslConfiguration(postgresSourceConfig, featureFlags)
        validateReplicationMethod(base.conn, postgresSourceConfig)
    }

    companion object {
        private val log = KotlinLogging.logger {}

        /**
         * Validates that the SSL/SSH configuration is sufficient for Airbyte Cloud. On Cloud, we
         * require SSL encryption or an SSH tunnel; connections with ssl_mode in
         * [disable, allow, prefer] and no tunnel are rejected. Shared with the section checks,
         * which apply it to the connection section.
         */
        fun validateCloudSslConfiguration(
            config: PostgresSourceConfiguration,
            featureFlags: Set<FeatureFlag>,
        ) {
            if (!featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)) {
                return
            }
            val sslMode: String? = config.jdbcProperties["sslmode"]
            val acceptableSslModes = listOf("require", "verify-ca", "verify-full")
            val hasNoTunnel = config.sshTunnel is SshNoTunnelMethod
            if (sslMode !in acceptableSslModes && hasNoTunnel) {
                throw ConfigErrorException(
                    "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel. " +
                        "Current SSL mode: $sslMode",
                )
            }
        }

        const val xminWraparoundError: String =
            "We detected XMIN transaction wraparound in the database, " +
                "which makes this sync option inefficient and can lead to higher credit consumption. " +
                "Please change the replication method to CDC or cursor based."

        /**
         * Validates the replication method's prerequisites on the server, with the connection
         * [conn] opened as the configured user: no transaction-id wraparound for Xmin; for CDC,
         * `wal_level = logical`, the replication slot (pgoutput, on this database) and the
         * publication exist, and the user can open a replication connection. The legacy connector
         * (before 3.8.0) checked the slot, the publication and the replication connection at CHECK
         * time as well. Shared with the section checks, which apply it to the sync method section.
         */
        fun validateReplicationMethod(conn: Connection, config: PostgresSourceConfiguration) {
            when (val incremental = config.incrementalConfiguration) {
                is XminIncrementalConfiguration -> {
                    if (dbNumWraparound(conn) > 0) {
                        throw ConfigErrorException(xminWraparoundError)
                    }
                }
                is CdcIncrementalConfiguration ->
                    validateCdcPrerequisites(conn, config, incremental)
                is UserDefinedCursorIncrementalConfiguration ->
                    log.info { "Cursor-based replication has no server-side prerequisite." }
            }
        }

        private fun validateCdcPrerequisites(
            conn: Connection,
            config: PostgresSourceConfiguration,
            cdc: CdcIncrementalConfiguration,
        ) {
            log.info { "Querying the server's wal_level." }
            val walLevel: String? =
                conn.createStatement().use { stmt ->
                    stmt.executeQuery("SHOW wal_level").use { rs ->
                        if (rs.next()) rs.getString(1) else null
                    }
                }
            if (walLevel != "logical") {
                throw ConfigErrorException(
                    "CDC requires the server setting wal_level = logical; it is '$walLevel'.",
                )
            }
            log.info { "Looking up replication slot '${cdc.replicationSlot}'." }
            val plugin: String =
                conn
                    .prepareStatement(
                        "SELECT plugin FROM pg_replication_slots " +
                            "WHERE slot_name = ? AND database = ?",
                    )
                    .use { stmt ->
                        stmt.setString(1, cdc.replicationSlot)
                        stmt.setString(2, config.database)
                        stmt.executeQuery().use { rs ->
                            if (rs.next()) rs.getString("plugin") else null
                        }
                    }
                    ?: throw ConfigErrorException(
                        "Replication slot '${cdc.replicationSlot}' does not exist " +
                            "in database '${config.database}'.",
                    )
            if (plugin != "pgoutput") {
                throw ConfigErrorException(
                    "Replication slot '${cdc.replicationSlot}' uses the '$plugin' output plugin; " +
                        "Airbyte requires pgoutput.",
                )
            }
            log.info { "Looking up publication '${cdc.publication}'." }
            val publicationExists: Boolean =
                conn.prepareStatement("SELECT 1 FROM pg_publication WHERE pubname = ?").use { stmt
                    ->
                    stmt.setString(1, cdc.publication)
                    stmt.executeQuery().use { rs -> rs.next() }
                }
            if (!publicationExists) {
                throw ConfigErrorException(
                    "Publication '${cdc.publication}' does not exist " +
                        "in database '${config.database}'.",
                )
            }
            // The replication connection READ opens first; it fails for a user without the
            // REPLICATION attribute (or the rds_replication role).
            log.info { "Opening a replication connection as '${config.jdbcProperties["user"]}'." }
            (PostgresSourceJdbcConnectionFactory(config).getReplication() as Connection).close()
        }

        public fun dbNumWraparound(conn: Connection): Long {
            log.info { "Querying server xmin wraparound status" }
            val query =
                """
                select (txid_snapshot_xmin(txid_current_snapshot()) >> 32) AS num_wraparound
                """
                    .trimIndent()
            conn.createStatement().use { stmt ->
                stmt.executeQuery(query).use { rs ->
                    if (rs.next()) {
                        val numWraparound = rs.getLong("num_wraparound")
                        return numWraparound
                    }
                }
            }
            return 0
        }
    }
}

@Singleton
@Primary
class Factory(
    val constants: DefaultJdbcConstants,
    val selectQueryGenerator: SelectQueryGenerator,
    val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
    val checkQueries: JdbcCheckQueries,
    val featureFlags: Set<FeatureFlag>,
    val configuredCatalog: ConfiguredAirbyteCatalog? = null,
) : MetadataQuerier.Factory<PostgresSourceConfiguration> {
    override fun session(config: PostgresSourceConfiguration): MetadataQuerier {
        // Before the connection opens: with an unreachable host the network error would win.
        CloudHostCheck.validate(config.realHost, config.sshTunnel, featureFlags)
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val base =
            JdbcMetadataQuerier(
                constants,
                config,
                selectQueryGenerator,
                fieldTypeMapper,
                checkQueries,
                jdbcConnectionFactory,
            )
        return PostgresSourceMetadataQuerier(base, config, featureFlags)
    }
}
