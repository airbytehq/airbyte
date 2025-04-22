/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.cdk

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.util.function.Supplier

class IntegrationTestOperations(
    private val configSpec: ConfigurationSpecification,
    // TODO: expand to non-JDBC sources
    jdbcConfig: JdbcSourceConfiguration,
    private val setupDdlStatements: List<String> = listOf(),
    private val teardownDdlStatements: List<String> = listOf(),
) : AutoCloseable {

    private val log = KotlinLogging.logger {}
    private val connectionFactory: Supplier<Connection> = JdbcConnectionFactory(jdbcConfig)

    fun setup() {
        connectionFactory.get().use { connection: Connection ->
            for (ddl in setupDdlStatements) {
                log.info { "executing setup DDL: $ddl" }
                connection.createStatement().use { stmt -> stmt.execute(ddl) }
            }
        }
    }

    fun execute(sqlStatements: List<String>) {
        connectionFactory.get().use { connection: Connection ->
            for (sql in sqlStatements) {
                log.info { "executing SQL: $sql" }
                connection.createStatement().use { stmt -> stmt.execute(sql) }
            }
        }
    }

    fun check(): Boolean {
        val output = CliRunner.source("check", configSpec).run()
        return output.records().isEmpty()
    }

    fun discover(): Map<String, AirbyteStream> {
        val output: BufferingOutputConsumer = CliRunner.source("discover", configSpec).run()
        val streams: Map<String, AirbyteStream> =
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        return streams
    }

    fun sync(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = listOf(),
        vararg featureFlags: FeatureFlag
    ): BufferingOutputConsumer {
        return CliRunner.source("read", configSpec, catalog, state, *featureFlags).run()
    }

    override fun close() {
        teardown()
    }

    private fun teardown() {
        connectionFactory.get().use { connection: Connection ->
            for (ddl in teardownDdlStatements) {
                log.info { "executing teardown DDL: $ddl" }
                connection.createStatement().use { stmt -> stmt.execute(ddl) }
            }
        }
    }
}
