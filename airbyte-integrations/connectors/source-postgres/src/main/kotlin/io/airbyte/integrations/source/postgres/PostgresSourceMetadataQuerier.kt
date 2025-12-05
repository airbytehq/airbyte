package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

class PostgresSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
    val postgresSourceConfig: PostgresSourceConfiguration,

): MetadataQuerier by base {
    private val log = KotlinLogging.logger {}

    override fun extraChecks() {
        base.extraChecks()
        if (postgresSourceConfig.incrementalConfiguration is XminIncrementalConfiguration) {
            if (dbNumWraparound() > 0) {
                throw ConfigErrorException("We detected XMIN transaction wraparound in the database, " +
                    "which makes this sync option inefficient and can lead to higher credit consumption. " +
                    "Please change the replication method to CDC or cursor based.")
            }
        }
    }

    private fun dbNumWraparound(): Long {
        log.info { "Querying server xmin wraparound status" }
        val query =
            """
            select (txid_snapshot_xmin(txid_current_snapshot()) >> 32) AS num_wraparound
        """.trimIndent()
        base.conn.createStatement().use { stmt ->
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
