/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.schema

import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.integrations.destination.starrocks.spec.StarrocksConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class StarrocksTableSchemaMapperTest {

    private fun mapper(enableJson: Boolean) =
        StarrocksTableSchemaMapper(
            StarrocksConfiguration(
                "h",
                9030,
                8030,
                "u",
                "p",
                "db",
                ssl = false,
                enableJson = enableJson,
                cdcSoftDelete = false,
                loadAsJson = false,
                sslMode = "required",
            ),
            DefaultTempTableNameGenerator(),
        )

    @Test
    fun `object maps to JSON when enable_json is set, STRING otherwise`() {
        assertEquals(
            StarrocksSqlTypes.JSON,
            mapper(enableJson = true).toColumnType(FieldType(ObjectTypeWithoutSchema, false)).type,
        )
        assertEquals(
            StarrocksSqlTypes.STRING,
            mapper(enableJson = false).toColumnType(FieldType(ObjectTypeWithoutSchema, false)).type,
        )
    }

    @Test
    fun `scalar types are unaffected by the json toggle`() {
        val m = mapper(enableJson = true)
        assertEquals(StarrocksSqlTypes.BIGINT, m.toColumnType(FieldType(IntegerType, true)).type)
        assertEquals(StarrocksSqlTypes.DECIMAL, m.toColumnType(FieldType(NumberType, true)).type)
        assertEquals(StarrocksSqlTypes.STRING, m.toColumnType(FieldType(StringType, true)).type)
    }
}
