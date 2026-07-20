/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping

/**
 * Client interface for database table operations.
 *
 * Provides a standard set of operations for managing database namespaces, tables, and data
 * manipulation across different database implementations. Implementations should handle
 * database-specific SQL generation and execution while maintaining consistent behavior across the
 * interface methods.
 */
interface TableOperationsClient {

    /** Creates a new namespace (database/schema). */
    suspend fun createNamespace(namespace: String) = Unit

    /** Checks if a namespace exists. */
    suspend fun namespaceExists(namespace: String) = false

    /** Creates a table with the given schema and column mapping. */
    suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    )

    /**
     * Creates a temporary table.Override in connectors where temp tables need different handling
     * (e.g. skipping stage creation, using transient storage, etc.).
     */
    suspend fun createTempTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) = createTable(stream, tableName, columnNameMapping, replace)

    /** Checks if a table exists. */
    suspend fun tableExists(table: TableName) = false

    /** Drops a table. */
    suspend fun dropTable(tableName: TableName)

    /** Returns the row count of a table, or null if the table doesn't exist. */
    suspend fun countTable(tableName: TableName): Long? = null

    /**
     * Returns whether the table contains no rows.
     *
     * The default implementation derives emptiness from [countTable]. Implementations should
     * override this with a cheaper existence check (e.g. `SELECT EXISTS(SELECT 1 FROM <table>)`)
     * when the underlying database can answer the yes/no "is this table empty" question without a
     * full `COUNT(*)`, which can be prohibitively expensive on large tables. Callers are expected
     * to confirm the table exists (via [tableExists]) before relying on this result.
     */
    suspend fun tableIsEmpty(tableName: TableName): Boolean = countTable(tableName) == 0L

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
}
