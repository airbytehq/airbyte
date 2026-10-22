/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.UnionType
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
                    ),
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
                .convert(
                    ArrayType(FieldType(StringType, nullable = false)),
                    stringifyObjects = false,
                )
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
                                        ),
                                    ),
                                    nullable = false,
                                ),
                            "nested_array" to
                                FieldType(
                                    ArrayType(
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf(
                                                    "nested_value" to
                                                        FieldType(StringType, nullable = false),
                                                ),
                                            ),
                                            nullable = false,
                                        ),
                                    ),
                                    nullable = false,
                                ),
                        ),
                    ),
                    nullable = false,
                ),
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

    @Test
    fun `STRUCT mode converts declared objects to deeply optional structs`() {
        val schema =
            ObjectType(
                    linkedMapOf(
                        "user" to
                            FieldType(
                                ObjectType(
                                    linkedMapOf(
                                        "id" to FieldType(IntegerType, nullable = false),
                                        "login" to FieldType(StringType, nullable = false),
                                    ),
                                ),
                                nullable = false,
                            ),
                        "labels" to
                            FieldType(
                                ArrayType(
                                    FieldType(
                                        ObjectType(
                                            linkedMapOf(
                                                "id" to FieldType(IntegerType, nullable = false),
                                                "name" to FieldType(StringType, nullable = false),
                                            ),
                                        ),
                                        nullable = false,
                                    ),
                                ),
                                nullable = true,
                            ),
                        "head" to
                            FieldType(
                                ObjectType(
                                    linkedMapOf(
                                        "repo" to
                                            FieldType(
                                                ObjectType(
                                                    linkedMapOf(
                                                        "owner" to
                                                            FieldType(
                                                                ObjectType(
                                                                    linkedMapOf(
                                                                        "login" to
                                                                            FieldType(
                                                                                StringType,
                                                                                nullable = false,
                                                                            ),
                                                                    ),
                                                                ),
                                                                nullable = false,
                                                            ),
                                                    ),
                                                ),
                                                nullable = false,
                                            ),
                                    ),
                                ),
                                nullable = true,
                            ),
                        "reactions" to
                            FieldType(
                                ObjectType(
                                    linkedMapOf(
                                        "+1" to FieldType(IntegerType, nullable = false),
                                    ),
                                ),
                                nullable = true,
                            ),
                        "empty" to FieldType(ObjectType(linkedMapOf()), nullable = true),
                        "union" to
                            FieldType(
                                UnionType(setOf(StringType, IntegerType), isLegacyUnion = false),
                                nullable = true,
                            ),
                        Meta.COLUMN_NAME_AB_META to
                            FieldType(Meta.AirbyteMetaFields.META.type, nullable = false),
                    ),
                )
                .toIcebergSchema(emptyList(), IcebergObjectMode.STRUCT)

        val user = schema.findField("user")!!.type().asStructType()
        val labels = schema.findField("labels")!!.type().asListType().elementType().asStructType()
        val head = schema.findField("head")!!.type().asStructType()
        val repo = head.field("repo")!!.type().asStructType()
        val owner = repo.field("owner")!!.type().asStructType()
        val reactions = schema.findField("reactions")!!.type().asStructType()
        val meta = schema.findField(Meta.COLUMN_NAME_AB_META)!!.type().asStructType()

        assertThat(user.fields().map { it.name() }).containsExactly("id", "login")
        assertThat(labels.fields().map { it.name() }).containsExactly("id", "name")
        assertThat(owner.field("login")).isNotNull
        assertThat(reactions.field("+1")).isNotNull
        assertThat(schema.findField("empty")!!.type()).isEqualTo(Types.StringType.get())
        assertThat(schema.findField("union")!!.type()).isEqualTo(Types.StringType.get())
        assertThat(user.fields()).allMatch { it.isOptional }
        assertThat(labels.fields()).allMatch { it.isOptional }
        assertThat(head.fields()).allMatch { it.isOptional }
        assertThat(repo.fields()).allMatch { it.isOptional }
        assertThat(owner.fields()).allMatch { it.isOptional }
        assertThat(reactions.fields()).allMatch { it.isOptional }

        val metaChanges = meta.field("changes")!!.type().asListType()
        assertThat(schema.findField(Meta.COLUMN_NAME_AB_META)!!.isOptional).isFalse()
        assertThat(meta.field("sync_id")!!.isOptional).isFalse()
        assertThat(metaChanges.isElementOptional).isTrue()
        assertThat(metaChanges.elementType().asStructType().fields()).allMatch { it.isOptional }
    }

    @Test
    fun `JSON_STRING mode keeps user objects as strings`() {
        val schema =
            ObjectType(
                    linkedMapOf(
                        "user" to
                            FieldType(
                                ObjectType(linkedMapOf("login" to FieldType(StringType, true))),
                                nullable = true,
                            ),
                    ),
                )
                .toIcebergSchema(emptyList(), IcebergObjectMode.JSON_STRING)

        assertThat(schema.findField("user")!!.type()).isEqualTo(Types.StringType.get())
    }
}
