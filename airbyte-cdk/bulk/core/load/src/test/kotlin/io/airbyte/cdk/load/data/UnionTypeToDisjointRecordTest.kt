/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class UnionTypeToDisjointRecordTest {
    @Test
    fun testBasicSchemaBehavior() {
        val disjointRecord =
            ObjectType(
                linkedMapOf(
                    "type" to FieldType(StringType, nullable = false),
                    "string" to FieldType(StringType, nullable = true),
                    "integer" to FieldType(IntegerType, nullable = true)
                )
            )
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(UnionType.of(StringType)) // union of 1 => ignore
                .with(UnionType.of(StringType, IntegerType), expected = disjointRecord)
                .build()
        val output = UnionTypeToDisjointRecord().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testUnionOfTypesWithSameNameThrows() {
        val (inputSchema, _) =
            SchemaRecordBuilder<Root>()
                // Both are mapped to `string`
                .with(UnionType.of(ObjectTypeWithEmptySchema, ObjectTypeWithoutSchema))
                .build()
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            UnionTypeToDisjointRecord().map(inputSchema)
        }
    }
}
