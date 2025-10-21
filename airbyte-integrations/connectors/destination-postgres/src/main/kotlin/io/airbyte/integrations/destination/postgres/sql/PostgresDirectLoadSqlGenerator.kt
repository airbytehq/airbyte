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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.collections.forEach

internal const val COUNT_TOTAL_ALIAS = "total"

private val log = KotlinLogging.logger {}

@Singleton
class PostgresDirectLoadSqlGenerator(val postgresColumnUtils: PostgresColumnUtils) {
    companion object {
        internal val DEFAULT_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_RAW_ID,
                    columnTypeName = PostgresDataType.VARCHAR.typeName,
                    nullable = false

                ),
                Column(
                    columnName = COLUMN_NAME_AB_EXTRACTED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_META,
                    columnTypeName = PostgresDataType.JSONB.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_GENERATION_ID,
                    columnTypeName = PostgresDataType.BIGINT.typeName,
                    nullable = false
                ),
            )

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
        replace: Boolean
    ): String {
        val columnDeclarations = postgresColumnUtils.columnsAndTypes((stream.schema as ObjectType).properties, columnNameMapping).joinToString(",\n")
        val dropTableIfExistsStatement = if (replace) "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};" else ""
        return """
            BEGIN TRANSACTION;
            $dropTableIfExistsStatement
            CREATE TABLE ${getFullyQualifiedName(tableName)} (
                $columnDeclarations
            );
            COMMIT;
            """
            .trimIndent()
            .andLog()
    }


    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)};
            ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${getName(targetTableName)};
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
        val columnNames = getTargetColumnNames(columnNameMapping).joinToString(",")
        return """
            INSERT INTO ${getFullyQualifiedName(targetTableName)} ($columnNames)
            SELECT $columnNames
            FROM ${getFullyQualifiedName(sourceTableName)};
            """
            .trimIndent()
            .andLog()

    }

    private fun getTargetColumnNames(columnNameMapping: ColumnNameMapping): List<String> =
        postgresColumnUtils.defaultColumns().map { "\"${it.columnName}\"" } + columnNameMapping.map { (_, targetName) -> "\"${targetName}\"" }

    @Suppress("UNUSED_PARAMETER")
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String = TODO("PostgresDirectLoadSqlGenerator.upsertTable not yet implemented")

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};".andLog()

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS \"$COUNT_TOTAL_ALIAS\" FROM ${getFullyQualifiedName(tableName)};".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\";".andLog()
    }

    fun getGenerationId(tableName: TableName): String =
        "SELECT \"${COLUMN_NAME_AB_GENERATION_ID}\" FROM ${getFullyQualifiedName(tableName)} LIMIT 1;".andLog()

    fun getTableSchema(tableName: TableName): String =
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '${tableName.namespace}'
        AND table_name = '${tableName.name}';
        """.trimIndent().andLog()

    fun copyFromCsv(tableName: TableName): String =
        """
        COPY "${tableName.namespace}"."${tableName.name}"
        FROM STDIN
        WITH (FORMAT csv)
        """.trimIndent()

    //should all alters happen in one same tx? probably
    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Set<Column>,
        columnsToRemove: Set<Column>,
        columnsToModify: Set<Column>,
    ): Set<String> {
        val clauses = mutableSetOf<String>()
        val fullyQualifiedTableName = getFullyQualifiedName(tableName)
        columnsToAdd.forEach {
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName ADD COLUMN ${getName(it)} ${it.columnTypeName};".andLog()
            )
        }
        columnsToRemove.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName DROP COLUMN ${getName(it)};".andLog())
        }

        columnsToModify.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName ALTER COLUMN ${getName(it)} SET DATA TYPE ${it.columnTypeName};".andLog())
        }
        return clauses
    }

    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String =
        "\"${tableName.namespace}\""

    private fun getName(tableName: TableName): String =
        "\"${tableName.name}\""

    private fun getName(column: Column): String =
        "\"${column.columnName}\""

    fun AirbyteType.toDialectType(): String =
        when (this) {
            BooleanType -> PostgresDataType.BOOLEAN.typeName
            DateType -> PostgresDataType.DATE.typeName
            IntegerType -> PostgresDataType.BIGINT.typeName
            NumberType -> PostgresDataType.DECIMAL.typeName
            StringType -> PostgresDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> PostgresDataType.TIME_WITH_TIMEZONE.typeName
            TimeTypeWithoutTimezone -> PostgresDataType.TIME.typeName
            TimestampTypeWithTimezone -> PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName
            TimestampTypeWithoutTimezone -> PostgresDataType.TIMESTAMP.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnknownType,
            is UnionType -> PostgresDataType.JSONB.typeName
        }
}

data class Column(val columnName: String, val columnTypeName: String, val nullable: Boolean = true) {
    override fun toString(): String {
        val isNullableSuffix = if (nullable) "" else "NOT NULL"
        return "\"$columnName\" $columnTypeName $isNullableSuffix".trim()
    }
}
