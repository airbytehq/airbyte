/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.DestinationRecord

class AirbyteTypeToAirbyteTypeWithMeta(private val flatten: Boolean) {
    fun convert(schema: AirbyteType): ObjectType {
        val properties =
            linkedMapOf(
                DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID to
                    FieldType(StringType, nullable = false),
                DestinationRecord.Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    FieldType(IntegerType, nullable = false),
                DestinationRecord.Meta.COLUMN_NAME_AB_META to
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
                DestinationRecord.Meta.COLUMN_NAME_AB_GENERATION_ID to
                    FieldType(IntegerType, nullable = false)
            )
        if (flatten) {
            (schema as ObjectType).properties.forEach { (name, field) -> properties[name] = field }
        } else {
            properties[DestinationRecord.Meta.COLUMN_NAME_DATA] =
                FieldType(schema, nullable = false)
        }
        return ObjectType(properties)
    }
}

fun AirbyteType.withAirbyteMeta(flatten: Boolean = false): ObjectType =
    AirbyteTypeToAirbyteTypeWithMeta(flatten).convert(this)
