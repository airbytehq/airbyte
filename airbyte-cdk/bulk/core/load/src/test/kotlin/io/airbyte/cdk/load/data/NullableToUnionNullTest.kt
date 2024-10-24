/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class NullableToUnionNullTest {
    @Test
    fun testBasicBehavior() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(FieldType(StringType, nullable = false))
                .with(
                    FieldType(IntegerType, nullable = true),
                    FieldType(UnionType(listOf(IntegerType, NullType)), nullable = false)
                )
                .build()
        Assertions.assertEquals(NullableToUnionNull().map(inputSchema), expectedOutput)
    }

    @Test
    fun testWackyBehavior() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(FieldType(UnionType(listOf(StringType, IntegerType)), nullable = false))
                .with(
                    FieldType(UnionType(listOf(StringType, IntegerType)), nullable = true),
                    FieldType(
                        UnionType(listOf(UnionType(listOf(StringType, IntegerType)), NullType)),
                        nullable = false
                    )
                )
                .with(FieldType(UnionType(listOf(StringType, NullType)), nullable = false))
                .with(
                    FieldType(UnionType(listOf(StringType, NullType)), nullable = true),
                    FieldType(
                        UnionType(listOf(UnionType(listOf(StringType, NullType)), NullType)),
                        nullable = false
                    )
                )
                .build()
        Assertions.assertEquals(NullableToUnionNull().map(inputSchema), expectedOutput)
    }
}
