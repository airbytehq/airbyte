/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking

private const val COLLATION = "SQL_Latin1_General_CP1_CI_AS"

internal class MSSQLFormatFileCreator(
    private val dataSource: DataSource,
    private val stream: DestinationStream,
    private val azureBlobClient: AzureBlobClient
) {

    /** Simple struct holding column metadata retrieved from SQL Server. */
    internal data class ColumnInfo(
        val ordinalPosition: Int, // 1-based position of the column in the table
        val name: String, // Column name
        val dataType: String, // e.g., "varchar", "int", "datetime"
        val charMaxLength: Int?, // May be null for non-character types
    )

    /** Intermediate struct mapping a CSV column to its corresponding SQL column info. */
    internal data class CsvToDbColumn(
        val csvPosition: Int, // 1-based index in the CSV
        val dbOrdinal: Int, // The column's ordinal position in the table
        val dbColumnName: String, // Column name in the DB
        val dbDataType: String, // The column's data type in the DB
        val dbCharLength: Int?, // The column's max length in the DB
    )

    fun createAndUploadFormatFile(defaultSchemaName: String): AzureBlob {
        // 1) Determine the target schema (namespace) to which this stream maps.
        val targetSchema = stream.descriptor.namespace ?: defaultSchemaName

        // 2) Retrieve DB columns for the table (in ordinal order).
        val dbColumns = fetchTableColumns(targetSchema, stream.descriptor.name)

        // 3) Build a CSV-to-DB mapping so each CSV column lines up with the correct DB column.
        val csvColumnNames = stream.schema.withAirbyteMeta(true).toCsvHeader().toList()
        val csvToDbMapping = buildCsvToDbMapping(csvColumnNames, dbColumns)

        // 4) Generate the .fmt content
        val fmtContent =
            buildFormatFileContent(
                csvToDbMapping = csvToDbMapping,
                delimiter = ",",
                rowDelimiter = "\\r\\n",
                formatFileVersion = "12.0",
            )

        // 5) Upload the format file to Azure Blob Storage
        val blobPath = buildFormatFileBlobPath(targetSchema)
        return runBlocking { azureBlobClient.put(blobPath, fmtContent.toByteArray()) }
    }

    /**
     * Retrieves columns for a given table in SQL Server, returning them in ascending ordinal order.
     */
    internal fun fetchTableColumns(schemaName: String, tableName: String): List<ColumnInfo> {
        val sql =
            """
            SELECT 
                ORDINAL_POSITION,
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ? 
              AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """.trimIndent()

        dataSource.connection.use { conn ->
            conn.prepareStatement(sql).use { stmt ->
                stmt.setString(1, schemaName)
                stmt.setString(2, tableName)

                stmt.executeQuery().use { rs ->
                    val columns = mutableListOf<ColumnInfo>()
                    while (rs.next()) {
                        val ordinal = rs.getInt("ORDINAL_POSITION")
                        val colName = rs.getString("COLUMN_NAME")
                        val dataType = rs.getString("DATA_TYPE")
                        val charLen = rs.getInt("CHARACTER_MAXIMUM_LENGTH")
                        val lengthOrNull = if (rs.wasNull()) null else charLen

                        columns.add(
                            ColumnInfo(
                                ordinalPosition = ordinal,
                                name = colName,
                                dataType = dataType,
                                charMaxLength = lengthOrNull,
                            ),
                        )
                    }
                    return columns
                }
            }
        }
    }

    /**
     * Builds a mapping from CSV columns (by name) to their corresponding DB columns, ensuring we
     * track the CSV column index (1-based) alongside the DB column’s ordinal position and metadata.
     */
    internal fun buildCsvToDbMapping(
        csvColumnNames: List<String>,
        dbColumns: List<ColumnInfo>
    ): List<CsvToDbColumn> {
        return csvColumnNames.mapIndexed { idx, csvColName ->
            val match =
                dbColumns.firstOrNull { it.name.equals(csvColName, ignoreCase = true) }
                    ?: error(
                        "No matching DB column found for CSV column '$csvColName' in table schema.",
                    )
            CsvToDbColumn(
                csvPosition = idx + 1,
                dbOrdinal = match.ordinalPosition,
                dbColumnName = match.name,
                dbDataType = match.dataType,
                dbCharLength = match.charMaxLength,
            )
        }
    }

    /**
     * Builds the content of the non-XML format file (.fmt) for SQL Server’s BULK INSERT. This ties
     * CSV columns (SQLCHAR, etc.) to table columns in the correct order, using UTF-8 collation and
     * automatically determining a prefix length if the column is nullable.
     */
    internal fun buildFormatFileContent(
        csvToDbMapping: List<CsvToDbColumn>,
        delimiter: String,
        rowDelimiter: String,
        formatFileVersion: String
    ): String {
        val sb = StringBuilder()

        // First line: format file version (e.g. 12.0)
        sb.appendLine(formatFileVersion)
        // Second line: total field count
        sb.appendLine(csvToDbMapping.size.toString())

        // Next N lines: define each column.
        // Format:
        // <CSVFieldPos> <BCPType> <PrefixLength> <Length> <Delimiter> <ServerColumnOrder>
        // <ColumnName> <Collation>
        csvToDbMapping.forEachIndexed { i, mapping ->
            val (csvPos, dbOrdinal, dbColName, dbDataType, dbCharLength) = mapping

            val (bcpType, length) = pickBcpTypeAndLength(dbDataType, dbCharLength)
            val isLast = (i == csvToDbMapping.size - 1)
            val usedDelimiter = if (isLast) "\"$rowDelimiter\"" else "\"$delimiter\""

            // For simplicity, apply the UTF-8 collation to all text-based columns (SQLCHAR).
            // If the column is numeric or date, the collation will be ignored by the server anyway.
            sb.appendLine(
                "%-8d %-10s %-8d %-8d %-8s %-8d %s %s".format(
                    csvPos,
                    bcpType,
                    0,
                    length,
                    usedDelimiter,
                    dbOrdinal,
                    dbColName,
                    COLLATION,
                ),
            )
        }

        return sb.toString()
    }

    /**
     * Chooses the correct BCP type ("SQLCHAR") and a reasonable max length in bytes based on the
     * SQL data type. Adapt or expand this logic as needed.
     */
    private fun pickBcpTypeAndLength(dataType: String, charMaxLength: Int?): Pair<String, Int> {
        // For CSV-based imports, it's common to treat all columns as text (SQLCHAR).
        // The length is a best-guess upper bound in bytes.
        return when (dataType.lowercase()) {
            "int" -> "SQLCHAR" to 12
            "bigint" -> "SQLCHAR" to 20
            "bit" -> "SQLCHAR" to 1
            "datetime",
            "smalldatetime",
            "datetime2",
            "date",
            "time" -> "SQLCHAR" to 25
            "decimal",
            "numeric",
            "money",
            "smallmoney",
            "float",
            "real" -> "SQLCHAR" to 50
            "varchar",
            "char",
            "nvarchar",
            "nchar" -> {
                val length =
                    if (charMaxLength != null && charMaxLength > 0) {
                        // For nvarchar, consider doubling (2 bytes per char)
                        (charMaxLength * if (dataType.startsWith("n")) 2 else 1).coerceAtLeast(
                            4
                        ) // small safety floor
                    } else {
                        // fallback for (max) or unknown
                        8000
                    }
                "SQLCHAR" to length
            }
            else -> "SQLCHAR" to 8000 // fallback for unknown or large types
        }
    }

    /**
     * Builds a path for uploading the .fmt file to Azure Blob Storage. For example:
     * "mySchema/myStreamName/format/1676999999999/formatFile.fmt"
     */
    private fun buildFormatFileBlobPath(outputSchema: String): String {
        return "${outputSchema}/${stream.descriptor.name}/format/${System.currentTimeMillis()}/formatFile.fmt"
    }
}
