/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.TableName

/** Operations which aren't easily represented as a sequence of SQL statements. */
interface DirectLoadTableNativeOperations {
    /**
     * Detect the existing schema of the table, and alter it if needed to match the correct schema.
     */
    suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
    )

    /**
     * Return the generation ID of an arbitrary record from the table. May assume the table exists
     * and is nonempty.
     *
     * If an existing record has null generation, treat that record as belonging to generation 0.
     * These records predate the refreshes project.
     */
    suspend fun getGenerationId(tableName: TableName): Long
}

/**
 * Operations which can be handled by an underlying [DatabaseHandler] executing SQL statements from
 * a [DirectLoadSqlGenerator].
 *
 * Destinations MAY choose to implement their own version of this class, if they want finer control,
 * but in general, the [DefaultDirectLoadTableSqlOperations] is a reasonable implementation.
 */
interface DirectLoadTableSqlOperations {
    suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    )

    suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    )

    suspend fun dropTable(tableName: TableName)
}

open class DefaultDirectLoadTableSqlOperations(
    private val generator: DirectLoadSqlGenerator,
    private val handler: DatabaseHandler,
) : DirectLoadTableSqlOperations {
    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        handler.execute(
            generator.createTable(stream, tableName, columnNameMapping, replace = replace)
        )
    }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        handler.execute(
            generator.overwriteTable(
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )
        )
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        handler.execute(
            generator.copyTable(
                columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        handler.execute(
            generator.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        handler.execute(generator.dropTable(tableName))
    }
}
