/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import javax.sql.DataSource
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest
import software.amazon.awssdk.services.s3.model.DeleteObjectResponse
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.s3.model.PutObjectResponse

@ExtendWith(MockKExtension::class)
internal class RedshiftAirbyteClientTest {

    @MockK lateinit var dataSource: DataSource
    @MockK lateinit var sqlGenerator: RedshiftSqlGenerator
    @MockK lateinit var s3Client: S3Client
    @MockK lateinit var mockConnection: Connection
    @MockK lateinit var mockStatement: Statement
    @MockK lateinit var mockPreparedStatement: PreparedStatement
    @MockK lateinit var mockResultSet: ResultSet

    private lateinit var client: RedshiftAirbyteClient

    private val testTable = TableName(namespace = "test_schema", name = "test_table")

    @BeforeEach
    fun setUp() {
        every { dataSource.connection } returns mockConnection
        every { mockConnection.createStatement() } returns mockStatement
        every { mockConnection.prepareStatement(any()) } returns mockPreparedStatement
        every { mockConnection.close() } returns Unit
        every { mockStatement.close() } returns Unit
        every { mockPreparedStatement.close() } returns Unit
        every { mockResultSet.close() } returns Unit

        client = RedshiftAirbyteClient(dataSource, sqlGenerator, s3Client)
    }

    // ================================================================
    // createNamespace
    // ================================================================

    @Test
    fun `createNamespace delegates to sqlGenerator`() = runTest {
        every { sqlGenerator.createNamespace("my_schema") } returns "CREATE SCHEMA SQL"
        every { mockStatement.execute("CREATE SCHEMA SQL") } returns true

        client.createNamespace("my_schema")

        verify { sqlGenerator.createNamespace("my_schema") }
        verify { mockStatement.execute("CREATE SCHEMA SQL") }
    }

    @Test
    fun `createNamespace swallows already exists race condition`() = runTest {
        every { sqlGenerator.createNamespace("my_schema") } returns "CREATE SCHEMA SQL"
        every { mockStatement.execute("CREATE SCHEMA SQL") } throws
            SQLException("Schema my_schema already exists")

        assertDoesNotThrow { client.createNamespace("my_schema") }
    }

    @Test
    fun `createNamespace rethrows non-race-condition errors`() = runTest {
        every { sqlGenerator.createNamespace("my_schema") } returns "CREATE SCHEMA SQL"
        every { mockStatement.execute("CREATE SCHEMA SQL") } throws
            SQLException("permission denied")

        assertThrows<SQLException> { client.createNamespace("my_schema") }
    }

    // ================================================================
    // namespaceExists / tableExists
    // ================================================================

