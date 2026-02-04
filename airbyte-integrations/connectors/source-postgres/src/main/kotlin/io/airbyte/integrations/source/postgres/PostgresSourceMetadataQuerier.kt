/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
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
) : MetadataQuerier by base {

    override fun extraChecks() {
        base.extraChecks()
        if (postgresSourceConfig.incrementalConfiguration is XminIncrementalConfiguration) {
            base.conn.use { conn ->
                if (dbNumWraparound(conn) > 0) {
                    throw ConfigErrorException(xminWraparoundError)
                }
            }
        }
    }

    companion object {
        private val log = KotlinLogging.logger {}

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
        return PostgresSourceMetadataQuerier(base, config)
    }
}
