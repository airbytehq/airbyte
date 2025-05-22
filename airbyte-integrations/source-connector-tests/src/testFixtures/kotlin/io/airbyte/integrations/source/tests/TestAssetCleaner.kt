/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tests

import io.github.oshai.kotlinlogging.KotlinLogging

/**
 * Interface for cleaning up old test assets. Implementations of this interface can provide cleanup
 * logic for test assets that might be left behind from previous test runs.
 */
interface TestAssetCleaner {
    /**
     * Cleans up old test assets from previous test runs. This might include tables, schemas, or
     * other database objects that follow a specific naming pattern used by tests and have
     * timestamps before the current time.
     */
    fun cleanupOldTestAssets()
}

/**
 * No-op implementation of TestAssetCleaner. This can be used as a default when cleanup is not
 * needed.
 */
class NoOpTestAssetCleaner : TestAssetCleaner {
    override fun cleanupOldTestAssets() {
        // Do nothing
    }
}

/**
 * Implementation of TestAssetCleaner for remote JDBC connections. This cleans up test assets
 * (tables, namespaces) from previous test runs by querying database metadata and identifying test
 * objects by their naming convention.
 */
class RemoteJdbcTestAssetCleaner(
    private val testDbInstance: RemoteJdbcTestInstance,
    private val sqlDialect: SqlDialect
) : TestAssetCleaner {

    private val log = KotlinLogging.logger {}
    private val currentTimestamp = System.currentTimeMillis()

    override fun cleanupOldTestAssets() {
        log.info { "Cleaning up old test assets from previous runs" }

        cleanupOldTestTables()
        cleanupOldTestNamespaces()
    }

    private fun cleanupOldTestTables() {
        // Query table metadata to find test tables
        val allTestTables = findAllTestTables()

        for ((namespace, tables) in allTestTables) {
            for (table in tables) {
                // Extract timestamp from table name
                val tableTimestamp = extractTimestampFromName(table, BaseConnectorTest.TABLE_PREFIX)

                // Only drop tables created before current test run
                if (tableTimestamp < currentTimestamp) {
                    val dropQuery = sqlDialect.buildDropTableQuery(namespace, table)
                    log.info { "Dropping old test table: $namespace.$table" }
                    testDbInstance.executeUpdate(dropQuery)
                }
            }
            val namespaceTimestamp =
                extractTimestampFromName(namespace, BaseConnectorTest.NAMESPACE_PREFIX)

            // Only drop tables created before current test run
            if (namespaceTimestamp < currentTimestamp) {
                val dropQuery = sqlDialect.buildDropNamespaceQuery(namespace)
                log.info { "Dropping old test namespace: $namespace" }
                testDbInstance.executeUpdate(dropQuery)
            }
        }
    }

    private fun cleanupOldTestNamespaces() {
        // Query namespace metadata to find test namespaces
        val testNamespaces = findAllTestNamespaces()

        for (namespace in testNamespaces) {
            // Extract timestamp from namespace name
            val timestamp = extractTimestampFromName(namespace, BaseConnectorTest.NAMESPACE_PREFIX)

            // Only drop namespaces created before current test run
            if (timestamp < currentTimestamp) {
                val dropQuery = sqlDialect.buildDropNamespaceQuery(namespace)
                log.info { "Dropping old test namespace: $namespace" }
                testDbInstance.executeUpdate(dropQuery)
            }
        }
    }

    /** Finds all test tables in the database. Returns a map of namespace to list of table names. */
    private fun findAllTestTables(): Map<String, List<String>> {
        val result = mutableMapOf<String, MutableList<String>>()

        val query = sqlDialect.buildFindAllTablesQuery()
        val queryResult = testDbInstance.executeReadQuery(query)

        for (row in queryResult.rows) {
            val namespace = row[sqlDialect.getNamespaceMetaFieldName()]?.toString() ?: continue
            val tableName = row[sqlDialect.getTableMetaFieldName()]?.toString() ?: continue

            if (tableName.startsWith(BaseConnectorTest.TABLE_PREFIX)) {
                result.getOrPut(namespace) { mutableListOf() }.add(tableName)
            }
        }

        return result
    }

    /** Finds all test namespaces in the database. Returns a list of namespace names. */
    private fun findAllTestNamespaces(): List<String> {
        val result = mutableListOf<String>()

        val query = sqlDialect.buildFindAllNamespacesQuery()
        val queryResult = testDbInstance.executeReadQuery(query)

        for (row in queryResult.rows) {
            val namespace = row[sqlDialect.getNamespaceMetaFieldName()]?.toString() ?: continue

            if (namespace.startsWith(BaseConnectorTest.NAMESPACE_PREFIX)) {
                result.add(namespace)
            }
        }
        return result
    }

    private fun extractTimestampFromName(name: String, prefix: String): Long {
        return try {
            val timestampStr = name.substring(prefix.length)
            timestampStr.toLong()
        } catch (e: Exception) {
            // If we can't extract a valid timestamp, leave it as is
            Long.MAX_VALUE
        }
    }
}
