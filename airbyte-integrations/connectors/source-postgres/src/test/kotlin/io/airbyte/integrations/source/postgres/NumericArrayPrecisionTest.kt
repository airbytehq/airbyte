/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.integrations.source.postgres.operations.PostgresSourceFieldTypeMapper
import java.sql.JDBCType
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class NumericArrayPrecisionTest {

    private val mapper = PostgresSourceFieldTypeMapper()

    // pgjdbc reports the array's own precision and scale, not those of its elements.
    private val numericArrayColumn =
        JdbcMetadataQuerier.ColumnMetadata(
            name = "c",
            label = "c",
            type =
                SystemType(
                    typeName = "_numeric",
                    typeCode = JDBCType.ARRAY.vendorTypeNumber,
                    precision = 0,
                    scale = 0,
                ),
        )

    private fun fieldTypeForTypmod(typmod: Int?) =
        mapper.toFieldType(
            PostgresSourceMetadataQuerier.withNumericArrayElementPrecision(
                numericArrayColumn,
                typmod,
            )
        )

    @Test
    fun `typmod decodes to precision and scale`() {
        // Values of pg_attribute.atttypmod observed on Postgres 16.
        assertEquals(20 to 0, PostgresSourceMetadataQuerier.numericPrecisionAndScale(1310724))
        assertEquals(10 to 0, PostgresSourceMetadataQuerier.numericPrecisionAndScale(655364))
        assertEquals(20 to 9, PostgresSourceMetadataQuerier.numericPrecisionAndScale(1310733))
        assertEquals(0 to 0, PostgresSourceMetadataQuerier.numericPrecisionAndScale(-1))
        assertEquals(0 to 0, PostgresSourceMetadataQuerier.numericPrecisionAndScale(null))
    }

    @Test
    fun `numeric array with zero scale is an array of integers`() {
        assertEquals(ArrayFieldType(BigIntegerFieldType), fieldTypeForTypmod(1310724))
        assertEquals(ArrayFieldType(BigIntegerFieldType), fieldTypeForTypmod(655364))
    }

    @Test
    fun `numeric array with nonzero scale is an array of decimals`() {
        assertEquals(ArrayFieldType(BigDecimalFieldType), fieldTypeForTypmod(1310733))
    }

    @Test
    fun `unconstrained numeric array is an array of decimals`() {
        assertEquals(ArrayFieldType(BigDecimalFieldType), fieldTypeForTypmod(-1))
        assertEquals(ArrayFieldType(BigDecimalFieldType), fieldTypeForTypmod(null))
    }
}
