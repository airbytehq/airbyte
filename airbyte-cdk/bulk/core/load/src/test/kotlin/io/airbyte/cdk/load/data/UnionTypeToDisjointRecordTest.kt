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
        val disjoinRecord =
            ObjectType(
                linkedMapOf(
                    "type" to FieldType(StringType, nullable = false),
                    "string" to FieldType(StringType, nullable = true),
                    "integer" to FieldType(IntegerType, nullable = true)
                )
            )
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(UnionType(listOf(StringType))) // union of 1 => ignore
                .with(UnionType(listOf(StringType, NullType))) // union of 1 w/ null => ignore
                .with(
                    UnionType(listOf(StringType, IntegerType)),
                    expected = disjoinRecord
                ) // union of 2 => disjoint
                .with(
                    UnionType(listOf(StringType, IntegerType, NullType)),
                    expected = UnionType(listOf(NullType, disjoinRecord))
                ) // union of 2 w/ null => disjoint
                .build()
        val output = UnionTypeToDisjointRecord().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testUnionOfTypesWithSameNameThrows() {
        val (inputSchema, _) =
            SchemaRecordBuilder<Root>()
                .with(UnionType(listOf(ObjectType(linkedMapOf()), ObjectTypeWithoutSchema)))
                .build()
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            UnionTypeToDisjointRecord().map(inputSchema)
        }
    }
}
