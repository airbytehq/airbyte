/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.Instant
import java.util.UUID

class AirbyteValueWithMetaToOutputRecord(val extractedAtType: ExtractedAtType) {
    fun convert(value: ObjectValue): OutputRecord {
        val meta = value.values[Meta.COLUMN_NAME_AB_META] as ObjectValue
        return OutputRecord(
            rawId =
                UUID.fromString((value.values[Meta.COLUMN_NAME_AB_RAW_ID] as StringValue).value),
            extractedAt =
                // extracted at should always be nonnull.
                extractedAtType.parseValue(value.values[Meta.COLUMN_NAME_AB_EXTRACTED_AT]!!),
            loadedAt = null,
            data = value.values[Meta.COLUMN_NAME_DATA] as ObjectValue,
            generationId =
                (value.values[Meta.COLUMN_NAME_AB_GENERATION_ID] as IntegerValue).value.toLong(),
            airbyteMeta =
                OutputRecord.Meta(
                    syncId = (meta.values["sync_id"] as IntegerValue).value.toLong(),
                    changes =
                        (meta.values["changes"] as ArrayValue)
                            .values
                            .map {
                                Meta.Change(
                                    field =
                                        ((it as ObjectValue).values["field"] as StringValue).value,
                                    change =
                                        AirbyteRecordMessageMetaChange.Change.fromValue(
                                            (it.values["change"] as StringValue).value
                                        ),
                                    reason =
                                        AirbyteRecordMessageMetaChange.Reason.fromValue(
                                            (it.values["reason"] as StringValue).value
                                        )
                                )
                            }
                            .toMutableList()
                )
        )
    }
}

fun AirbyteValue.maybeUnflatten(wasFlattened: Boolean): ObjectValue {
    this as ObjectValue
    if (!wasFlattened) {
        return this
    }
    val (meta, data) = this.values.toList().partition { Meta.COLUMN_NAMES.contains(it.first) }
    val properties = LinkedHashMap(meta.toMap())
    val dataObject = ObjectValue(LinkedHashMap(data.toMap()))
    properties[Meta.COLUMN_NAME_DATA] = dataObject
    return ObjectValue(properties)
}

enum class ExtractedAtType {
    TIMESTAMP_WITH_TIMEZONE {
        override fun parseValue(value: AirbyteValue): Instant {
            if (value is TimestampWithTimezoneValue) {
                return value.value.toInstant()
            } else {
                throw IllegalArgumentException("Invalid extractedAt value: $value")
            }
        }
    },
    INTEGER {
        override fun parseValue(value: AirbyteValue): Instant {
            if (value is IntegerValue) {
                return Instant.ofEpochMilli(value.value.toLong())
            } else {
                throw IllegalArgumentException("Invalid extractedAt value: $value")
            }
        }
    };

    abstract fun parseValue(value: AirbyteValue): Instant
}

fun AirbyteValue.toOutputRecord(extractedAtType: ExtractedAtType): OutputRecord {
    return AirbyteValueWithMetaToOutputRecord(extractedAtType).convert(this as ObjectValue)
}
