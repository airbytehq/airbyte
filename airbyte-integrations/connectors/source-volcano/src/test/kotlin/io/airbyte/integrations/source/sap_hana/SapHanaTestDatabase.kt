/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import java.sql.Connection
import java.sql.DriverManager
import java.sql.ResultSet
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

    @Throws(SQLException::class)
    fun executeQuery(sql: String): ResultSet? {
        return connection?.createStatement()?.executeQuery(sql)
    }

    /** Verifies that a table exists in the specified schema. */
    @Throws(SQLException::class)
    fun verifyTableExists(schemaName: String, tableName: String): Boolean {
        executeQuery(
                "SELECT COUNT(*) FROM SYS.TABLES WHERE SCHEMA_NAME = '$schemaName' AND TABLE_NAME = '$tableName'"
            )
            ?.use { resultSet ->
                return if (resultSet.next()) {
                    resultSet.getInt(1) > 0
                } else {
                    false
                }
            }
        return false
    }

    /** Verifies that a trigger exists in the specified schema. */
    @Throws(SQLException::class)
    fun verifyTriggerExists(schemaName: String, triggerName: String): Boolean {
        executeQuery(
                "SELECT COUNT(*) FROM SYS.TRIGGERS WHERE SCHEMA_NAME = '$schemaName' AND TRIGGER_NAME = '$triggerName'"
            )
            ?.use { resultSet ->
                return if (resultSet.next()) {
                    resultSet.getInt(1) > 0
                } else {
                    false
                }
            }
        return false
    }

    /** Verifies that data exists in the specified table. */
    @Throws(SQLException::class)
    fun verifyDataExists(schemaName: String, tableName: String): Boolean {
        executeQuery("SELECT COUNT(*) FROM \"$schemaName\".\"$tableName\"")?.use { resultSet ->
            return if (resultSet.next()) {
                resultSet.getInt(1) > 0
            } else {
                false
            }
        }
        return false
    }

    /** Verifies that a schema exists. */
    @Throws(SQLException::class)
    fun verifySchemaExists(schemaName: String): Boolean {
        executeQuery("SELECT COUNT(*) FROM SYS.SCHEMAS WHERE SCHEMA_NAME = '$schemaName'")?.use {
            resultSet ->
            return if (resultSet.next()) {
                resultSet.getInt(1) > 0
            } else {
                false
            }
        }
        return false
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
