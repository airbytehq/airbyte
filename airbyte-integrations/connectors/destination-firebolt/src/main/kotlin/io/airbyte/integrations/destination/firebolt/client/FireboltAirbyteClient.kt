/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.client

import com.zaxxer.hikari.HikariDataSource
import jakarta.inject.Singleton
import java.sql.Connection

/** JDBC client for executing SQL against Firebolt. */
@Singleton
class FireboltAirbyteClient(private val dataSource: HikariDataSource) {

    /** Execute a single SQL statement. */
    fun execute(sql: String) {
        dataSource.connection.use { conn: Connection ->
            conn.createStatement().use { stmt ->
                stmt.execute(sql)
            }
        }
    }

    /** Execute a query and return the first column of the first row as a boolean. */
    fun queryBoolean(sql: String): Boolean {
        dataSource.connection.use { conn: Connection ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    return if (rs.next()) rs.getBoolean(1) else false
                }
            }
        }
    }

    /** Execute a query and return the first column of the first row as a Long. */
    fun queryLong(sql: String): Long? {
        dataSource.connection.use { conn: Connection ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    return if (rs.next()) rs.getLong(1) else null
                }
            }
        }
    }

    /** Upload raw bytes to S3. Not yet implemented. */
    fun uploadToS3(bucket: String, key: String, bytes: ByteArray) {
        TODO("S3 upload implementation pending")
    }

    /** Delete an S3 object. Not yet implemented. */
    fun deleteFromS3(bucket: String, key: String) {
        TODO("S3 delete implementation pending")
    }
}