    @Test
    fun `namespaceExists returns true when schema exists`() = runTest {
        every { sqlGenerator.namespaceExists("my_schema") } returns "NAMESPACE EXISTS SQL"
        every { mockStatement.executeQuery("NAMESPACE EXISTS SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean(1) } returns true

        assertTrue(client.namespaceExists("my_schema"))
        verify { sqlGenerator.namespaceExists("my_schema") }
    }

    @Test
    fun `namespaceExists returns false when schema absent`() = runTest {
        every { sqlGenerator.namespaceExists("my_schema") } returns "NAMESPACE EXISTS SQL"
        every { mockStatement.executeQuery("NAMESPACE EXISTS SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean(1) } returns false

        assertFalse(client.namespaceExists("my_schema"))
    }

    @Test
    fun `tableExists returns true when table exists`() = runTest {
        every { sqlGenerator.tableExists(testTable) } returns "TABLE EXISTS SQL"
        every { mockStatement.executeQuery("TABLE EXISTS SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean(1) } returns true

        assertTrue(client.tableExists(testTable))
        verify { sqlGenerator.tableExists(testTable) }
    }

    @Test
    fun `tableExists returns false when table absent`() = runTest {
        every { sqlGenerator.tableExists(testTable) } returns "TABLE EXISTS SQL"
        every { mockStatement.executeQuery("TABLE EXISTS SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean(1) } returns false

        assertFalse(client.tableExists(testTable))
    }

    // ================================================================
    // createTable / dropTable
    // ================================================================

    @Test
    fun `createTable delegates to sqlGenerator with replace`() = runTest {
        val stream = mockStream()
        val columnNameMapping = ColumnNameMapping(mapOf("col" to "col"))
        every { sqlGenerator.createTable(stream, testTable, true) } returns "CREATE TABLE SQL"
        every { mockStatement.execute("CREATE TABLE SQL") } returns true

        client.createTable(stream, testTable, columnNameMapping, replace = true)

        verify { sqlGenerator.createTable(stream, testTable, true) }
    }

    @Test
    fun `createTable delegates to sqlGenerator without replace`() = runTest {
        val stream = mockStream()
        val columnNameMapping = ColumnNameMapping(mapOf("col" to "col"))
        every { sqlGenerator.createTable(stream, testTable, false) } returns "CREATE TABLE SQL"
        every { mockStatement.execute("CREATE TABLE SQL") } returns true

        client.createTable(stream, testTable, columnNameMapping, replace = false)

        verify { sqlGenerator.createTable(stream, testTable, false) }
    }

    @Test
    fun `dropTable delegates to sqlGenerator`() = runTest {
        every { sqlGenerator.dropTable(testTable) } returns "DROP TABLE SQL"
        every { mockStatement.execute("DROP TABLE SQL") } returns true

        client.dropTable(testTable)

        verify { sqlGenerator.dropTable(testTable) }
    }

    // ================================================================
    // overwriteTable / copyTable / upsertTable
    // ================================================================

    @Test
    fun `overwriteTable delegates to sqlGenerator`() = runTest {
        val source = TableName(namespace = "ns", name = "src")
        val target = TableName(namespace = "ns", name = "tgt")
        every { sqlGenerator.overwriteTable(source, target) } returns "OVERWRITE SQL"
        every { mockStatement.execute("OVERWRITE SQL") } returns true

        client.overwriteTable(source, target)

        verify { sqlGenerator.overwriteTable(source, target) }
    }

    @Test
    fun `copyTable delegates to sqlGenerator with ALTER TABLE APPEND`() = runTest {
        val source = TableName(namespace = "ns", name = "src")
        val target = TableName(namespace = "ns", name = "tgt")
        val columnNameMapping = ColumnNameMapping(mapOf("user_col" to "user_col"))

        every { sqlGenerator.copyTable(source, target) } returns "ALTER TABLE APPEND SQL"
        every { mockStatement.execute("ALTER TABLE APPEND SQL") } returns true

        client.copyTable(columnNameMapping, source, target)

        verify { sqlGenerator.copyTable(source, target) }
    }

    @Test
    fun `upsertTable delegates to sqlGenerator`() = runTest {
        val stream = mockDedupStream()
        val source = TableName(namespace = "ns", name = "src")
        val target = TableName(namespace = "ns", name = "tgt")
        val columnNameMapping = ColumnNameMapping(emptyMap())

        every { sqlGenerator.upsertTable(stream, source, target) } returns "UPSERT SQL"
        every { mockStatement.execute("UPSERT SQL") } returns true

        client.upsertTable(stream, columnNameMapping, source, target)

        verify { sqlGenerator.upsertTable(stream, source, target) }
    }

    // ================================================================
    // countTable
    // ================================================================

    @Test
    fun `countTable returns count on success`() = runTest {
        every { sqlGenerator.countTable(testTable) } returns "COUNT SQL"
        every { mockStatement.executeQuery("COUNT SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getLong("total") } returns 42L

        assertEquals(42L, client.countTable(testTable))
    }

    @Test
    fun `countTable returns null on missing table`() = runTest {
        every { sqlGenerator.countTable(testTable) } returns "COUNT SQL"
        every { mockStatement.executeQuery("COUNT SQL") } throws
            SQLException("relation \"test_schema.test_table\" does not exist", "42P01")

        assertNull(client.countTable(testTable))
    }

    @Test
    fun `countTable rethrows non-table-not-found SQLException`() = runTest {
        every { sqlGenerator.countTable(testTable) } returns "COUNT SQL"
        every { mockStatement.executeQuery("COUNT SQL") } throws SQLException("Connection reset")

        assertThrows<SQLException> { client.countTable(testTable) }
    }

    @Test
    fun `countTable returns 0 when empty result set`() = runTest {
        every { sqlGenerator.countTable(testTable) } returns "COUNT SQL"
        every { mockStatement.executeQuery("COUNT SQL") } returns mockResultSet
        every { mockResultSet.next() } returns false

        assertEquals(0L, client.countTable(testTable))
    }

    // ================================================================
    // isTableNotEmpty
    // ================================================================

    @Test
    fun `isTableNotEmpty returns true when table has rows`() = runTest {
        every { sqlGenerator.isTableNotEmpty(testTable) } returns "IS NOT EMPTY SQL"
        every { mockStatement.executeQuery("IS NOT EMPTY SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean("not_empty") } returns true

        assertEquals(true, client.isTableNotEmpty(testTable))
    }

    @Test
    fun `isTableNotEmpty returns false when table is empty`() = runTest {
        every { sqlGenerator.isTableNotEmpty(testTable) } returns "IS NOT EMPTY SQL"
        every { mockStatement.executeQuery("IS NOT EMPTY SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getBoolean("not_empty") } returns false

        assertEquals(false, client.isTableNotEmpty(testTable))
    }

    @Test
    fun `isTableNotEmpty returns null on missing table`() = runTest {
        every { sqlGenerator.isTableNotEmpty(testTable) } returns "IS NOT EMPTY SQL"
        every { mockStatement.executeQuery("IS NOT EMPTY SQL") } throws
            SQLException("relation \"test_schema.test_table\" does not exist", "42P01")

        assertNull(client.isTableNotEmpty(testTable))
    }

    @Test
    fun `isTableNotEmpty rethrows non-table-not-found SQLException`() = runTest {
        every { sqlGenerator.isTableNotEmpty(testTable) } returns "IS NOT EMPTY SQL"
        every { mockStatement.executeQuery("IS NOT EMPTY SQL") } throws
            SQLException("Connection reset")

        assertThrows<SQLException> { client.isTableNotEmpty(testTable) }
    }

    @Test
    fun `isTableNotEmpty returns false on empty result set`() = runTest {
        every { sqlGenerator.isTableNotEmpty(testTable) } returns "IS NOT EMPTY SQL"
        every { mockStatement.executeQuery("IS NOT EMPTY SQL") } returns mockResultSet
        every { mockResultSet.next() } returns false

        assertEquals(false, client.isTableNotEmpty(testTable))
    }

    // ================================================================
    // getGenerationId
    // ================================================================

    @Test
    fun `getGenerationId returns value on success`() = runTest {
        every { sqlGenerator.getGenerationId(testTable) } returns "GEN ID SQL"
        every { mockStatement.executeQuery("GEN ID SQL") } returns mockResultSet
        every { mockResultSet.next() } returns true
        every { mockResultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID) } returns 5L

        assertEquals(5L, client.getGenerationId(testTable))
    }

    @Test
    fun `getGenerationId returns 0 on empty result`() = runTest {
        every { sqlGenerator.getGenerationId(testTable) } returns "GEN ID SQL"
        every { mockStatement.executeQuery("GEN ID SQL") } returns mockResultSet
        every { mockResultSet.next() } returns false

        assertEquals(0L, client.getGenerationId(testTable))
    }

    @Test
    fun `getGenerationId returns 0 on missing table`() = runTest {
        every { sqlGenerator.getGenerationId(testTable) } returns "GEN ID SQL"
        every { mockStatement.executeQuery("GEN ID SQL") } throws
            SQLException("relation \"test_schema.test_table\" does not exist", "42P01")

        assertEquals(0L, client.getGenerationId(testTable))
    }

    @Test
    fun `getGenerationId rethrows non-table-not-found SQLException`() = runTest {
        every { sqlGenerator.getGenerationId(testTable) } returns "GEN ID SQL"
        every { mockStatement.executeQuery("GEN ID SQL") } throws SQLException("Connection reset")

        assertThrows<SQLException> { client.getGenerationId(testTable) }
    }

    // ================================================================
    // execute error handling
    // ================================================================

    @Test
    fun `execute throws ConfigErrorException on dependent objects by sqlState`() {
        val exception = SQLException("cannot drop table", "2BP01")
        every { mockStatement.execute(any<String>()) } throws exception

        val thrown = assertThrows<ConfigErrorException> { client.execute("DROP TABLE something") }
        assertTrue(thrown.message!!.contains("other database objects"))
        assertTrue(thrown.message!!.contains("Drop tables with CASCADE"))
        assertTrue(thrown.message!!.contains("pg_depend"))
    }

    @Test
    fun `execute throws ConfigErrorException on dependent objects by message`() {
        val exception = SQLException("column depends on view xyz")
        every { mockStatement.execute(any<String>()) } throws exception

        val thrown = assertThrows<ConfigErrorException> { client.execute("ALTER TABLE something") }
        assertTrue(thrown.message!!.contains("other database objects"))
        assertTrue(thrown.message!!.contains("Drop tables with CASCADE"))
    }

    @Test
    fun `execute rethrows non-dependent-object errors`() {
        val exception = SQLException("permission denied", "42501")
        every { mockStatement.execute(any<String>()) } throws exception

        assertThrows<SQLException> { client.execute("DROP TABLE something") }
    }

    // ================================================================
    // discoverSchema
    // ================================================================

    @Test
    fun `discoverSchema returns user columns only`() = runTest {
        every { sqlGenerator.getTableSchema(testTable) } returns "GET SCHEMA SQL"
        every { mockStatement.executeQuery("GET SCHEMA SQL") } returns mockResultSet
        // Simulate: _airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta,
        // _airbyte_generation_id, user_col
        every { mockResultSet.next() } returnsMany listOf(true, true, true, true, true, false)
        every { mockResultSet.getString("column_name") } returnsMany
            listOf(
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id",
                "user_col",
            )
        every { mockResultSet.getString("data_type") } returnsMany
            listOf(
                "character varying",
                "timestamp with time zone",
                "super",
                "bigint",
                "character varying",
            )
        every { mockResultSet.getString("is_nullable") } returnsMany
            listOf("NO", "NO", "NO", "NO", "YES")

        val schema = client.discoverSchema(testTable)

        assertEquals(1, schema.columns.size)
        assertTrue(schema.columns.containsKey("user_col"))
        assertEquals("varchar(65535)", schema.columns["user_col"]!!.type)
        assertTrue(schema.columns["user_col"]!!.nullable)
    }

    @Test
    fun `discoverSchema throws ConfigErrorException when meta columns missing`() = runTest {
        every { sqlGenerator.getTableSchema(testTable) } returns "GET SCHEMA SQL"
        every { mockStatement.executeQuery("GET SCHEMA SQL") } returns mockResultSet
        // Simulate: table exists but has no Airbyte columns
        every { mockResultSet.next() } returnsMany listOf(true, false)
        every { mockResultSet.getString("column_name") } returns "user_col"
        every { mockResultSet.getString("data_type") } returns "character varying"
        every { mockResultSet.getString("is_nullable") } returns "YES"

        assertThrows<ConfigErrorException> { client.discoverSchema(testTable) }
    }

    @Test
    fun `discoverSchema returns empty schema when table does not exist`() = runTest {
        every { sqlGenerator.getTableSchema(testTable) } returns "GET SCHEMA SQL"
        every { mockStatement.executeQuery("GET SCHEMA SQL") } returns mockResultSet
        // Simulate: no rows returned = table doesn't exist in information_schema
        every { mockResultSet.next() } returns false

        val schema = client.discoverSchema(testTable)
        assertEquals(TableSchema(emptyMap()), schema)
    }

    // ================================================================
    // computeSchema
    // ================================================================

    @Test
    fun `computeSchema returns stream finalSchema`() {
        val finalSchema =
            mapOf(
                "col_a" to ColumnType("bigint", false),
                "col_b" to ColumnType("varchar(65535)", true),
            )
        val stream = mockStream(finalSchema)
        val columnNameMapping = ColumnNameMapping(mapOf("col_a" to "col_a", "col_b" to "col_b"))

        val schema = client.computeSchema(stream, columnNameMapping)

        assertEquals(finalSchema, schema.columns)
    }

    // ================================================================
    // applyChangeset
    // ================================================================

    @Test
    fun `applyChangeset delegates to matchSchemas when non-empty`() = runTest {
        val stream = mockStream()
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val columnsToAdd = mapOf("new_col" to ColumnType("varchar(65535)", true))
        val changeset =
            ColumnChangeset(
                columnsToAdd = columnsToAdd,
                columnsToDrop = emptyMap(),
                columnsToChange = emptyMap(),
                columnsToRetain = emptyMap(),
            )

        every {
            sqlGenerator.matchSchemas(
                tableName = testTable,
                columnsToAdd = columnsToAdd,
                columnsToModify = emptyMap(),
            )
        } returns "ALTER TABLE SQL"
        every { mockStatement.execute("ALTER TABLE SQL") } returns true

        client.applyChangeset(stream, columnNameMapping, testTable, emptyMap(), changeset)

        verify {
            sqlGenerator.matchSchemas(
                tableName = testTable,
                columnsToAdd = columnsToAdd,
                columnsToModify = emptyMap(),
            )
        }
    }

    @Test
    fun `applyChangeset skips execution when changeset is noop`() = runTest {
        val stream = mockStream()
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val changeset =
            ColumnChangeset(
                columnsToAdd = emptyMap(),
                columnsToDrop = emptyMap(),
                columnsToChange = emptyMap(),
                columnsToRetain = mapOf("existing" to ColumnType("bigint", false)),
            )

        client.applyChangeset(stream, columnNameMapping, testTable, emptyMap(), changeset)

        // Should not call sqlGenerator.matchSchemas or execute anything
        verify(exactly = 0) { sqlGenerator.matchSchemas(any(), any(), any()) }
        verify(exactly = 0) { mockStatement.execute(any<String>()) }
    }

    @Test
    fun `applyChangeset passes type changes to matchSchemas`() = runTest {
        val stream = mockStream()
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val typeChanges =
            mapOf(
                "col" to
                    ColumnTypeChange(
                        originalType = ColumnType("super", true),
                        newType = ColumnType("varchar(65535)", true),
                    ),
            )
        val changeset =
            ColumnChangeset(
                columnsToAdd = emptyMap(),
                columnsToDrop = emptyMap(),
                columnsToChange = typeChanges,
                columnsToRetain = emptyMap(),
            )

        every {
            sqlGenerator.matchSchemas(
                tableName = testTable,
                columnsToAdd = emptyMap(),
                columnsToModify = typeChanges,
            )
        } returns "ALTER TABLE TYPE CHANGE SQL"
        every { mockStatement.execute("ALTER TABLE TYPE CHANGE SQL") } returns true

        client.applyChangeset(stream, columnNameMapping, testTable, emptyMap(), changeset)

        verify {
            sqlGenerator.matchSchemas(
                tableName = testTable,
                columnsToAdd = emptyMap(),
                columnsToModify = typeChanges,
            )
        }
    }

    // ================================================================
    // normalizeRedshiftType
    // ================================================================

    @Test
    fun `normalizeRedshiftType maps character varying`() {
        assertEquals("varchar(65535)", client.normalizeRedshiftType("character varying"))
    }

    @Test
    fun `normalizeRedshiftType maps numeric`() {
        assertEquals("decimal(38,9)", client.normalizeRedshiftType("numeric"))
    }

    @Test
    fun `normalizeRedshiftType maps timestamp without time zone`() {
        assertEquals("timestamp", client.normalizeRedshiftType("timestamp without time zone"))
    }

    @Test
    fun `normalizeRedshiftType maps timestamp with time zone`() {
        assertEquals("timestamptz", client.normalizeRedshiftType("timestamp with time zone"))
    }

    @Test
    fun `normalizeRedshiftType maps time without time zone`() {
        assertEquals("time", client.normalizeRedshiftType("time without time zone"))
    }

    @Test
    fun `normalizeRedshiftType maps time with time zone`() {
        assertEquals("timetz", client.normalizeRedshiftType("time with time zone"))
    }

    @Test
    fun `normalizeRedshiftType passes through known types`() {
        assertEquals("bigint", client.normalizeRedshiftType("bigint"))
        assertEquals("boolean", client.normalizeRedshiftType("boolean"))
        assertEquals("date", client.normalizeRedshiftType("date"))
        assertEquals("super", client.normalizeRedshiftType("super"))
    }

    @Test
    fun `normalizeRedshiftType passes through unknown types`() {
        assertEquals("geometry", client.normalizeRedshiftType("geometry"))
    }

    // ================================================================
    // getMetaColumnNames
    // ================================================================

    @Test
    fun `getMetaColumnNames returns expected meta columns`() {
        val metaNames = client.getMetaColumnNames()

        assertTrue(metaNames.contains(Meta.COLUMN_NAME_AB_RAW_ID))
        assertTrue(metaNames.contains(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(metaNames.contains(Meta.COLUMN_NAME_AB_META))
        assertTrue(metaNames.contains(Meta.COLUMN_NAME_AB_GENERATION_ID))
        assertEquals(4, metaNames.size)
    }

    // ================================================================
    // Helpers
    // ================================================================

    private fun mockStream(
        finalSchema: Map<String, ColumnType> = emptyMap(),
    ): DestinationStream {
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { importType } returns Append
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    private fun mockDedupStream(): DestinationStream {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
            )
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns listOf(listOf("id"))
                every { getCursor() } returns emptyList()
                every { importType } returns
                    Dedupe(
                        primaryKey = listOf(listOf("id")),
                        cursor = emptyList(),
                    )
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    // ================================================================
    // ping
    // ================================================================

    @Test
    fun `ping executes SELECT 1`() = runTest {
        every { mockStatement.execute("SELECT 1") } returns true

        client.ping()

        verify { mockStatement.execute("SELECT 1") }
    }

    // ================================================================
    // copyFromS3
    // ================================================================

    @Test
    fun `copyFromS3 delegates to sqlGenerator and suppresses logging`() = runTest {
        every {
            sqlGenerator.copyFromS3(testTable, "s3://bucket/key", "AKIA", "secret", "us-east-1")
        } returns "COPY SQL"
        every { mockStatement.execute("COPY SQL") } returns false

        client.copyFromS3(testTable, "s3://bucket/key", "AKIA", "secret", "us-east-1")

        verify {
            sqlGenerator.copyFromS3(testTable, "s3://bucket/key", "AKIA", "secret", "us-east-1")
        }
        verify { mockStatement.execute("COPY SQL") }
    }

    // ================================================================
    // addColumn
    // ================================================================

    @Test
    fun `addColumn delegates to sqlGenerator`() = runTest {
        every { sqlGenerator.addColumn(testTable, "new_col", "varchar(65535)") } returns "ALTER SQL"
        every { mockStatement.execute("ALTER SQL") } returns true

        client.addColumn(testTable, "new_col", "varchar(65535)")

        verify { sqlGenerator.addColumn(testTable, "new_col", "varchar(65535)") }
    }

    // ================================================================
    // deleteByRawId
    // ================================================================

    @Test
    fun `deleteByRawId uses PreparedStatement`() = runTest {
        every { sqlGenerator.deleteByRawId(testTable) } returns "DELETE SQL WHERE ? = ?"
        every { mockPreparedStatement.setString(1, "test-raw-id") } returns Unit
        every { mockPreparedStatement.executeUpdate() } returns 1

        client.deleteByRawId(testTable, "test-raw-id")

        verify { mockPreparedStatement.setString(1, "test-raw-id") }
        verify { mockPreparedStatement.executeUpdate() }
    }

    // ================================================================
    // uploadToS3
    // ================================================================

    @Test
    fun `uploadToS3 delegates to s3Client`() = runTest {
        val data = "test".toByteArray()
        every {
            s3Client.putObject(
                any<PutObjectRequest>(),
                any<software.amazon.awssdk.core.sync.RequestBody>()
            )
        } returns PutObjectResponse.builder().build()

        client.uploadToS3("bucket", "key", data)

        verify {
            s3Client.putObject(
                match<PutObjectRequest> { it.bucket() == "bucket" && it.key() == "key" },
                any<software.amazon.awssdk.core.sync.RequestBody>(),
            )
        }
    }

    // ================================================================
    // deleteFromS3
    // ================================================================

    @Test
    fun `deleteFromS3 delegates to s3Client`() = runTest {
        every { s3Client.deleteObject(any<DeleteObjectRequest>()) } returns
            DeleteObjectResponse.builder().build()

        client.deleteFromS3("bucket", "key")

        verify {
            s3Client.deleteObject(
                match<DeleteObjectRequest> { it.bucket() == "bucket" && it.key() == "key" }
            )
        }
    }
}
