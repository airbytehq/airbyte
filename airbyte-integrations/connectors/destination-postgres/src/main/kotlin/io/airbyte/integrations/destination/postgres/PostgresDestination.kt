/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addThrowableForDeinterpolation
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils
import io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.obtainConnectionOptions
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.postgres.typing_deduping.*
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.*
import org.postgresql.util.PSQLException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class PostgresDestination :
    AbstractJdbcDestination<PostgresState>(DRIVER_CLASS, PostgresSQLNameTransformer()),
    Destination {
    override fun modifyDataSourceBuilder(
        builder: DataSourceFactory.DataSourceBuilder
    ): DataSourceFactory.DataSourceBuilder {
        // Anything in the pg_temp schema is only visible to the connection that created it.
        // So this creates an airbyte_safe_cast function that only exists for the duration of
        // a single connection.
        // This avoids issues with creating the same function concurrently (e.g. if multiple syncs
        // run
        // at the same time).
        // Function definition copied from https://dba.stackexchange.com/a/203986

        // Adding 60 seconds to connection timeout, for ssl connections, default 10 seconds is not
        // enough

        return builder
            .withConnectionTimeout(Duration.ofSeconds(60))
            .withConnectionInitSql(
                """
                               CREATE OR REPLACE FUNCTION pg_temp.airbyte_safe_cast(_in text, INOUT _out ANYELEMENT)
                                 LANGUAGE plpgsql AS
                               ${'$'}func${'$'}
                               BEGIN
                                 EXECUTE format('SELECT %L::%s', ${'$'}1, pg_typeof(_out))
                                 INTO  _out;
                               EXCEPTION WHEN others THEN
                                 -- do nothing: _out already carries default
                               END
                               ${'$'}func${'$'};
                               
                               """.trimIndent()
            )
    }

    public override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        if (
            !config.has(PostgresSslConnectionUtils.PARAM_SSL) ||
                config
                    .get(
                        PostgresSslConnectionUtils.PARAM_SSL,
                    )
                    .asBoolean()
        ) {
            if (config.has(PostgresSslConnectionUtils.PARAM_SSL_MODE)) {
                if (
                    PostgresSslConnectionUtils.DISABLE ==
                        config
                            .get(PostgresSslConnectionUtils.PARAM_SSL_MODE)
                            .get(PostgresSslConnectionUtils.PARAM_MODE)
                            .asText()
                ) {
                    additionalParameters["sslmode"] = PostgresSslConnectionUtils.DISABLE
                } else {
                    additionalParameters.putAll(
                        obtainConnectionOptions(
                            config.get(
                                PostgresSslConnectionUtils.PARAM_SSL_MODE,
                            ),
                        ),
                    )
                }
            } else {
                additionalParameters[JdbcUtils.SSL_KEY] = "true"
                additionalParameters["sslmode"] = "require"
            }
        }
        return additionalParameters
    }

    override fun toJdbcConfig(config: JsonNode): JsonNode {
        val schema =
            Optional.ofNullable(config[JdbcUtils.SCHEMA_KEY])
                .map { obj: JsonNode -> obj.asText() }
                .orElse("public")

        var encodedDatabase = config[JdbcUtils.DATABASE_KEY].asText()
        if (encodedDatabase != null) {
            encodedDatabase = URLEncoder.encode(encodedDatabase, StandardCharsets.UTF_8)
        }
        val jdbcUrl =
            String.format(
                "jdbc:postgresql://%s:%s/%s?",
                config[JdbcUtils.HOST_KEY].asText(),
                config[JdbcUtils.PORT_KEY].asText(),
                encodedDatabase
            )

        val configBuilder =
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.USERNAME_KEY, config[JdbcUtils.USERNAME_KEY].asText())
                .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
                .put(JdbcUtils.SCHEMA_KEY, schema)

        if (config.has(JdbcUtils.PASSWORD_KEY)) {
            configBuilder.put(JdbcUtils.PASSWORD_KEY, config[JdbcUtils.PASSWORD_KEY].asText())
        }

        if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
            configBuilder.put(
                JdbcUtils.JDBC_URL_PARAMS_KEY,
                config[JdbcUtils.JDBC_URL_PARAMS_KEY].asText()
            )
        }

        return jsonNode(configBuilder.build())
    }

    override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator {
        return PostgresSqlGenerator(
            PostgresSQLNameTransformer(),
            hasDropCascadeMode(config),
            hasUnconstrainedNumber(config),
        )
    }
    override fun getSqlOperations(config: JsonNode): PostgresSqlOperations {
        return PostgresSqlOperations(hasDropCascadeMode(config))
    }

    override fun getGenerationHandler(): PostgresGenerationHandler {
        return PostgresGenerationHandler()
    }

    private fun hasDropCascadeMode(config: JsonNode): Boolean {
        val dropCascadeNode = config[DROP_CASCADE_OPTION]
        return dropCascadeNode != null && dropCascadeNode.asBoolean()
    }

    private fun hasUnconstrainedNumber(config: JsonNode): Boolean {
        val unconstrainedNumberNode = config[UNCONSTRAINED_NUMBER_OPTION]
        return unconstrainedNumberNode != null && unconstrainedNumberNode.asBoolean()
    }

    override fun getDestinationHandler(
        config: JsonNode,
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<PostgresState> {
        return PostgresDestinationHandler(
            databaseName,
            database,
            rawTableSchema,
            getGenerationHandler(),
        )
    }

    protected override fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<PostgresState>
    ): List<Migration<PostgresState>> {
        return java.util.List.of<Migration<PostgresState>>(
            PostgresRawTableAirbyteMetaMigration(database, databaseName),
            PostgresGenerationIdMigration(database, databaseName),
        )
    }

    override fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        return PostgresDataTransformer()
    }

    override val isV2Destination: Boolean
        get() = true

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(PostgresDestination::class.java)

        val DRIVER_CLASS: String = DatabaseDriver.POSTGRESQL.driverClassName

        const val DROP_CASCADE_OPTION = "drop_cascade"
        const val UNCONSTRAINED_NUMBER_OPTION = "unconstrained_number"

        @JvmStatic
        fun sshWrappedDestination(): Destination {
            return SshWrappedDestination(
                PostgresDestination(),
                JdbcUtils.HOST_LIST_KEY,
                JdbcUtils.PORT_LIST_KEY
            )
        }

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            addThrowableForDeinterpolation(PSQLException::class.java)
            val destination = sshWrappedDestination()
            LOGGER.info("starting destination: {}", PostgresDestination::class.java)
            IntegrationRunner(destination).run(args)
            LOGGER.info("completed destination: {}", PostgresDestination::class.java)
        }
    }
}
