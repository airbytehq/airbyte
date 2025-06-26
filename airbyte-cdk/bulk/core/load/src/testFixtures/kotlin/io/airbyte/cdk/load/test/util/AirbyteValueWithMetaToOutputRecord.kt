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

class AirbyteValueWithMetaToOutputRecord {
    fun convert(value: ObjectValue): OutputRecord {
        val meta = value.values[Meta.COLUMN_NAME_AB_META] as ObjectValue
        return OutputRecord(
            rawId =
                UUID.fromString((value.values[Meta.COLUMN_NAME_AB_RAW_ID] as StringValue).value),
            extractedAt =
                Instant.ofEpochMilli(
                    value.values[Meta.COLUMN_NAME_AB_EXTRACTED_AT].let { v ->
                        when (v) {
                            is IntegerValue -> v.value.toLong()
                            is TimestampWithTimezoneValue -> v.value.toEpochSecond()
                            else -> throw IllegalArgumentException("Invalid extractedAt value: $v")
                        }
                    }
                ),
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

fun AirbyteValue.toOutputRecord(): OutputRecord {
    return AirbyteValueWithMetaToOutputRecord().convert(this as ObjectValue)
}
