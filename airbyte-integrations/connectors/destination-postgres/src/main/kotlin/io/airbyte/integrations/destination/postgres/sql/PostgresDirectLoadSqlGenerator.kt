/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import jakarta.inject.Singleton

@Singleton
class PostgresDirectLoadSqlGenerator {

    @Suppress("UNUSED_PARAMETER")
    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): String = TODO("PostgresDirectLoadSqlGenerator.createTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ): String = TODO("PostgresDirectLoadSqlGenerator.overwriteTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String = TODO("PostgresDirectLoadSqlGenerator.copyTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String = TODO("PostgresDirectLoadSqlGenerator.upsertTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun dropTable(tableName: TableName): String =
        TODO("PostgresDirectLoadSqlGenerator.dropTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun countTable(tableName: TableName): String =
        TODO("PostgresDirectLoadSqlGenerator.countTable not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun createNamespace(namespace: String): String =
        TODO("PostgresDirectLoadSqlGenerator.createNamespace not yet implemented")

    @Suppress("UNUSED_PARAMETER")
    fun getGenerationId(tableName: TableName): String =
        TODO("PostgresDirectLoadSqlGenerator.getGenerationId not yet implemented")

    fun showColumns(tableName: TableName): String =
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = '${tableName.namespace}'
          AND table_name = '${tableName.name}'
        ORDER BY ordinal_position
        """.trimIndent()

    fun copyFromCsv(tableName: TableName, filePath: String): String =
        """
        COPY "${tableName.namespace}"."${tableName.name}"
        FROM '$filePath'
        WITH (FORMAT csv)
        """.trimIndent()
}
