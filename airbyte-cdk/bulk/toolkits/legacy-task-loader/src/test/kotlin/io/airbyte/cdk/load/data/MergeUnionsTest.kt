/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

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
    fun testNameClash() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(
                            ObjectType(
                                properties =
                                    linkedMapOf(
                                        "foo" to
                                            FieldType(UnionType.of(StringType, IntegerType), false)
                                    )
                            ),
                            false
                        )
                )
                .withRecord()
                .with(StringType, nameOverride = "foo")
                .endRecord()
                .withRecord()
                .with(IntegerType, nameOverride = "foo")
                .endRecord()
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testMergeLikeTypes() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(UnionType.of(StringType, IntegerType), nullable = false)
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
                        FieldType(UnionType.of(StringType, IntegerType), nullable = false)
                )
                .with(StringType)
                .with(UnionType.of(StringType, UnionType.of(IntegerType, StringType)))
                .with(IntegerType)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testObjectTypeSubsumesObjectTypeWithoutSchema() {
        val concreteObject =
            ObjectType(linkedMapOf("field1" to FieldType(StringType, nullable = true)))
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(expectedInstead = FieldType(concreteObject, nullable = false))
                .with(concreteObject)
                .with(ObjectTypeWithoutSchema)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testObjectTypeSubsumesObjectTypeWithEmptySchema() {
        val concreteObject =
            ObjectType(linkedMapOf("field1" to FieldType(StringType, nullable = true)))
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(expectedInstead = FieldType(concreteObject, nullable = false))
                .with(concreteObject)
                .with(ObjectTypeWithEmptySchema)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testSchemalessObjectVariantsDedup() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(expectedInstead = FieldType(ObjectTypeWithoutSchema, nullable = false))
                .with(ObjectTypeWithoutSchema)
                .with(ObjectTypeWithEmptySchema)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testSchemalessObjectBeforeConcreteObject() {
        val concreteObject =
            ObjectType(linkedMapOf("field1" to FieldType(StringType, nullable = true)))
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(expectedInstead = FieldType(concreteObject, nullable = false))
                .with(ObjectTypeWithoutSchema)
                .with(concreteObject)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testObjectTypeSubsumesAllSchemalessVariants() {
        val concreteObject =
            ObjectType(linkedMapOf("field1" to FieldType(StringType, nullable = true)))
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(expectedInstead = FieldType(concreteObject, nullable = false))
                .with(ObjectTypeWithEmptySchema)
                .with(concreteObject)
                .with(ObjectTypeWithoutSchema)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testSchemalessObjectWithOtherTypes() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withUnion(
                    expectedInstead =
                        FieldType(
                            UnionType.of(StringType, ObjectTypeWithoutSchema),
                            nullable = false
                        )
                )
                .with(StringType)
                .with(ObjectTypeWithoutSchema)
                .with(ObjectTypeWithEmptySchema)
                .endUnion()
                .build()
        val output = MergeUnions().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }
}
