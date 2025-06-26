/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.integrations.destination.mssql.v2.MSSQLFormatFileCreator
import io.airbyte.integrations.destination.mssql.v2.MSSQLFormatFileCreator.ColumnInfo
import io.airbyte.integrations.destination.mssql.v2.MSSQLFormatFileCreator.CsvToDbColumn
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import javax.sql.DataSource
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class MSSQLFormatFileCreatorTest {

    private val dataSource: DataSource = mockk()
    private val azureBlobClient: AzureBlobClient = mockk()
    private val stream: DestinationStream = mockk(relaxed = true)

    /**
     * Test that fetchTableColumns returns the expected list of ColumnInfo by simulating a SQL
     * result set.
     */
    @Test
    fun `test fetchTableColumns returns correct columns`() {
        val connection: Connection = mockk()
        val preparedStatement: PreparedStatement = mockk()
        val resultSet: ResultSet = mockk()
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

        every { dataSource.connection } returns connection
        every { connection.prepareStatement(sql) } returns preparedStatement
        every { connection.close() } just Runs
        every { preparedStatement.executeQuery() } returns resultSet
        every { preparedStatement.setString(1, any()) } just Runs
        every { preparedStatement.setString(2, any()) } just Runs
        every { preparedStatement.close() } just Runs

        // Simulate a result set with two rows:
        // Row 1: id (int, no char length) and Row 2: name (varchar, length 255)
        val rows =
            listOf(
                mapOf(
                    "ORDINAL_POSITION" to 1,
                    "COLUMN_NAME" to "id",
                    "DATA_TYPE" to "int",
                    "CHARACTER_MAXIMUM_LENGTH" to null
                ),
                mapOf(
                    "ORDINAL_POSITION" to 2,
                    "COLUMN_NAME" to "name",
                    "DATA_TYPE" to "varchar",
                    "CHARACTER_MAXIMUM_LENGTH" to 255
                )
            )
        var rowIndex = -1
        every { resultSet.next() } answers
            {
                rowIndex++
                rowIndex < rows.size
            }
        every { resultSet.getInt("ORDINAL_POSITION") } answers
            {
                rows[rowIndex]["ORDINAL_POSITION"] as Int
            }
        every { resultSet.getString("COLUMN_NAME") } answers
            {
                rows[rowIndex]["COLUMN_NAME"] as String
            }
        every { resultSet.getString("DATA_TYPE") } answers { rows[rowIndex]["DATA_TYPE"] as String }
        every { resultSet.getInt("CHARACTER_MAXIMUM_LENGTH") } answers
            {
                (rows[rowIndex]["CHARACTER_MAXIMUM_LENGTH"] as? Int) ?: 0
            }
        every { resultSet.wasNull() } answers { rows[rowIndex]["CHARACTER_MAXIMUM_LENGTH"] == null }
        every { resultSet.close() } just Runs

        val creator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)
        val columns = creator.fetchTableColumns("dbo", "test_table")

        assertEquals(2, columns.size)
        with(columns[0]) {
            assertEquals(1, ordinalPosition)
            assertEquals("id", name)
            assertEquals("int", dataType)
            assertNull(charMaxLength)
        }
        with(columns[1]) {
            assertEquals(2, ordinalPosition)
            assertEquals("name", name)
            assertEquals("varchar", dataType)
            assertEquals(255, charMaxLength)
        }

        verify { connection.prepareStatement(sql) }
        verify { connection.close() }
        verify { preparedStatement.setString(1, "dbo") }
        verify { preparedStatement.setString(2, "test_table") }
        verify { preparedStatement.executeQuery() }
        verify { preparedStatement.close() }
        verify { resultSet.close() }
    }

    /** Test that buildCsvToDbMapping properly maps CSV headers to DB columns. */
    @Test
    fun `test buildCsvToDbMapping returns correct mapping`() {
        val csvHeaders = listOf("id", "name")
        val dbColumns =
            listOf(ColumnInfo(1, "id", "int", null), ColumnInfo(2, "name", "varchar", 255))

        val creator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)
        val mapping = creator.buildCsvToDbMapping(csvHeaders, dbColumns)

        assertEquals(2, mapping.size)
        with(mapping[0]) {
            assertEquals(1, csvPosition)
            assertEquals(1, dbOrdinal)
            assertEquals("id", dbColumnName)
            assertEquals("int", dbDataType)
            assertNull(dbCharLength)
        }
        with(mapping[1]) {
            assertEquals(2, csvPosition)
            assertEquals(2, dbOrdinal)
            assertEquals("name", dbColumnName)
            assertEquals("varchar", dbDataType)
            assertEquals(255, dbCharLength)
        }
    }

    /** Test that buildCsvToDbMapping throws an error if a CSV column has no matching DB column. */
    @Test
    fun `test buildCsvToDbMapping throws error when mapping not found`() {
        val csvHeaders = listOf("id", "non_existent")
        val dbColumns = listOf(ColumnInfo(1, "id", "int", null))
        val creator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)
        val exception =
            assertThrows<IllegalStateException> {
                creator.buildCsvToDbMapping(csvHeaders, dbColumns)
            }
        assertTrue(exception.message!!.contains("No matching DB column found"))
    }

    /**
     * Test that buildFormatFileContent produces the expected .fmt file content. This indirectly
     * tests the pickBcpTypeAndLength logic.
     */
    @Test
    fun `test buildFormatFileContent produces correct format file content`() {
        // Two mappings: one for an int column and one for a varchar column.
        val mapping =
            listOf(
                CsvToDbColumn(1, 1, "id", "int", null),
                CsvToDbColumn(2, 2, "name", "varchar", 255)
            )
        val creator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)
        val delimiter = ","
        val rowDelimiter = "\\r\\n"
        val version = "12.0"

        val content = creator.buildFormatFileContent(mapping, delimiter, rowDelimiter, version)
        val lines = content.lines().filter { it.isNotBlank() }

        // Expected header lines
        assertEquals(version, lines[0])
        assertEquals("2", lines[1])

        // For the first mapping ("id", int) the pickBcpTypeAndLength returns ("SQLCHAR", 12)
        val expectedLine1 =
            "%-8d %-10s %-8d %-8d %-8s %-8d %s %s".format(
                1,
                "SQLCHAR",
                0,
                12,
                "\"$delimiter\"",
                1,
                "id",
                "SQL_Latin1_General_CP1_CI_AS"
            )
        assertEquals(expectedLine1, lines[2])

        // For the second mapping ("name", varchar) the length is computed as 255.
        // Since it is the last mapping, the delimiter becomes the row delimiter.
        val expectedLine2 =
            "%-8d %-10s %-8d %-8d %-8s %-8d %s %s".format(
                2,
                "SQLCHAR",
                0,
                255,
                "\"$rowDelimiter\"",
                2,
                "name",
                "SQL_Latin1_General_CP1_CI_AS"
            )
        assertEquals(expectedLine2, lines[3])
    }
}
