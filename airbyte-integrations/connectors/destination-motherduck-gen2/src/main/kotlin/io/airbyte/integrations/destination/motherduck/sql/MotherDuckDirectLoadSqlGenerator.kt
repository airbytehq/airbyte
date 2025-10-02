package io.airbyte.integrations.destination.motherduck.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import jakarta.inject.Singleton

@Singleton
class MotherDuckDirectLoadSqlGenerator {

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) FROM ${fullyQualifiedName(tableName)}"
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\""
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        val createOrReplace = if (replace) "CREATE OR REPLACE" else "CREATE"
        return "$createOrReplace TABLE ${fullyQualifiedName(tableName)} (_placeholder TEXT)"
    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return "INSERT INTO ${fullyQualifiedName(targetTableName)} SELECT * FROM ${fullyQualifiedName(sourceTableName)}"
    }

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return "INSERT INTO ${fullyQualifiedName(targetTableName)} SELECT * FROM ${fullyQualifiedName(sourceTableName)}"
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}"
    }

    fun renameTable(sourceTableName: TableName, targetTableName: TableName): String {
        return "ALTER TABLE ${fullyQualifiedName(sourceTableName)} RENAME TO ${fullyQualifiedName(targetTableName)}"
    }

    fun getGenerationId(tableName: TableName): String {
        return "SELECT \"$COLUMN_NAME_AB_GENERATION_ID\" FROM ${fullyQualifiedName(tableName)} LIMIT 1"
    }

    private fun fullyQualifiedName(tableName: TableName): String {
        return "\"${tableName.namespace}\".\"${tableName.name}\""
    }
}
