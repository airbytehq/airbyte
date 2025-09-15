/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName

interface DirectLoadSqlGenerator {
    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): Sql

    /**
     * Replace the targetTable with the sourceTable. This is typically something like
     * ```sql
     * DROP TABLE IF EXISTS target;
     * ALTER TABLE source RENAME TO target;
     * ```
     */
    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ): Sql

    /**
     * Copy all records from sourceTable to targetTable. May assume that both tables exist, and have
     * schemas which match the expected schema, i.e.
     * [DirectLoadTableNativeOperations.ensureSchemaMatches] was invoked on both tables.
     *
     * MUST NOT assume that the columns are in the same order in both tables.
     */
    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): Sql

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): Sql

    fun dropTable(tableName: TableName): Sql
}
