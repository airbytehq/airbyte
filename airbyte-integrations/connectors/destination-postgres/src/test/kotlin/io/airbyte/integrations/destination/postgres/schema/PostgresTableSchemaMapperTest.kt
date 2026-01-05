/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.schema

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.PostgresDataType
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresTableSchemaMapperTest {

    private lateinit var config: PostgresConfiguration
    private lateinit var tempTableNameGenerator: TempTableNameGenerator
    private lateinit var mapper: PostgresTableSchemaMapper

    @BeforeEach
    fun setUp() {
        config = mockk()
        tempTableNameGenerator = mockk()
        mapper = PostgresTableSchemaMapper(config, tempTableNameGenerator)
    }

    @Test
    fun testToFinalTableNameNonLegacy() {
        every { config.legacyRawTablesOnly } returns false
        every { config.schema } returns "public"

        val desc = DestinationStream.Descriptor(name = "Users", namespace = "App")
        val tableName = mapper.toFinalTableName(desc)

        assertEquals("App", tableName.namespace)
        assertEquals("Users", tableName.name)
    }

    @Test
    fun testToFinalTableNameLegacy() {
        every { config.legacyRawTablesOnly } returns true
        every { config.internalTableSchema } returns "airbyte_internal"

        val desc = DestinationStream.Descriptor(name = "Users", namespace = "App")
        val tableName = mapper.toFinalTableName(desc)

        assertEquals("airbyte_internal", tableName.namespace)
        // TypingDedupingUtil.concatenateRawTableName(namespace, name) -> namespace_name
        assertEquals("app_raw__stream_users", tableName.name)
    }

    @Test
    fun testToTempTableName() {
        val tableName = TableName("public", "users")
        val tempTableName = TableName("public", "users_temp")
        every { tempTableNameGenerator.generate(tableName) } returns tempTableName

        assertEquals(tempTableName, mapper.toTempTableName(tableName))
    }

    @Test
    fun testToColumnNameNonLegacy() {
        every { config.legacyRawTablesOnly } returns false
        assertEquals("User_Id", mapper.toColumnName("User Id"))
    }

    @Test
    fun testToColumnNameLegacy() {
        every { config.legacyRawTablesOnly } returns true
        assertEquals("User Id", mapper.toColumnName("User Id"))
    }

    @Test
    fun testToColumnType() {
        assertEquals(ColumnType(PostgresDataType.VARCHAR.typeName, true), mapper.toColumnType(FieldType(StringType, true)))
        assertEquals(ColumnType(PostgresDataType.BIGINT.typeName, false), mapper.toColumnType(FieldType(IntegerType, false)))
        assertEquals(ColumnType(PostgresDataType.BOOLEAN.typeName, true), mapper.toColumnType(FieldType(BooleanType, true)))
    }

    @Test
    fun testToFinalSchemaNonLegacy() {
        every { config.legacyRawTablesOnly } returns false
        val schema = StreamTableSchema(
            tableNames = TableNames(finalTableName = TableName("public", "users")),
            columnSchema = ColumnSchema(mapOf(), mapOf(), mapOf()),
            importType = Append
        )

        assertEquals(schema, mapper.toFinalSchema(schema))
    }

    @Test
    fun testToFinalSchemaLegacy() {
        every { config.legacyRawTablesOnly } returns true
        val schema = StreamTableSchema(
            tableNames = TableNames(finalTableName = TableName("public", "users")),
            columnSchema = ColumnSchema(mapOf(), mapOf(), mapOf()),
            importType = Append
        )

        val finalSchema = mapper.toFinalSchema(schema)

        assertEquals(1, finalSchema.columnSchema.finalSchema.size)
        assertEquals(PostgresDataType.JSONB.typeName, finalSchema.columnSchema.finalSchema[Meta.COLUMN_NAME_DATA]?.type)
    }
}