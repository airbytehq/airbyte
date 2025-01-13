/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta

class AirbyteTypeToAirbyteTypeWithMeta(private val flatten: Boolean) {
    fun convert(schema: AirbyteType): ObjectType {
        val properties =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to FieldType(StringType, nullable = false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to FieldType(IntegerType, nullable = false),
                Meta.COLUMN_NAME_AB_META to
                    FieldType(
                        nullable = false,
                        type =
                            ObjectType(
                                linkedMapOf(
                                    "sync_id" to FieldType(IntegerType, nullable = false),
                                    "changes" to
                                        FieldType(
                                            nullable = false,
                                            type =
                                                ArrayType(
                                                    FieldType(
                                                        nullable = false,
                                                        type =
                                                            ObjectType(
                                                                linkedMapOf(
                                                                    "field" to
                                                                        FieldType(
                                                                            StringType,
                                                                            nullable = false
                                                                        ),
                                                                    "change" to
                                                                        FieldType(
                                                                            StringType,
                                                                            nullable = false
                                                                        ),
                                                                    "reason" to
                                                                        FieldType(
                                                                            StringType,
                                                                            nullable = false
                                                                        ),
                                                                )
                                                            )
                                                    )
                                                )
                                        )
                                )
                            )
                    ),
                Meta.COLUMN_NAME_AB_GENERATION_ID to FieldType(IntegerType, nullable = false)
            )
        if (flatten) {
            if (schema is ObjectType) {
                schema.properties.forEach { (name, field) -> properties[name] = field }
            } else if (schema is ObjectTypeWithEmptySchema) {
                // Do nothing: no fields to add
            } else {
                throw IllegalStateException(
                    "Cannot flatten without an object schema (schema type: $schema)"
                )
            }
        } else {
            properties[Meta.COLUMN_NAME_DATA] = FieldType(schema, nullable = false)
        }
        return ObjectType(properties)
    }
}

fun AirbyteType.withAirbyteMeta(flatten: Boolean = false): ObjectType =
    AirbyteTypeToAirbyteTypeWithMeta(flatten).convert(this)
