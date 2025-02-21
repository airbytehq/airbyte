/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import java.sql.Connection
import java.sql.DriverManager
import java.sql.SQLException
import java.util.UUID

class SapHanaTestDatabase(
    val host: String,
    val port: Int,
    val username: String,
    val password: String
) {
    var connection: Connection? = null
        private set

    @Throws(SQLException::class)
    fun connect() {
        val url = "jdbc:sap://$host:$port"
        connection = DriverManager.getConnection(url, username, password)
    }

    @Throws(SQLException::class)
    fun disconnect() {
        connection?.takeIf { !it.isClosed }?.close()
    }

    @Throws(SQLException::class)
    fun execute(sql: String): Boolean {
        connection?.createStatement().use { statement ->
            return statement?.execute(sql) ?: false
        }
    }

    fun getRandomSchemaName(): String {
        return "SCHEMA_" + UUID.randomUUID().toString().replace("-", "").uppercase()
    }

    fun getRandomTableName(): String {
        return "TABLE_" + UUID.randomUUID().toString().replace("-", "").uppercase()
    }

    fun getRandomSchemaNames(x: Int): List<String> {
        return List(x) { getRandomSchemaName() }
    }

    fun getRandomTableNames(x: Int): List<String> {
        return List(x) { getRandomTableName() }
    }
}
