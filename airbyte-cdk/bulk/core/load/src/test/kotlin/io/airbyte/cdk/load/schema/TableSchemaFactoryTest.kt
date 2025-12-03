/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.TableName
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class TableSchemaFactoryTest {
    @MockK private lateinit var mapper: TableSchemaMapper

    @MockK private lateinit var colNameResolver: ColumnNameResolver

    @ParameterizedTest
    @MethodSource("schemaTestCases")
    fun `creates correct StreamTableSchema`(
        inputSchema: Map<String, FieldType>,
        importType: ImportType,
        columnNameMapping: Map<String, String>
    ) {
        val factory = TableSchemaFactory(mapper, colNameResolver)
        val finalTableName = TableName("namespace", "table")
        val tempTableName = TableName("namespace", "table_tmp")

        every { mapper.toTempTableName(finalTableName) } returns tempTableName
        every { colNameResolver.getColumnNameMapping(inputSchema.keys) } returns columnNameMapping
        every { mapper.toColumnType(any()) } returns ColumnType("test_type", false)

        val result = factory.make(finalTableName, inputSchema, importType)

        assertEquals(finalTableName, result.tableNames.finalTableName)
        assertEquals(tempTableName, result.tableNames.tempTableName)
        assertEquals(inputSchema, result.columnSchema.inputSchema)
        assertEquals(columnNameMapping, result.columnSchema.inputToFinalColumnNames)
        assertEquals(importType, result.importType)

        val expectedFinalSchema =
            columnNameMapping
                .map { (_, finalName) ->
                    val columnType = ColumnType("test_type", false)
                    finalName to columnType
                }
                .toMap()

        assertEquals(expectedFinalSchema, result.columnSchema.finalSchema)
    }

    companion object {
        @JvmStatic
        fun schemaTestCases(): Stream<Arguments> =
            Stream.of(
                Arguments.of(
                    mapOf(
                        "id" to FieldType(IntegerType, false),
                        "name" to FieldType(StringType, false),
                    ),
                    Append,
                    mapOf("id" to "id_final", "name" to "name_final")
                ),
                Arguments.of(
                    mapOf(
                        "id" to FieldType(IntegerType, false),
                        "name" to FieldType(StringType, false),
                        "updated_at" to FieldType(StringType, false),
                    ),
                    Dedupe(listOf(listOf("id")), listOf("updated_at")),
                    mapOf("id" to "id", "name" to "name", "updated_at" to "updated_at")
                ),
                Arguments.of(emptyMap<String, FieldType>(), Append, emptyMap<String, String>()),
                Arguments.of(
                    mapOf(
                        "id1" to FieldType(IntegerType, false),
                        "id2" to FieldType(IntegerType, false),
                        "data" to FieldType(StringType, false),
                    ),
                    Dedupe(listOf(listOf("id1", "id2")), emptyList()),
                    mapOf("id1" to "id1", "id2" to "id2", "data" to "data")
                ),
                Arguments.of(
                    mapOf("value" to FieldType(StringType, false)),
                    Append,
                    mapOf("value" to "value")
                )
            )
    }
}
