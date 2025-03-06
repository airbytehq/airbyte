/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.SQLException
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.sql.DataSource
import kotlin.math.absoluteValue
import kotlin.random.Random

private val logger = KotlinLogging.logger {}

class MSSQLBulkLoadHandler(
    private val dataSource: DataSource,
    private val schemaName: String,
    private val mainTableName: String,
    private val bulkUploadDataSource: String,
    private val mssqlQueryBuilder: MSSQLQueryBuilder
) {

    companion object {
        // Common bulk insert constants
        private const val CODE_PAGE = "65001"
        private const val FILE_FORMAT = "CSV"
    }

    /**
     * Bulk-load data in "append-overwrite" mode from the CSV file located in Azure Blob Storage.
     *
     * @param dataFilePath The path to the CSV file in Azure Blob Storage
     * @param formatFilePath The path to a format file if needed
     * @param rowsPerBatch Optional parameter to control the batching size in BULK INSERT.
     */
    fun bulkLoadForAppendOverwrite(
        dataFilePath: String,
        formatFilePath: String,
        rowsPerBatch: Long? = null
    ) {
        val bulkInsertSql =
            buildBulkInsertSql(
                quotedTableName =
                    quoteIdentifier(schemaName = schemaName, tableName = mainTableName),
                dataFilePath = dataFilePath,
                formatFilePath = formatFilePath,
                rowsPerBatch = rowsPerBatch,
            )

        dataSource.connection.use { conn ->
            conn.autoCommit = false
            try {
                logger.info {
                    "Starting bulk insert into table: $schemaName.$mainTableName from file: $dataFilePath"
                }
                conn.prepareStatement(bulkInsertSql).use { stmt -> stmt.executeUpdate() }
                logger.info {
                    "Bulk insert completed successfully for table: $schemaName.$mainTableName"
                }
                handleCdcDeletes(conn)
                conn.commit()
            } catch (ex: SQLException) {
                logger.error(ex) { "Error during bulk insert; rolling back. Cause: ${ex.message}" }
                conn.rollback()
                throw ex
            }
        }
    }

    /**
     * Bulk load CSV data into a local temp table, then upsert (merge) into a main table when there
     * are multiple primary key columns. This helps deduplicate records.
     *
     * @param primaryKeyColumns A list of the column names that form the composite PK
     * @param nonPkColumns A list of non-PK column names
     * @param dataFilePath The path to the CSV file in Azure Blob Storage
     * @param formatFilePath (Optional) The path to a format file if needed
     * @param rowsPerBatch Optional parameter to control the batching size in BULK INSERT.
     */
    fun bulkLoadAndUpsertForDedup(
        primaryKeyColumns: List<String>,
        cursorColumns: List<String>,
        nonPkColumns: List<String>,
        dataFilePath: String,
        formatFilePath: String,
        rowsPerBatch: Long? = null
    ) {
        if (primaryKeyColumns.isEmpty()) {
            throw IllegalArgumentException("At least one primary key column is required.")
        }

        val tempTableName = generateLocalTempTableName()

        dataSource.connection.use { conn ->
            conn.autoCommit = false
            try {
                // Create the temp table
                createTempTable(conn, tempTableName)
                // Bulk load the CSV data into the temp table
                val bulkInsertSql =
                    buildBulkInsertSql(
                        quotedTableName = "[$tempTableName]",
                        dataFilePath = dataFilePath,
                        formatFilePath = formatFilePath,
                        rowsPerBatch = rowsPerBatch,
                    )
                logger.info {
                    "Starting bulk insert into temp table: $tempTableName from file: $dataFilePath"
                }
                conn.prepareStatement(bulkInsertSql).use { stmt -> stmt.executeUpdate() }
                logger.info { "Bulk insert completed successfully for temp table: $tempTableName" }

                // Deduplicate temp table
                deduplicateTempTable(conn, tempTableName, primaryKeyColumns, cursorColumns)

                // Merge into the main table
                val mergeSql = buildMergeSql(tempTableName, primaryKeyColumns, nonPkColumns)
                logger.info { "Starting MERGE into: $schemaName.$mainTableName" }
                conn.prepareStatement(mergeSql).use { stmt -> stmt.executeUpdate() }
                logger.info {
                    "MERGE completed successfully into table: $schemaName.$mainTableName"
                }

                handleCdcDeletes(conn)
                conn.commit()
            } catch (ex: SQLException) {
                logger.error(ex) {
                    "Error during bulk load & upsert; rolling back. Cause: $ex.message"
                }
                conn.rollback()
                throw ex
            }
        }
    }

    private fun deduplicateTempTable(
        conn: Connection,
        tempTableName: String,
        primaryKeyColumns: List<String>,
        cursorColumns: List<String>
    ) {
        // Build the partition clause for primary keys, e.g. T.[id1], T.[id2]
        val pkPartition = primaryKeyColumns.joinToString(", ") { "T.[$it]" }

        // Build the ORDER BY clause using cursor columns in descending order
        val orderByClause =
            if (cursorColumns.isNotEmpty()) {
                cursorColumns.joinToString(", ") { "T.[$it] DESC" }
            } else {
                // If no cursor columns are provided, you can either choose no ordering (SELECT
                // NULL).
                "(SELECT NULL)"
            }

        val dedupSql =
            """
        ;WITH Dedup_CTE AS (
            SELECT T.*,
                ROW_NUMBER() OVER (
                    PARTITION BY $pkPartition
                    ORDER BY $orderByClause
                ) AS row_num
            FROM [$tempTableName] T
        )
        DELETE
        FROM Dedup_CTE
        WHERE row_num > 1;
    """.trimIndent()

        logger.info { "Starting deduplication for temp table: $tempTableName" }
        conn.prepareStatement(dedupSql).use { stmt -> stmt.executeUpdate() }
        logger.info { "Deduplication completed for temp table: $tempTableName" }
    }

    private fun handleCdcDeletes(conn: Connection) {
        if (mssqlQueryBuilder.hasCdc) {
            logger.info {
                "Starting removal of deleted records in table: $schemaName.$mainTableName"
            }
            mssqlQueryBuilder.deleteCdc(conn)
            logger.info {
                "Deleted records removal completed successfully in table: $schemaName.$mainTableName"
            }
        }
    }

    private fun quoteIdentifier(schemaName: String, tableName: String): String {
        return "[$schemaName].[$tableName]"
    }

    /** Builds the BULK INSERT SQL statement with optional rowsPerBatch. */
    private fun buildBulkInsertSql(
        quotedTableName: String,
        dataFilePath: String,
        formatFilePath: String,
        rowsPerBatch: Long? = null
    ): String {
        // The ROWS_PER_BATCH hint can help optimize the bulk load.
        // If not provided, it won't be included in the statement.
        val rowBatchClause = rowsPerBatch?.let { "ROWS_PER_BATCH = $it," } ?: ""
        return StringBuilder()
            .apply {
                append("BULK INSERT $quotedTableName\n")
                append("FROM '$dataFilePath'\n")
                append("WITH (\n")
                append("\tCODEPAGE = '$CODE_PAGE',\n")
                append("\tDATA_SOURCE = '$bulkUploadDataSource',\n")
                append("\tFORMATFILE_DATA_SOURCE = '$bulkUploadDataSource',\n")
                append("\tFIRSTROW = 2,\n")
                append("\tFORMAT = '$FILE_FORMAT',\n")
                append("\tFORMATFILE = '$formatFilePath',\n")
                append("\t$rowBatchClause\n")
                append("\tKEEPNULLS\n")
                append(")")
            }
            .toString()
            .trimIndent()
    }

    /** Creates a Global temp table by cloning the column structure from the main table. */
    private fun createTempTable(conn: Connection, tempTableName: String) {
        val createTempTableSql =
            """
            SELECT TOP 0 *
            INTO [${tempTableName}]
            FROM ${quoteIdentifier(schemaName, mainTableName)}
        """.trimIndent()

        conn.prepareStatement(createTempTableSql).use { stmt -> stmt.executeUpdate() }
        conn.commit()
    }

    /**
     * Builds a MERGE statement using the provided PK and non-PK columns, always quoting column
     * names to avoid keyword conflicts.
     */
    private fun buildMergeSql(
        tempTableName: String,
        primaryKeyColumns: List<String>,
        nonPkColumns: List<String>
    ): String {
        val quotedTableName = quoteIdentifier(schemaName = schemaName, tableName = mainTableName)
        // 1. ON condition:
        //    e.g. Target.[Pk1] = Source.[Pk1] AND Target.[Pk2] = Source.[Pk2]
        val onCondition = primaryKeyColumns.joinToString(" AND ") { "Target.[$it] = Source.[$it]" }

        // 2. All columns for the INSERT statement (quoted)
        val allColumns = primaryKeyColumns + nonPkColumns
        val allColumnsCsv = allColumns.joinToString(", ") { "[$it]" }

        // 3. The UPDATE assignments for non-PK columns
        //    e.g. Target.[col1] = Source.[col1], Target.[col2] = ...
        val updateAssignments = nonPkColumns.joinToString(", ") { "Target.[$it] = Source.[$it]" }

        // 4. The VALUES for the INSERT statement
        //    e.g. Source.[Pk1], Source.[col1], Source.[col2]...
        val sourceColumnsCsv = allColumns.joinToString(", ") { "Source.[$it]" }

        return """
        MERGE INTO $quotedTableName AS Target
        USING [$tempTableName] AS Source
            ON $onCondition
        WHEN MATCHED THEN
            UPDATE SET
                $updateAssignments
        WHEN NOT MATCHED THEN
            INSERT ($allColumnsCsv)
            VALUES ($sourceColumnsCsv)
        ;
    """.trimIndent()
    }

    /** Generates a local temp table name with a timestamp suffix to avoid collisions. */
    private fun generateLocalTempTableName(): String {
        val timestamp =
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss_SSS"))
        return "##TempTable_${timestamp}_${Random.nextInt().absoluteValue}"
    }
}
