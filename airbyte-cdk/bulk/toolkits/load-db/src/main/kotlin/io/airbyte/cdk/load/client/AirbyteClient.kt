package io.airbyte.cdk.load.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName

abstract class AirbyteClient<DestinationDataType: Enum<DestinationDataType>>() {
    /**
     * Returns the number of records in a specific table within a given database.
     *
     * @param database The name of the database.
     * @param table The name of the table.
     * @return The number of records in the specified table.
     */
    // TODO: missing namespace
    abstract fun getNumberOfRecordsInTable(table: String): Long

    /**
     * Executes a query against the database.
     *
     * @param query The SQL query to execute.
     * @return A boolean indicating whether the query was executed successfully.
     */
    protected abstract fun executeQuery(query: String): Boolean

    protected abstract fun getDatabaseName(): String

    open fun getCreateTableStatement(stream: DestinationStream,
                                                   tableName: TableName,
                                                   columnNameMapping: ColumnNameMapping,
                                                   replace: Boolean,): Sql {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)

        val forceCreateTable = if (replace) "OR REPLACE" else ""
//        TODO: Add namespace to table name properly — CH doesn't like periods
//        val finalTableId = tableName.toPrettyString(QUOTE)
        val finalTableId = tableName.name

        return return Sql.of(
            """
            CREATE $forceCreateTable TABLE `${getDatabaseName()}`.$finalTableId (
              _airbyte_raw_id String NOT NULL,
              _airbyte_extracted_at DateTime64(3) NOT NULL,
              _airbyte_meta String NOT NULL,
              _airbyte_generation_id UInt32,
              $columnDeclarations
            )
            ${getCreateTableSuffix()}
            """.trimIndent()
        )
    }

    protected open fun getCreateTableSuffix(): String = ""

    protected open fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): String =
        stream.schema
            .asColumns()
            .map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName]!!
                val typeName = toDialectType(type.type).name
                "`$columnName` $typeName"
            }
            .joinToString(",\n")

    protected abstract fun toDialectType(type: AirbyteType): DestinationDataType
}
