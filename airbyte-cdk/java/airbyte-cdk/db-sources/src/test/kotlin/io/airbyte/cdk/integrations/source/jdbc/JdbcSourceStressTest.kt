/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcStressTest
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper.runSqlScript
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.JDBCType
import java.util.*
import java.util.function.Supplier
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Disabled
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

private val LOGGER = KotlinLogging.logger {}

/**
 * Runs the stress tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
@Disabled
internal class JdbcSourceStressTest : JdbcStressTest() {
    private var config: JsonNode? = null

    @BeforeEach
    @Throws(Exception::class)
    override fun setup() {
        val schemaName = Strings.addRandomSuffix("db", "_", 10)

        config =
            Jsons.jsonNode(
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.HOST_KEY, PSQL_DB.host)
                    .put(JdbcUtils.PORT_KEY, PSQL_DB.firstMappedPort)
                    .put(JdbcUtils.DATABASE_KEY, schemaName)
                    .put(JdbcUtils.USERNAME_KEY, PSQL_DB.username)
                    .put(JdbcUtils.PASSWORD_KEY, PSQL_DB.password)
                    .build()
            )

        val initScriptName = "init_$schemaName.sql"
        val tmpFilePath =
            IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $schemaName;")
        runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB)

        super.setup()
    }

    override val defaultSchemaName = Optional.of("public")

    override fun getSource(): AbstractJdbcSource<JDBCType> {
        return PostgresTestSource()
    }

    override fun getConfig(): JsonNode {
        return config!!
    }

    override val driverClass = PostgresTestSource.DRIVER_CLASS

    private class PostgresTestSource :
        AbstractJdbcSource<JDBCType>(
            DRIVER_CLASS,
            Supplier { AdaptiveStreamingQueryConfig() },
            JdbcUtils.defaultSourceOperations
        ),
        Source {
        override fun toDatabaseConfig(config: JsonNode): JsonNode {
            val configBuilder =
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.USERNAME_KEY, config[JdbcUtils.USERNAME_KEY].asText())
                    .put(
                        JdbcUtils.JDBC_URL_KEY,
                        String.format(
                            DatabaseDriver.POSTGRESQL.urlFormatString,
                            config[JdbcUtils.HOST_KEY].asText(),
                            config[JdbcUtils.PORT_KEY].asInt(),
                            config[JdbcUtils.DATABASE_KEY].asText()
                        )
                    )

            if (config.has(JdbcUtils.PASSWORD_KEY)) {
                configBuilder.put(JdbcUtils.PASSWORD_KEY, config[JdbcUtils.PASSWORD_KEY].asText())
            }

            return Jsons.jsonNode(configBuilder.build())
        }

        override val excludedInternalNameSpaces =
            setOf("information_schema", "pg_catalog", "pg_internal", "catalog_history")

        companion object {

            val DRIVER_CLASS: String = DatabaseDriver.POSTGRESQL.driverClassName

            @Throws(Exception::class)
            @JvmStatic
            fun main(args: Array<String>) {
                val source: Source = PostgresTestSource()
                LOGGER.info { "starting source: ${PostgresTestSource::class.java}" }
                IntegrationRunner(source).run(args)
                LOGGER.info { "completed source: ${PostgresTestSource::class.java}" }
            }
        }
    }

    companion object {
        private lateinit var PSQL_DB: PostgreSQLContainer<Nothing>

        @BeforeAll
        @JvmStatic
        fun init() {
            PSQL_DB = PostgreSQLContainer("postgres:13-alpine")
            PSQL_DB.start()
        }

        @AfterAll
        @JvmStatic
        fun cleanUp() {
            PSQL_DB.close()
        }
    }
}
