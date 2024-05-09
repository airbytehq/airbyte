/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import java.sql.Connection
import java.sql.DriverManager
import java.sql.SQLException
import java.util.*

/**
 * This class as been added in order to be able to save the connection in a test. It was found that
 * the [javax.sql.DataSource] close method wasn't propagating the connection properly. It shouldn't
 * be needed in our application code.
 */
object ConnectionFactory {
    /**
     * Construct a new [Connection] instance using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param connectionProperties The extra properties to add to the connection.
     * @param jdbcConnectionString The JDBC connection string.
     * @return The configured [Connection]
     */
    @JvmStatic
    fun create(
        username: String?,
        password: String?,
        connectionProperties: Map<String?, String?>,
        jdbcConnectionString: String?
    ): Connection {
        try {
            val properties = Properties()
            properties["user"] = username
            properties["password"] = password
            connectionProperties.forEach { (k: String?, v: String?) -> properties[k] = v }

            return DriverManager.getConnection(jdbcConnectionString, properties)
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }
}
