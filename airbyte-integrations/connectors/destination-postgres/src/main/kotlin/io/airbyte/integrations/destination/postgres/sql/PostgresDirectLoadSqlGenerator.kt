/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
// we are using this on the cdk so I'm assuming this is the right import for sql data types
import org.jooq.impl.SQLDataType

internal const val COUNT_TOTAL_ALIAS = "total"

private val log = KotlinLogging.logger {}

@Singleton
class PostgresDirectLoadSqlGenerator {
    companion object {
        /**
         * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
         * we want to log
         */
        fun String.andLog(): String {
            log.info { this.trim() }
            return this
        }
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean // I don't really know what to do with this
    ): String {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)};
            CREATE TABLE ${fullyQualifiedName(tableName)} (
            $columnDeclarations
            );
            COMMIT;
            """
            .trimIndent()
            .andLog()

    }

    private fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): String {
        return stream.schema
            .asColumns()
            .map { (columnName, columnType) ->
                val targetColumnName = columnNameMapping[columnName] //can I assume there's always a mapping?
                val typeName = columnType.type.toDialectType()
                "$targetColumnName $typeName"
            }
            .joinToString(",\n")
    }

    // not sure which one is the one we should be overwriting. I went with deleting target,
    // and renaming source
    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${fullyQualifiedName(targetTableName)};
            ALTER TABLE ${fullyQualifiedName(sourceTableName)} RENAME TO ${fullyQualifiedName(targetTableName)};
            COMMIT;
            """
            .trimIndent()
            .andLog()
    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames = columnNameMapping.map { (_, targetName) -> targetName }.joinToString(",")
        return """
            CREATE TABLE ${fullyQualifiedName(targetTableName)} AS
            SELECT $columnNames
            FROM ${fullyQualifiedName(sourceTableName)};
            """
            .trimIndent()
            .andLog()

    }

    @Suppress("UNUSED_PARAMETER")
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String = TODO("PostgresDirectLoadSqlGenerator.upsertTable not yet implemented")

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)};".andLog()

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS $COUNT_TOTAL_ALIAS FROM ${fullyQualifiedName(tableName)};".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\";".andLog()
    }

    @Suppress("UNUSED_PARAMETER")
    fun getGenerationId(tableName: TableName): String =
        "SELECT ${COLUMN_NAME_AB_GENERATION_ID} FROM ${fullyQualifiedName(tableName)} LIMIT 1;".andLog()



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

    private fun fullyQualifiedName(tableName: TableName): String =
        "\"${tableName.namespace}\".\"${tableName.name}\""

    fun AirbyteType.toDialectType(): String =
        when (this) {
            BooleanType -> SQLDataType.BOOLEAN.typeName
            DateType -> SQLDataType.DATE.typeName
            IntegerType -> SQLDataType.BIGINT.typeName
            NumberType -> SQLDataType.DECIMAL.typeName
            StringType -> SQLDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> SQLDataType.TIMEWITHTIMEZONE.typeName
            TimeTypeWithoutTimezone -> SQLDataType.TIME.typeName
            TimestampTypeWithTimezone -> SQLDataType.TIMESTAMPWITHTIMEZONE.typeName
            TimestampTypeWithoutTimezone -> SQLDataType.TIMESTAMP.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnionType -> SQLDataType.JSONB.typeName
            is UnknownType -> SQLDataType.VARCHAR.typeName
        }
}
