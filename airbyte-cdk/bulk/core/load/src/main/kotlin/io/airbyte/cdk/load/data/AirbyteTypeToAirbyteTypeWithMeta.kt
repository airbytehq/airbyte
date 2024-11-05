/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.DestinationRecord

fun AirbyteType.withAirbyteMeta(): ObjectType =
    ObjectType(
        linkedMapOf(
            DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID to FieldType(StringType, nullable = false),
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
                FieldType(IntegerType, nullable = false),
            DestinationRecord.Meta.COLUMN_NAME_DATA to FieldType(this, nullable = false),
        )
    )
