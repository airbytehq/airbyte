/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
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
        validateSslConfiguration()
        val isXmin = postgresSourceConfig.incrementalConfiguration is XminIncrementalConfiguration
        val isCdc = postgresSourceConfig.cdc != null
        if (!isXmin && !isCdc) return
        base.conn.use { conn ->
            if (isXmin && dbNumWraparound(conn) > 0) {
                throw ConfigErrorException(xminWraparoundError)
            }
            if (isCdc) validateNoEmptyEnumTypes(conn)
        }
    }

    /**
     * Validates that the SSL/SSH configuration is sufficient for Airbyte Cloud. On Cloud, we
     * require SSL encryption or an SSH tunnel; connections with ssl_mode in [disable, allow,
     * prefer] and no tunnel are rejected.
     */
    private fun validateSslConfiguration() {
        if (!featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)) {
            return
        }
        val sslMode: String? = postgresSourceConfig.jdbcProperties["sslmode"]
        val acceptableSslModes = listOf("require", "verify-ca", "verify-full")
        val hasNoTunnel = postgresSourceConfig.sshTunnel is SshNoTunnelMethod
        if (sslMode !in acceptableSslModes && hasNoTunnel) {
            throw ConfigErrorException(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel. " +
                    "Current SSL mode: $sslMode",
            )
        }
    }

    companion object {
        private val log = KotlinLogging.logger {}

        const val xminWraparoundError: String =
            "We detected XMIN transaction wraparound in the database, " +
                "which makes this sync option inefficient and can lead to higher credit consumption. " +
                "Please change the replication method to CDC or cursor based."

        const val EMPTY_ENUM_TYPES_QUERY: String =
            """
            SELECT n.nspname AS schema_name, t.typname AS type_name
            FROM pg_catalog.pg_type t
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            LEFT JOIN (SELECT enumtypid AS id, array_agg(enumlabel) AS vals
                       FROM pg_catalog.pg_enum GROUP BY enumtypid) ev ON t.oid = ev.id
            WHERE n.nspname <> 'pg_toast' AND t.typcategory = 'E' AND ev.vals IS NULL
            ORDER BY schema_name, type_name
            """

        fun emptyEnumTypesError(types: List<String>): String =
            "Database contains enum type(s) with no labels (${types.joinToString(", ")}). " +
                "CDC cannot initialize on such types, even if no synced table uses them."

        public fun dbNumWraparound(conn: Connection): Long {
            log.info { "Querying server xmin wraparound status" }
            val query =
                """
            select (txid_snapshot_xmin(txid_current_snapshot()) >> 32) AS num_wraparound
        """.trimIndent()
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

        fun findEmptyEnumTypes(conn: Connection): List<String> {
            log.info { "Querying PostgreSQL enum types with no labels" }
            conn.createStatement().use { stmt ->
                stmt.executeQuery(EMPTY_ENUM_TYPES_QUERY).use { rs ->
                    return buildList {
                        while (rs.next()) {
                            add("${rs.getString("schema_name")}.${rs.getString("type_name")}")
                        }
                    }
                }
            }
        }

        fun validateNoEmptyEnumTypes(conn: Connection) {
            val types = findEmptyEnumTypes(conn)
            if (types.isNotEmpty()) {
                throw ConfigErrorException(emptyEnumTypesError(types))
            }
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
