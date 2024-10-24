/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class MergeUnionsTest {
    @Test
    fun testBasicBehavior() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(
                            ObjectType(
                                properties =
                                    linkedMapOf(
                                        "foo" to FieldType(StringType, false),
                                        "bar" to FieldType(IntegerType, false)
                                    )
                            ),
                            nullable = false
                        )
                )
                .withRecord()
                .with(StringType, nameOverride = "foo")
                .endRecord()
                .withRecord()
                .with(IntegerType, nameOverride = "bar")
                .endRecord()
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testNameClashFails() {
        val (inputSchema, _) =
            SchemaRecordBuilder<Root>()
                .withUnion()
                .withRecord()
                .with(StringType, nameOverride = "foo")
                .endRecord()
                .withRecord()
                .with(IntegerType, nameOverride = "foo")
                .endRecord()
                .endUnion()
                .build()
        assertThrows<IllegalArgumentException> { MergeUnions().map(inputSchema) }
    }

    @Test
    fun testMergeLikeTypes() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(UnionType(listOf(StringType, IntegerType)), nullable = false)
                )
                .with(StringType)
                .with(IntegerType)
                .with(IntegerType)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testNestedUnion() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(UnionType(listOf(StringType, IntegerType)), nullable = false)
                )
                .with(StringType)
                .with(UnionType(listOf(StringType, UnionType(listOf(IntegerType, StringType)))))
                .with(IntegerType)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }
}
