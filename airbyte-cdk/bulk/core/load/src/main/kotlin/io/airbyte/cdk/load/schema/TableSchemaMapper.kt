/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName

/** Transforms input schema elements to destination-specific naming and type conventions. */
interface TableSchemaMapper {
    /**
     * Converts a stream descriptor to the final destination table name.
     *
     * @param desc The stream descriptor containing namespace and name information
     * @return The mapped final table name in the destination system
     */
    fun toFinalTableName(desc: DestinationStream.Descriptor): TableName

    /**
     * Generates a temporary table name based on the provided final table name. Temporary tables are
     * typically used before data is moved to final tables to avoid data downtime.
     *
     * @param tableName The final table name to base the temporary name on
     * @return The temporary table name
     */
    fun toTempTableName(tableName: TableName): TableName

    /**
     * Transforms a column name from the input schema to comply with destination naming conventions.
     * This may include handling special characters, case transformations, or length limitations.
     *
     * @param name The original column name from the input schema
     * @return The destination-compatible column name
     */
    fun toColumnName(name: String): String

    /**
     * Converts an Airbyte field type to the corresponding destination-specific column type. This
     * handles mapping of data types from Airbyte's type system to the destination database's type
     * system.
     *
     * @param fieldType The Airbyte field type to convert
     * @return The destination-specific column type representation
     */
    fun toColumnType(fieldType: FieldType): ColumnType

    /**
     * Performs any final transformations on the complete table schema before it's used in the
     * destination. By default, returns the schema unchanged. Override to apply destination-specific
     * schema modifications.
     *
     * @param tableSchema The complete stream table schema
     * @return The finalized schema ready for use in the destination
     */
    fun toFinalSchema(tableSchema: StreamTableSchema) = tableSchema

    /**
     * Determines if two column names conflict according to destination-specific rules. By default,
     * performs case-insensitive comparison. Override for different conflict detection logic.
     *
     * @param a First column name
     * @param b Second column name
     * @return true if the column names conflict, false otherwise
     */
    fun colsConflict(a: String, b: String): Boolean = a.equals(b, ignoreCase = true)
}
