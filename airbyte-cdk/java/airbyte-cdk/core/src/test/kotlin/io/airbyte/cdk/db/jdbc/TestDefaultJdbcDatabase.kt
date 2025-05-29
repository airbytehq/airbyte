/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import javax.sql.DataSource
import org.junit.jupiter.api.*
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

internal class TestDefaultJdbcDatabase {
    private val sourceOperations: JdbcSourceOperations = JdbcUtils.defaultSourceOperations
    private lateinit var dataSource: DataSource
    private lateinit var database: JdbcDatabase

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        val dbName = Strings.addRandomSuffix("db", "_", 10)

        val config = getConfig(PSQL_DB, dbName)
        val initScriptName = "init_$dbName.sql"
        val tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $dbName;")
        PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB)

        dataSource = getDataSourceFromConfig(config)
        database = DefaultJdbcDatabase(dataSource)
        database.execute(
            CheckedConsumer { connection: Connection ->
                connection
                    .createStatement()
                    .execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
                connection
                    .createStatement()
                    .execute(
                        "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                    )
            }
        )
    }

    @AfterEach
    @Throws(Exception::class)
    fun close() {
        DataSourceFactory.close(dataSource)
    }

    @Test
    @Throws(SQLException::class)
    fun testBufferedResultQuery() {
        val actual =
            database.bufferedResultSetQuery(
                { connection: Connection ->
                    connection.createStatement().executeQuery("SELECT * FROM id_and_name;")
                },
                { queryContext: ResultSet -> sourceOperations.rowToJson(queryContext) }
            )

        Assertions.assertEquals(RECORDS_AS_JSON, actual)
    }

    @Test
    @Throws(SQLException::class)
    fun testResultSetQuery() {
        database
            .unsafeResultSetQuery(
                { connection: Connection ->
                    connection.createStatement().executeQuery("SELECT * FROM id_and_name;")
                },
                { queryContext: ResultSet -> sourceOperations.rowToJson(queryContext) }
            )
            .use { actual -> Assertions.assertEquals(RECORDS_AS_JSON, actual.toList()) }
    }

    @Test
    @Throws(SQLException::class)
    fun testQuery() {
        val actual =
            database.queryJsons(
                { connection: Connection ->
                    connection.prepareStatement("SELECT * FROM id_and_name;")
                },
                { queryContext: ResultSet -> sourceOperations.rowToJson(queryContext) }
            )
        Assertions.assertEquals(RECORDS_AS_JSON, actual)
    }

    private fun getDataSourceFromConfig(config: JsonNode): DataSource {
        return DataSourceFactory.create(
            config[JdbcUtils.USERNAME_KEY].asText(),
            config[JdbcUtils.PASSWORD_KEY].asText(),
            DatabaseDriver.POSTGRESQL.driverClassName,
            String.format(
                DatabaseDriver.POSTGRESQL.urlFormatString,
                config[JdbcUtils.HOST_KEY].asText(),
                config[JdbcUtils.PORT_KEY].asInt(),
                config[JdbcUtils.DATABASE_KEY].asText()
            )
        )
    }

    private fun getConfig(psqlDb: PostgreSQLContainer<*>?, dbName: String): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, psqlDb!!.host)
                .put(JdbcUtils.PORT_KEY, psqlDb.firstMappedPort)
                .put(JdbcUtils.DATABASE_KEY, dbName)
                .put(JdbcUtils.USERNAME_KEY, psqlDb.username)
                .put(JdbcUtils.PASSWORD_KEY, psqlDb.password)
                .build()
        )
    }

    companion object {
        private val RECORDS_AS_JSON: List<JsonNode> =
            Lists.newArrayList(
                Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
                Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
                Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash"))
            )

        private lateinit var PSQL_DB: PostgreSQLContainer<Nothing>

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_DB = PostgreSQLContainer<Nothing>("postgres:13-alpine")
            PSQL_DB.start()
        }

        @JvmStatic
        @AfterAll
        fun cleanUp(): Unit {
            PSQL_DB.close()
        }
    }
}
