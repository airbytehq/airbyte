/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName

/**
 * Database-agnostic interface for table and namespace operations.
 *
 * Provides CRUD operations for managing database namespaces (schemas/databases) and tables across
 * different database implementations. Implementations handle database-specific SQL generation and
 * execution while maintaining consistent behavior.
 *
 * Used by [StreamLoader] implementations to create tables, manage data, and perform operations like
 * upserts and overwrites during the loading process.
 */
interface TableOperationsClient {

    /**
     * Creates a new namespace (database or schema) in the destination.
     *
     * @param namespace The namespace name to create
     */
    suspend fun createNamespace(namespace: String) = Unit

    /**
     * Checks if a namespace exists in the destination.
     *
     * @param namespace The namespace name to check
     * @return True if the namespace exists, false otherwise
     */
    suspend fun namespaceExists(namespace: String) = false

    /**
     * Creates a table with the specified schema and column mapping.
     *
     * @param stream The stream configuration containing schema information
     * @param tableName The name of the table to create
     * @param columnNameMapping Mapping from logical column names to physical column names
     * @param replace If true, drop and recreate the table if it already exists
     */
    suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    )

    /**
     * Checks if a table exists in the destination.
     *
     * @param table The table name to check
     * @return True if the table exists, false otherwise
     */
    suspend fun tableExists(table: TableName) = false

    /**
     * Drops a table from the destination.
     *
     * @param tableName The name of the table to drop
     */
    suspend fun dropTable(tableName: TableName)

    /**
     * Returns the number of rows in a table.
     *
     * @param tableName The name of the table to count
     * @return The row count, or null if the table doesn't exist
     */
    suspend fun countTable(tableName: TableName): Long? = null

    /**
     * Returns the generation ID from an arbitrary record in the table.
     *
     * Generation IDs are used to track data versions across sync operations.
     *
     * @param tableName The name of the table to query
     * @return The generation ID, or 0 if the table is empty or doesn't have generation tracking
     */
    suspend fun getGenerationId(tableName: TableName): Long = 0

    /**
     * Atomically replaces the target table with the source table.
     *
     * After this operation, the target table contains the source table's data, and the source table
     * is dropped. This is typically used to promote staging tables to final tables.
     *
     * @param sourceTableName The table to promote
     * @param targetTableName The table to replace
     */
    suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    /**
     * Copies all records from the source table to the target table.
     *
     * Performs an INSERT operation without deduplication. Both tables must exist and have
     * compatible schemas.
     *
     * @param columnNameMapping Mapping from logical to physical column names
     * @param sourceTableName The table to copy from
     * @param targetTableName The table to copy to
     */
    suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    /**
     * Upserts records from the source table into the target table.
     *
     * Performs an INSERT or UPDATE operation based on primary keys. Existing records with matching
     * keys are updated, new records are inserted. Used for incremental syncs and deduplication.
     *
     * @param stream The stream configuration containing primary key information
     * @param columnNameMapping Mapping from logical to physical column names
     * @param sourceTableName The table containing new/updated records
     * @param targetTableName The table to upsert into
     */
    suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )
}
