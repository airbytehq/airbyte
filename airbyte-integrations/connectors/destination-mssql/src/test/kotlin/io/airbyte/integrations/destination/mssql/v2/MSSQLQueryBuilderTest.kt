/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MSSQLQueryBuilderTest {

    private fun mockStream(
        namespace: String? = "dbo",
        name: String = "clients_details",
        importType: io.airbyte.cdk.load.command.ImportType = Append,
        extraColumns: LinkedHashMap<String, FieldType> = linkedMapOf(),
    ): DestinationStream {
        val stream = mockk<DestinationStream>(relaxed = true)
        every { stream.mappedDescriptor } returns
            DestinationStream.Descriptor(namespace = namespace, name = name)
        every { stream.importType } returns importType
        every { stream.schema } returns ObjectType(properties = extraColumns)
        return stream
    }

    private fun captureCreateTableSql(builder: MSSQLQueryBuilder): String {
        val connection = mockk<Connection>(relaxed = true)
        val preparedStatement = mockk<PreparedStatement>(relaxed = true)
        every { connection.prepareStatement(any()) } returns preparedStatement

        builder.createTableIfNotExists(connection)

        val sqlStatements = mutableListOf<String>()
        verify(atLeast = 2) { connection.prepareStatement(capture(sqlStatements)) }
        return sqlStatements.last { it.contains("CREATE TABLE") }
    }

    @Test
    fun `CDC append stream types _ab_cdc_deleted_at as VARCHAR(200) instead of VARCHAR(MAX)`() {
        val columns =
            linkedMapOf(
                "id" to FieldType(StringType, true),
                MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT to FieldType(StringType, true),
            )
        val stream = mockStream(importType = Append, extraColumns = columns)
        val builder = MSSQLQueryBuilder(defaultSchema = "dbo", stream = stream)

        assertTrue(builder.hasCdc, "stream with _ab_cdc_deleted_at should be detected as CDC")

        val sql = captureCreateTableSql(builder)

        assertTrue(
            sql.contains("[${MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT}] VARCHAR(200) NULL"),
            "_ab_cdc_deleted_at must be declared as VARCHAR(200) so the secondary index is valid. SQL:\n$sql",
        )
        assertFalse(
            sql.contains("[${MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT}] VARCHAR(MAX) NULL"),
            "_ab_cdc_deleted_at must not be declared as VARCHAR(MAX). SQL:\n$sql",
        )
        assertTrue(
            sql.contains("CREATE  INDEX") &&
                sql.contains("[${MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT}]"),
            "CREATE INDEX on _ab_cdc_deleted_at should still be emitted. SQL:\n$sql",
        )
    }

    @Test
    fun `non-CDC append stream leaves string columns as VARCHAR(MAX)`() {
        val columns = linkedMapOf("id" to FieldType(StringType, true))
        val stream = mockStream(importType = Append, extraColumns = columns)
        val builder = MSSQLQueryBuilder(defaultSchema = "dbo", stream = stream)

        assertFalse(builder.hasCdc)

        val sql = captureCreateTableSql(builder)

        assertTrue(
            sql.contains("[id] VARCHAR(MAX) NULL"),
            "non-indexed string columns should remain VARCHAR(MAX). SQL:\n$sql",
        )
    }

    @Test
    fun `CDC dedupe stream types both primary key and _ab_cdc_deleted_at as VARCHAR(200)`() {
        val columns =
            linkedMapOf(
                "id" to FieldType(StringType, true),
                MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT to FieldType(StringType, true),
            )
        val stream =
            mockStream(
                importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                extraColumns = columns,
            )
        val builder = MSSQLQueryBuilder(defaultSchema = "dbo", stream = stream)

        assertTrue(builder.hasCdc)

        val sql = captureCreateTableSql(builder)

        assertTrue(
            sql.contains("[id] VARCHAR(200) NULL"),
            "dedupe primary key should be VARCHAR(200). SQL:\n$sql",
        )
        assertTrue(
            sql.contains("[${MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT}] VARCHAR(200) NULL"),
            "_ab_cdc_deleted_at should be VARCHAR(200) on CDC dedupe streams. SQL:\n$sql",
        )
    }
}
