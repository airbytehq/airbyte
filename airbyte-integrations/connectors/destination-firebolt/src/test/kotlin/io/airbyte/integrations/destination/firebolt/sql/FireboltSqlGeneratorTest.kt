/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.mockk.every
import io.mockk.mockk

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class FireboltSqlGeneratorTest {

    private lateinit var sqlGenerator: FireboltSqlGenerator

    @BeforeEach
    fun setUp() {
        sqlGenerator = FireboltSqlGenerator()
    }

    @Test
    fun `createNamespace generates CREATE SCHEMA`() {
        val sql = sqlGenerator.createNamespace("my_schema")
        assertEquals("""CREATE SCHEMA IF NOT EXISTS "my_schema"""", sql)
    }

    @Test
    fun `tableExists queries information_schema`() {
        val sql = sqlGenerator.tableExists(TableName(namespace = "my_schema", name = "my_table"))
        assertTrue(sql.contains("SELECT EXISTS("))
        assertTrue(sql.contains("FROM information_schema.tables"))
        assertTrue(sql.contains("table_schema = 'my_schema'"))
        assertTrue(sql.contains("table_name = 'my_table'"))
    }

    @Test
    fun `dropTable drops qualified table`() {
        val sql = sqlGenerator.dropTable(TableName(namespace = "my_schema", name = "my_table"))
        assertEquals("""DROP TABLE IF EXISTS "my_schema"."my_table"""", sql)
    }

    @Test
    fun `copyTable inserts from source to target`() {
        val sql =
            sqlGenerator.copyTable(
                sourceTableName = TableName(namespace = "my_schema", name = "source"),
                targetTableName = TableName(namespace = "my_schema", name = "target"),
            )
        assertTrue(sql.contains("INSERT INTO \"my_schema\".\"target\""))
        assertTrue(sql.contains("SELECT * FROM \"my_schema\".\"source\""))
    }

    @Test
    fun `copyFromS3 generates COPY command with static credentials`() {
        val sql =
            sqlGenerator.copyFromS3(
                TableName(namespace = "my_schema", name = "my_table"),
                s3Path = "s3://my-bucket/prefix/data.csv.gz",
                accessKeyId = "AKIA",
                secretAccessKey = "secret",
            )
        assertTrue(sql.contains("""COPY INTO "my_schema"."my_table""".trim()))
        assertTrue(sql.contains("TYPE = CSV"))
        assertTrue(sql.contains("HEADER = TRUE"))
        assertTrue(sql.contains("AWS_ACCESS_KEY_ID = 'AKIA'"))
        assertTrue(sql.contains("AWS_SECRET_ACCESS_KEY = 'secret'"))
    }

    @Test
    fun `createTable includes meta and user columns`() {
        val sql = sqlGenerator.createTable(
            stream = mockAppendStream(
                finalSchema = mapOf("id" to ColumnType("bigint", false), "name" to ColumnType("text", true))
            ),
            tableName = TableName(namespace = "my_schema", name = "my_table")
        )
        assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
        assertTrue(sql.contains(""""_airbyte_raw_id" text"""))
        assertTrue(sql.contains(""""_airbyte_extracted_at" timestamptz"""))
        assertTrue(sql.contains(""""_airbyte_meta" text"""))
        assertTrue(sql.contains(""""_airbyte_generation_id" bigint"""))
        assertTrue(sql.contains(""""id" bigint NOT NULL"""))
        assertTrue(sql.contains(""""name" text"""))
    }

    @Test
    fun `upsertTable requires a primary key`() {
        assertThrows(IllegalArgumentException::class.java) {
            sqlGenerator.upsertTable(
                stream = mockDedupeStream(
                    finalSchema = mapOf("id" to ColumnType("bigint", false)),
                    primaryKey = emptyList(),
                ),
                sourceTableName = TableName(namespace = "my_schema", name = "source"),
                targetTableName = TableName(namespace = "my_schema", name = "target"),
            )
        }
    }

    @Test
    fun `upsertTable generates a MERGE with dedup and update conditions`() {
        val sql =
            sqlGenerator.upsertTable(
                stream = mockDedupeStream(
                    finalSchema = mapOf("id" to ColumnType("bigint", false), "value" to ColumnType("text", true)),
                    primaryKey = listOf(listOf("id")),
                    cursor = listOf("value"),
                ),
                sourceTableName = TableName(namespace = "my_schema", name = "source"),
                targetTableName = TableName(namespace = "my_schema", name = "target"),
            )
        assertTrue(sql.contains("MERGE INTO \"my_schema\".\"target\" AS t"))
        assertTrue(sql.contains("USING ("))
        assertTrue(sql.contains("ROW_NUMBER() OVER ("))
        assertTrue(sql.contains("WHEN MATCHED"))
        assertTrue(sql.contains("UPDATE SET *"))
        assertTrue(sql.contains("WHEN NOT MATCHED"))
        assertTrue(sql.contains("INSERT *"))
    }

    private fun mockAppendStream(finalSchema: Map<String, ColumnType>): DestinationStream {
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns emptyList()
                every { getCursor() } returns emptyList()
                every { importType } returns Append
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    private fun mockDedupeStream(
        finalSchema: Map<String, ColumnType>,
        inputSchema: Map<String, FieldType> = emptyMap(),
        primaryKey: List<List<String>>,
        cursor: List<String> = emptyList(),
    ): DestinationStream {
        val columnSchema = ColumnSchema(inputSchema, emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns primaryKey
                every { getCursor() } returns cursor
                every { importType } returns Dedupe(primaryKey = primaryKey, cursor = cursor)
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }
}
