/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class AirbyteTypeToIcebergSchemaTest {
    private val converter = AirbyteTypeToIcebergSchema()

    @Test
    fun `meta schema keeps top-level required fields and relaxes fields inside changes list`() {
        val schema =
            ObjectType(
                    linkedMapOf(
                        Meta.COLUMN_NAME_AB_META to
                            FieldType(Meta.AirbyteMetaFields.META.type, nullable = false),
                        "id" to FieldType(StringType, nullable = false),
                    )
                )
                .toIcebergSchema(emptyList())

        val metaField = schema.findField(Meta.COLUMN_NAME_AB_META)!!
        val metaStruct = metaField.type().asStructType()
        val syncId = metaStruct.field("sync_id")!!
        val changes = metaStruct.field("changes")!!
        val changesList = changes.type().asListType()
        val changeFields = changesList.elementType().asStructType().fields()

        assertThat(metaField.isOptional).isFalse()
        assertThat(syncId.isOptional).isFalse()
        assertThat(changes.isOptional).isFalse()
        assertThat(changesList.isElementOptional).isTrue()
        assertThat(changeFields.map { it.name() }).containsExactly("field", "change", "reason")
        assertThat(changeFields).allMatch { it.isOptional }
    }

    @Test
    fun `array elements are always optional`() {
        val list =
            converter
                .convert(ArrayType(FieldType(StringType, nullable = false)), stringifyObjects = false)
                .asListType()

        assertThat(list.isElementOptional).isTrue()
    }

    @Test
    fun `struct fields recursively inside arrays are optional`() {
        val arrayType =
            ArrayType(
                FieldType(
                    ObjectType(
                        linkedMapOf(
                            "child" to
                                FieldType(
                                    ObjectType(
                                        linkedMapOf(
                                            "value" to FieldType(StringType, nullable = false),
                                        )
                                    ),
                                    nullable = false
                                ),
                            "nested_array" to
                                FieldType(
                                    ArrayType(
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf(
                                                    "nested_value" to
                                                        FieldType(StringType, nullable = false),
                                                )
                                            ),
                                            nullable = false
                                        )
                                    ),
                                    nullable = false
                                ),
                        )
                    ),
                    nullable = false
                )
            )

        val outerList = converter.convert(arrayType, stringifyObjects = false).asListType()
        val outerStruct = outerList.elementType().asStructType()
        val childStruct = outerStruct.field("child")!!.type().asStructType()
        val nestedList = outerStruct.field("nested_array")!!.type().asListType()
        val nestedStruct = nestedList.elementType().asStructType()

        assertThat(outerList.isElementOptional).isTrue()
        assertThat(outerStruct.fields()).allMatch { it.isOptional }
        assertThat(childStruct.fields()).allMatch { it.isOptional }
        assertThat(nestedList.isElementOptional).isTrue()
        assertThat(nestedStruct.fields()).allMatch { it.isOptional }
    }
}
