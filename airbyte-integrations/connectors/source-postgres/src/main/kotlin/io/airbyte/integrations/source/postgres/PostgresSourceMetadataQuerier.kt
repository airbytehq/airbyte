/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
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

    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        val table: TableName = base.findTableName(streamID) ?: return listOf()
        val columns: List<JdbcMetadataQuerier.ColumnMetadata> = base.columnMetadata(table)
        val typmods: Map<String, Int> =
            if (columns.any { isNumericArray(it) }) queryTypmods(table) else emptyMap()
        return columns.map { c ->
            val resolved: JdbcMetadataQuerier.ColumnMetadata =
                if (isNumericArray(c)) withNumericArrayElementPrecision(c, typmods[c.name]) else c
            EmittedField(c.label, base.fieldTypeMapper.toFieldType(resolved))
        }
    }

    /**
     * JDBC does not report the precision and scale of array elements, so we read the column's type
     * modifier from the catalog. For `numeric(p,s)[]`, atttypmod holds the element's typmod.
     */
    private fun queryTypmods(table: TableName): Map<String, Int> {
        val sql =
            """
            SELECT a.attname, a.atttypmod
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = ? AND c.relname = ? AND a.attnum > 0 AND NOT a.attisdropped
            """.trimIndent()
        val result = mutableMapOf<String, Int>()
        base.conn.prepareStatement(sql).use { stmt ->
            stmt.setString(1, table.schema)
            stmt.setString(2, table.name)
            stmt.executeQuery().use { rs ->
                while (rs.next()) {
                    result[rs.getString("attname")] = rs.getInt("atttypmod")
                }
            }
        }
        return result
    }

    override fun extraChecks() {
        base.extraChecks()
        validateSslConfiguration()
        if (postgresSourceConfig.incrementalConfiguration is XminIncrementalConfiguration) {
            base.conn.use { conn ->
                if (dbNumWraparound(conn) > 0) {
                    throw ConfigErrorException(xminWraparoundError)
                }
            }
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

        private const val VARHDRSZ = 4

        private fun isNumericArray(c: JdbcMetadataQuerier.ColumnMetadata): Boolean =
            (c.type as? SystemType)?.typeName == "_numeric"

        /**
         * Decodes a numeric typmod the same way the Postgres JDBC driver does for scalar columns.
         * An unconstrained numeric (typmod -1) or a missing typmod yields precision 0 and scale 0.
         */
        fun numericPrecisionAndScale(typmod: Int?): Pair<Int, Int> =
            if (typmod == null || typmod < VARHDRSZ) 0 to 0
            else ((typmod - VARHDRSZ) shr 16 and 0xFFFF) to ((typmod - VARHDRSZ) and 0xFFFF)

        fun withNumericArrayElementPrecision(
            c: JdbcMetadataQuerier.ColumnMetadata,
            typmod: Int?,
        ): JdbcMetadataQuerier.ColumnMetadata {
            val type = c.type as SystemType
            val (precision, scale) = numericPrecisionAndScale(typmod)
            return c.copy(type = type.copy(precision = precision, scale = scale))
        }

        const val xminWraparoundError: String =
            "We detected XMIN transaction wraparound in the database, " +
                "which makes this sync option inefficient and can lead to higher credit consumption. " +
                "Please change the replication method to CDC or cursor based."

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
