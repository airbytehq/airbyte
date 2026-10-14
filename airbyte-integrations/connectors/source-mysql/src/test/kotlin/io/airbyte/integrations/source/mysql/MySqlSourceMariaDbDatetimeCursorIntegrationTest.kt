/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.JdbcSelectQuerier
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.util.Jsons
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

class MySqlSourceMariaDbDatetimeCursorIntegrationTest {
    @Test
    fun testInclusiveDateTimeCursorReturnsRowAtCursor() {
        val rows =
            executeQuery(
                LesserOrEqual(
                    EmittedField("modified", LocalDateTimeFieldType),
                    Jsons.textNode("2026-04-14T16:27:33.726846"),
                )
            )

        assertEquals(1, rows.size)
    }

    @Test
    fun testGreaterDateTimeCursorReturnsRowAfterCursor() {
        val rows =
            executeQuery(
                Greater(
                    EmittedField("modified", LocalDateTimeFieldType),
                    Jsons.textNode("2026-04-14T16:27:33.726845"),
                )
            )

        assertEquals(1, rows.size)
    }

    private fun executeQuery(clause: WhereClauseNode): List<SelectQuerier.ResultRow> {
        val id = EmittedField("id", IntFieldType)
        val modified = EmittedField("modified", LocalDateTimeFieldType)
        val query: SelectQuery =
            MySqlSourceOperations()
                .generate(
                    SelectQuerySpec(
                        SelectColumns(id, modified),
                        From("tbl", "test"),
                        Where(clause),
                    )
                )

        return JdbcSelectQuerier(connectionFactory).executeQuery(query).use { result ->
            result.asSequence().toList()
        }
    }

    companion object {
        private lateinit var dbContainer: MySQLContainer<*>
        private lateinit var connectionFactory: JdbcConnectionFactory

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = MySqlContainerFactory.exclusive(imageName = "mariadb:10.11")
            val config =
                MySqlContainerFactory.config(dbContainer).apply {
                    setEncryptionValue(EncryptionPreferred)
                }
            connectionFactory =
                JdbcConnectionFactory(MySqlSourceConfigurationFactory().make(config))

            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE test.tbl (id INT PRIMARY KEY, modified DATETIME(6))")
                    stmt.execute(
                        "INSERT INTO test.tbl (id, modified) " +
                            "VALUES (1, '2026-04-14 16:27:33.726846')"
                    )
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun stopTestContainer() {
            if (::dbContainer.isInitialized) {
                dbContainer.stop()
            }
        }
    }
}
