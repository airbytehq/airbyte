/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.SQLException
import javax.sql.DataSource
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class MSSQLBulkLoadHandlerTest {

    private lateinit var dataSource: DataSource
    private lateinit var connection: Connection
    private lateinit var preparedStatement: PreparedStatement
    private lateinit var mssqlQueryBuilder: MSSQLQueryBuilder

    private lateinit var bulkLoadHandler: MSSQLBulkLoadHandler

    @BeforeEach
    fun setUp() {
        // Mockk initialization
        dataSource = mockk(relaxed = true)
        connection = mockk(relaxed = true)
        preparedStatement = mockk(relaxed = true)
        mssqlQueryBuilder = mockk(relaxed = true)

        // Common stubs
        every { dataSource.connection } returns connection
        every { connection.prepareStatement(any()) } returns preparedStatement
        every { connection.autoCommit = any() } just runs
        every { connection.commit() } just runs
        every { connection.rollback() } just runs
        every { preparedStatement.executeUpdate() } returns 1

        // Instantiate our MSSQLBulkLoadHandler
        bulkLoadHandler =
            MSSQLBulkLoadHandler(
                dataSource = dataSource,
                schemaName = "dbo",
                mainTableName = "MyMainTable",
                bulkUploadDataSource = "MyBlobDataSource",
                mssqlQueryBuilder = mssqlQueryBuilder
            )
    }

    @Test
    fun `test bulkLoadForAppendOverwrite success`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns false // No CDC logic

        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        // When
        bulkLoadHandler.bulkLoadForAppendOverwrite(
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        // Then
        // Verify that the prepared statement was created with the correct SQL
        val sqlSlot = slot<String>()
        verify { connection.prepareStatement(capture(sqlSlot)) }
        assertTrue(sqlSlot.captured.contains("BULK INSERT [dbo].[MyMainTable]"))
        assertTrue(sqlSlot.captured.contains("FROM '$dataFilePath'"))
        assertTrue(sqlSlot.captured.contains("FORMATFILE = '$formatFilePath'"))

        // Verify that commit was called and rollback was not
        verify(exactly = 1) { connection.commit() }
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.rollback() }
        // Verify that CDC delete is not called
        verify(exactly = 0) { mssqlQueryBuilder.deleteCdc(connection) }
    }

    @Test
    fun `test bulkLoadForAppendOverwrite rollback on SQLException`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns false
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        // Throw an exception when executing the prepared statement
        every { preparedStatement.executeUpdate() } throws SQLException("Test SQL Exception")

        // When & Then
        assertThrows(SQLException::class.java) {
            bulkLoadHandler.bulkLoadForAppendOverwrite(dataFilePath, formatFilePath)
        }

        // Verify that rollback was called and commit was not
        verify(exactly = 1) { connection.rollback() }
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.commit() }
    }

    @Test
    fun `test bulkLoadForAppendOverwrite with CDC enabled`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns true
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        // When
        bulkLoadHandler.bulkLoadForAppendOverwrite(dataFilePath, formatFilePath)

        // Then
        // We expect the CDC delete to be called
        verify { mssqlQueryBuilder.deleteCdc(connection) }
        // And we expect a commit (no rollback)
        verify(exactly = 1) { connection.commit() }
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.rollback() }
    }

    @Test
    fun `test bulkLoadAndUpsertForDedup success`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns false
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"
        val pkColumns = listOf("Id")
        val cursorColumns = listOf("Id")
        val nonPkColumns = listOf("Name", "Value")

        // When
        bulkLoadHandler.bulkLoadAndUpsertForDedup(
            primaryKeyColumns = pkColumns,
            cursorColumns = cursorColumns,
            nonPkColumns = nonPkColumns,
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        // Then
        // We'll capture the SQL statements generated
        val sqlStatements = mutableListOf<String>()
        verify(atLeast = 1) { connection.prepareStatement(capture(sqlStatements)) }

        // 1) The first statement should create temp table
        assertTrue(
            sqlStatements.any { it.contains("SELECT TOP 0 *\nINTO [##TempTable_") },
            "Expected a statement containing SELECT TOP 0 * INTO [##TempTable_"
        )

        // 2) The second statement should do the bulk insert into temp table
        assertTrue(
            sqlStatements.any { it.contains("BULK INSERT [##TempTable_") },
            "Expected a statement containing BULK INSERT [##TempTable_"
        )

        // 3) The third statement should be MERGE into the main table
        assertTrue(
            sqlStatements.any { it.contains("MERGE INTO [dbo].[MyMainTable] AS Target") },
            "Expected a statement containing MERGE INTO [dbo].[MyMainTable] AS Target"
        )

        // No rollback, commit should be called once
        verify(exactly = 2) { connection.commit() }
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.rollback() }
        // No CDC call
        verify(exactly = 0) { mssqlQueryBuilder.deleteCdc(connection) }
    }

    @Test
    fun `test bulkLoadAndUpsertForDedup rollback on SQLException`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns false
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"
        val pkColumns = listOf("Id")
        val cursorColumns = listOf("Id")
        val nonPkColumns = listOf("Name", "Value")

        // Simulate exception during the bulk insert
        every { preparedStatement.executeUpdate() } throws SQLException("Test SQL Exception")

        // When & Then
        assertThrows(SQLException::class.java) {
            bulkLoadHandler.bulkLoadAndUpsertForDedup(
                primaryKeyColumns = pkColumns,
                cursorColumns = cursorColumns,
                nonPkColumns = nonPkColumns,
                dataFilePath = dataFilePath,
                formatFilePath = formatFilePath
            )
        }

        // Verify we rolled back and never committed
        verify(exactly = 1) { connection.rollback() }
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.commit() }
    }

    @Test
    fun `test bulkLoadAndUpsertForDedup throws if primaryKeyColumns empty`() {
        // Given
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"
        val pkColumns = emptyList<String>() // no PK
        val cursorColumns = emptyList<String>() // no PK
        val nonPkColumns = listOf("Name", "Value")

        // When & Then
        assertThrows(IllegalArgumentException::class.java) {
            bulkLoadHandler.bulkLoadAndUpsertForDedup(
                primaryKeyColumns = pkColumns,
                cursorColumns = cursorColumns,
                nonPkColumns = nonPkColumns,
                dataFilePath = dataFilePath,
                formatFilePath = formatFilePath
            )
        }

        // Should not even attempt any SQL statements
        verify(exactly = 0) { connection.prepareStatement(any()) }
    }

    @Test
    fun `test buildBulkInsertSql includes row batch when specified`() {
        // We'll test the private method via reflection or by forcing public
        // For demonstration, let's call it indirectly:
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"
        val rowsPerBatch = 5000L

        // Force a call via the public method
        bulkLoadHandler.bulkLoadForAppendOverwrite(
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath,
            rowsPerBatch = rowsPerBatch
        )

        val sqlSlot = slot<String>()
        verify { connection.prepareStatement(capture(sqlSlot)) }
        assertTrue(
            sqlSlot.captured.contains("ROWS_PER_BATCH = 5000"),
            "Expected ROWS_PER_BATCH clause"
        )
    }

    @Test
    fun `test buildBulkInsertSql excludes row batch when not specified`() {
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        // Force a call via the public method
        bulkLoadHandler.bulkLoadForAppendOverwrite(
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        val sqlSlot = slot<String>()
        verify { connection.prepareStatement(capture(sqlSlot)) }
        assertFalse(
            sqlSlot.captured.contains("ROWS_PER_BATCH"),
            "Should not contain ROWS_PER_BATCH clause"
        )
    }

    @Test
    fun `test createTempTable`() {
        // We indirectly test createTempTable in bulkLoadAndUpsertForDedup.
        // But let's verify the actual statement for clarity:
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"
        val pkColumns = listOf("Id")
        val cursorColumns = listOf("Id")
        val nonPkColumns = listOf("Name")

        bulkLoadHandler.bulkLoadAndUpsertForDedup(
            primaryKeyColumns = pkColumns,
            cursorColumns = cursorColumns,
            nonPkColumns = nonPkColumns,
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        val sqlSlot = mutableListOf<String>()
        verify(atLeast = 1) { connection.prepareStatement(capture(sqlSlot)) }

        assertTrue(
            sqlSlot.any { it.contains("SELECT TOP 0 *\nINTO [##TempTable_") },
            "Expected creation of temp table via SELECT TOP 0 * INTO"
        )
    }

    @Test
    fun `test buildMergeSql includes PK columns and non-PK columns`() {
        // Force the MERGE by calling bulkLoadAndUpsertForDedup
        val pkColumns = listOf("Id", "TenantId")
        val cursorColumns = listOf("Id", "TenantId")
        val nonPkColumns = listOf("Name", "Description")
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        bulkLoadHandler.bulkLoadAndUpsertForDedup(
            primaryKeyColumns = pkColumns,
            cursorColumns = cursorColumns,
            nonPkColumns = nonPkColumns,
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        val sqlSlot = mutableListOf<String>()
        verify { connection.prepareStatement(capture(sqlSlot)) }

        val mergeStatement =
            sqlSlot.find { it.contains("MERGE INTO [dbo].[MyMainTable] AS Target") }
                ?: fail("MERGE statement not found")

        // Should have ON condition for both PK columns
        assertTrue(
            mergeStatement.contains(
                "ON Target.[Id] = Source.[Id] AND Target.[TenantId] = Source.[TenantId]\n"
            )
        )
        // Should have an UPDATE with the non-PK columns
        assertTrue(
            mergeStatement.contains(
                "WHEN MATCHED THEN\n    UPDATE SET\n        Target.[Name] = Source.[Name], Target.[Description] = Source.[Description]\n"
            )
        )
        // Should have an INSERT with [Id], [TenantId], [Name], [Description]
        assertTrue(
            mergeStatement.contains(
                "WHEN NOT MATCHED THEN\n    INSERT ([Id], [TenantId], [Name], [Description])\n    VALUES (Source.[Id], Source.[TenantId], Source.[Name], Source.[Description])\n;"
            )
        )
    }

    @Test
    fun `test generateLocalTempTableName returns expected pattern`() {
        // We'll call the private method via reflection in an actual codebase,
        // but for demonstration, let's quickly do it by making the method internal
        // or just trust it's tested indirectly. Here's how you'd do it with reflection:

        val method =
            MSSQLBulkLoadHandler::class.java.getDeclaredMethod("generateLocalTempTableName")
        method.isAccessible = true

        val tempTableName = method.invoke(bulkLoadHandler) as String
        assertTrue(
            tempTableName.startsWith("##TempTable_"),
            "Temp table name should start with ##TempTable_"
        )
        // Then check if it has a timestamp (regex etc.). We'll do a simple length check:
        assertTrue(
            tempTableName.length > "##TempTable_".length,
            "Temp table name should contain a timestamp suffix"
        )
    }

    @Test
    fun `test bulkLoadAndUpsertForDedup with cursor columns performs dedup`() {
        // Given
        every { mssqlQueryBuilder.hasCdc } returns false
        val dataFilePath = "azure://container/path/to/file.csv"
        val formatFilePath = "azure://container/path/to/format.fmt"

        // Suppose our primary key is "Id", and we also have a cursor column "updated_at".
        val pkColumns = listOf("Id")
        val nonPkColumns = listOf("Name", "Value")
        val cursorColumns = listOf("updated_at")

        // We will capture all SQL statements that are executed.
        val sqlStatements = mutableListOf<String>()
        every { connection.prepareStatement(capture(sqlStatements)) } returns preparedStatement

        // When
        bulkLoadHandler.bulkLoadAndUpsertForDedup(
            primaryKeyColumns = pkColumns,
            cursorColumns = cursorColumns,
            nonPkColumns = nonPkColumns,
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )

        // Then
        // 1. We expect at least these 4 statements in order:
        //    (a) Create temp table
        //    (b) Bulk insert into temp table
        //    (c) Deduplicate rows in the temp table (using a CTE, row_number > 1)
        //    (d) MERGE from temp table -> main table

        // Ensure CREATE TABLE statement is present:
        assertTrue(
            sqlStatements.any { it.contains("SELECT TOP 0 *\nINTO [##TempTable_") },
            "Expected the temp table creation statement (SELECT TOP 0 * INTO [##TempTable_...)"
        )

        // Ensure the bulk insert statement is present:
        assertTrue(
            sqlStatements.any { it.contains("BULK INSERT [##TempTable_") },
            "Expected a BULK INSERT statement into the temp table"
        )

        // **Ensure we have a CTE-based deduplication statement:**
        // For example, looking for "WITH Dedup_CTE" or "ROW_NUMBER() OVER"
        val dedupStatement =
            sqlStatements.find { it.contains("ROW_NUMBER() OVER") && it.contains("DELETE") }
        assertTrue(dedupStatement != null, "Expected a dedup statement using ROW_NUMBER() in a CTE")

        assertTrue(
            dedupStatement!!.contains(
                ";WITH Dedup_CTE AS (\n    SELECT T.*,\n        ROW_NUMBER() OVER (\n            PARTITION BY T.[Id]\n            ORDER BY T.[updated_at] DESC\n        ) AS row_num\n    FROM ["
            )
        )
        assertTrue(dedupStatement.contains("DELETE\n" + "FROM Dedup_CTE\n" + "WHERE row_num > 1;"))

        // Ensure we have a MERGE statement referencing the main table
        val mergeStatement =
            sqlStatements.find { it.contains("MERGE INTO [dbo].[MyMainTable] AS Target") }
        assertTrue(mergeStatement != null, "Expected a MERGE statement into main table")

        // Verify no rollback, one commit, and the connection was closed
        verify(exactly = 2) {
            connection.commit()
        } // Temp table creation + final commit after MERGE
        verify(exactly = 1) { connection.close() }
        verify(exactly = 0) { connection.rollback() }
    }
}
