/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class AirbyteTypeToAirbyteTypeWithMetaTest {
    private val expectedMeta =
        linkedMapOf(
            Meta.COLUMN_NAME_AB_RAW_ID to FieldType(StringType, nullable = false),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to FieldType(IntegerType, nullable = false),
            Meta.COLUMN_NAME_AB_META to
                FieldType(
                    ObjectType(
                        linkedMapOf(
                            "sync_id" to FieldType(IntegerType, nullable = false),
                            "changes" to
                                FieldType(
                                    ArrayType(
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf(
                                                    "field" to
                                                        FieldType(StringType, nullable = false),
                                                    "change" to
                                                        FieldType(StringType, nullable = false),
                                                    "reason" to
                                                        FieldType(StringType, nullable = false)
                                                )
                                            ),
                                            nullable = false
                                        )
                                    ),
                                    nullable = false
                                )
                        )
                    ),
                    nullable = false
                ),
            Meta.COLUMN_NAME_AB_GENERATION_ID to FieldType(IntegerType, nullable = false)
        )

    @Test
    fun testWithoutFlattening() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "name" to FieldType(StringType, nullable = false),
                    "age" to FieldType(IntegerType, nullable = false),
                    "is_cool" to FieldType(BooleanType, nullable = false)
                )
            )
        val withMeta = schema.withAirbyteMeta(flatten = false)
        val expected = ObjectType(expectedMeta)
        expected.properties[Meta.COLUMN_NAME_DATA] = FieldType(schema, nullable = false)
        assertEquals(expected, withMeta)
    }

    @Test
    fun testWithFlattening() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "name" to FieldType(StringType, nullable = false),
                    "age" to FieldType(IntegerType, nullable = false),
                    "is_cool" to FieldType(BooleanType, nullable = false)
                )
            )
        val withMeta = schema.withAirbyteMeta(flatten = true)
        val expected = ObjectType(expectedMeta)
        schema.properties.forEach { (name, field) -> expected.properties[name] = field }
        assertEquals(expected, withMeta)
    }
}
