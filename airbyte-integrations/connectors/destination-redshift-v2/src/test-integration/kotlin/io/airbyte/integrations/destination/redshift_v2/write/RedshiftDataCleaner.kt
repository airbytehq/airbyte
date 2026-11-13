/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import io.airbyte.cdk.load.test.util.DestinationCleaner
import javax.sql.DataSource

object RedshiftDataCleaner : DestinationCleaner {
    private var dataSourceProvider: (() -> DataSource)? = null
    private var testNamespaces: List<String> = emptyList()

    fun configure(dataSourceProvider: () -> DataSource, testNamespaces: List<String>) {
        this.dataSourceProvider = dataSourceProvider
        this.testNamespaces = testNamespaces
    }

    override fun cleanup() {
        val provider = dataSourceProvider ?: return
        val namespaces =
            testNamespaces.ifEmpty {
                return
            }

        provider().connection.use { connection ->
            namespaces.forEach { namespace ->
                // Find all tables in the namespace
                val sql =
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '$namespace'
                """.trimIndent()

                val tablesToDrop = mutableListOf<String>()
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery(sql)
                    while (rs.next()) {
                        tablesToDrop.add(rs.getString("table_name"))
                    }
                }

                // Drop each table
                tablesToDrop.forEach { tableName ->
                    try {
                        connection.createStatement().use { statement ->
                            statement.execute(
                                """DROP TABLE IF EXISTS "$namespace"."$tableName" CASCADE"""
                            )
                        }
                    } catch (e: Exception) {
                        // Ignore errors during cleanup
                    }
                }

                // Optionally drop the schema
                try {
                    connection.createStatement().use { statement ->
                        statement.execute("""DROP SCHEMA IF EXISTS "$namespace" CASCADE""")
                    }
                } catch (e: Exception) {
                    // Ignore errors during cleanup
                }
            }
        }
    }
}
