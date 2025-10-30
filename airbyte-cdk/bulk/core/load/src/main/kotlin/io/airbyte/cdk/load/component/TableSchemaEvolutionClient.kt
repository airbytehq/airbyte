/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName

/**
 * Database-specific schema evolution operations.
 *
 * This interface encapsulates schema evolution and synchronization operations. Implementations
 * handle the details of schema migration, including type compatibility, column mapping, constraint
 * management, and database-specific quirks when aligning source stream schemas with destination
 * table structures.
 *
 * These operations typically involve:
 * - Schema introspection and comparison
 * - Type system translation between source and destination
 * - Safe schema evolution strategies (adding/modifying columns)
 * - Handling of database-specific constraints and limitations
 * - Preservation of data integrity during schema changes
 *
 * @see TableOperationsClient for standard SQL-based table operations
 */
interface TableSchemaEvolutionClient<AdditionalSchemaInfo, AdditionalSchemaInfoDiff> {
    /**
     * Ensures the destination table schema matches the expected stream schema through introspection
     * and reconciliation.
     *
     * This method performs a comprehensive schema synchronization process:
     * 1. Introspects the current table schema if it exists
     * 2. Compares it against the expected stream schema
     * 3. Identifies required schema modifications (new columns, type changes, constraint updates)
     * 4. Applies safe schema evolution strategies specific to the database implementation
     * 5. Handles edge cases like incompatible type changes or constraint violations
     *
     * The implementation must handle various complexities:
     * - Column name normalization and mapping between source and destination naming conventions
     * - Type system differences between the source platform and destination database
     * - Nullable vs non-nullable column conversions
     * - Primary key and unique constraint management during deduplication mode changes
     * - Database-specific limitations (e.g., maximum column count, type restrictions)
     * - Backward compatibility when schema evolution would break existing data
     *
     * @param stream The source stream containing schema definition and sync mode configuration
     * @param tableName The destination table to be synchronized
     * @param columnNameMapping Mapping between logical column names and physical database column
     * names
     * @throws io.airbyte.cdk.ConfigErrorException if the table exists but is incompatible with
     * Airbyte's requirements
     * @throws IllegalStateException if schema evolution cannot be safely performed
     */
    suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
    ) {
        val (actualSchema, actualAdditionalInfo) = discoverSchema(tableName)
        val (expectedSchema, expectedAdditionalInfo) = computeSchema(stream, columnNameMapping)
        val schemaDiff = actualSchema.diff(expectedSchema)
        val additionalInfoDiff = diff(actualAdditionalInfo, expectedAdditionalInfo)
        applySchemaDiff(
            tableName,
            expectedSchema,
            expectedAdditionalInfo,
            schemaDiff,
            additionalInfoDiff
        )
    }

    suspend fun discoverSchema(tableName: TableName): Pair<TableSchema, AdditionalSchemaInfo> {
        throw NotImplementedError()
    }
    fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): Pair<TableSchema, AdditionalSchemaInfo> {
        throw NotImplementedError()
    }
    fun diff(
        actualSchemaInfo: AdditionalSchemaInfo,
        expectedSchemaInfo: AdditionalSchemaInfo
    ): AdditionalSchemaInfoDiff {
        throw NotImplementedError()
    }
    suspend fun applySchemaDiff(
        tableName: TableName,
        expectedSchema: TableSchema,
        expectedAdditionalInfo: AdditionalSchemaInfo,
        diff: TableSchemaDiff,
        additionalSchemaInfoDiff: AdditionalSchemaInfoDiff
    ) {
        throw NotImplementedError()
    }
}

data class TableSchema(val columns: Map<String, ColumnType>) {
    /** Generate a diff which, when applied to `this`, will result in [other]. */
    fun diff(other: TableSchema): TableSchemaDiff {
        TODO()
    }
}

data class ColumnType(
    val type: String,
    val nullable: Boolean,
) {
    fun nullClause() =
        if (nullable) {
            ""
        } else {
            "NOT NULL"
        }

    /** Generate a string like "INTEGER NOT NULL" or "VARCHAR". Useful for SQL-ish destinations. */
    fun typeDeclaration() = "$type ${nullClause()}"
}

data class TableSchemaDiff(
    val columnsToAdd: Map<String, ColumnType>,
    val columnsToDrop: Set<String>,
    val columnsToChange: Map<String, ColumnTypeChange>,
    val columnsToRetain: Set<String>,
) {
    fun isNoop() = columnsToAdd.isEmpty() && columnsToDrop.isEmpty() && columnsToChange.isEmpty()
}

data class ColumnTypeChange(
    val originalType: ColumnType,
    val newType: ColumnType,
)
