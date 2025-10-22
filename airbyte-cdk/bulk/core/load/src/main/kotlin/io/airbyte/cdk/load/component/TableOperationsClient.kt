/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName

/**
 * Client interface for database table operations.
 *
 * Provides a standard set of operations for managing database namespaces, tables, and data
 * manipulation across different database implementations. Implementations should handle
 * database-specific SQL generation and execution while maintaining consistent behavior across the
 * interface methods.
 */
interface TableOperationsClient {

    /** Tests database connectivity. */
    suspend fun ping() = Unit

    /** Creates a new namespace (database/schema). */
    suspend fun createNamespace(namespace: String) = Unit

    /** Checks if a namespace exists. */
    suspend fun namespaceExists(namespace: String) = false

    /** Drops a namespace if it exists. */
    suspend fun dropNamespace(namespace: String) = Unit

    /** Creates a table with the given schema and column mapping. */
    suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
        isFinalTable: Boolean = true
    )

    /** Checks if a table exists. */
    suspend fun tableExists(table: TableName) = false

    /** Drops a table. */
    suspend fun dropTable(tableName: TableName)

    /** Returns the row count of a table, or null if the table doesn't exist. */
    suspend fun countTable(tableName: TableName): Long? = null

    /** Returns generation ID from an arbitrary record in the table (0 if null). */
    suspend fun getGenerationId(tableName: TableName): Long = 0

    /** Replaces table — target table becomes source table and source table is dropped */
    suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    /** Inserts records from source table to target table */
    suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    /** Upserts records from source table to target table */
    suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    /**
     * TEST ONLY: Inserts records directly into a table for test verification. Do not use in
     * production code - use appropriate streaming mechanisms instead.
     */
    suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) = Unit

    /**
     * TEST ONLY: Reads all records from a table for test verification. Do not use in production
     * code - this loads entire table into memory.
     */
    suspend fun readTable(table: TableName): List<Map<String, Any>> = listOf()
}
