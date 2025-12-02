/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.PostgresUtils.getLsn
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import java.sql.Connection
import java.sql.SQLException
import javax.sql.DataSource
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

internal class PostgresUtilsTest {
    private var dataSource: DataSource? = null

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        val dbName = Strings.addRandomSuffix("db", "_", 10)

        val config = getConfig(PSQL_DB, dbName)

        val initScriptName = "init_$dbName.sql"
        val tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $dbName;")
        PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB)

        dataSource =
            create(
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

        val defaultJdbcDatabase: JdbcDatabase = DefaultJdbcDatabase(dataSource!!)

        defaultJdbcDatabase.execute(
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

    @Test
    @Throws(SQLException::class)
    fun testGetLsn() {
        val database: JdbcDatabase = DefaultJdbcDatabase(dataSource!!)

        val lsn1 = getLsn(database)
        Assertions.assertNotNull(lsn1)
        Assertions.assertTrue(lsn1.asLong() > 0)

        database.execute(
            CheckedConsumer { connection: Connection ->
                connection
                    .createStatement()
                    .execute(
                        "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                    )
            }
        )

        val lsn2 = getLsn(database)
        Assertions.assertNotNull(lsn2)
        Assertions.assertTrue(lsn2.asLong() > 0)

        Assertions.assertTrue(lsn1.compareTo(lsn2) < 0, "returned lsns are not ascending.")
    }

    companion object {
        var PSQL_DB: PostgreSQLContainer<Nothing> =
            PostgreSQLContainer<Nothing>("postgres:13-alpine")

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_DB.start()
        }
    }
}
