/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.Instant
import java.util.*

class AirbyteValueWithMetaToOutputRecord {
    fun convert(value: ObjectValue): OutputRecord {
        val meta = value.values[DestinationRecord.Meta.COLUMN_NAME_AB_META] as ObjectValue
        return OutputRecord(
            rawId =
                UUID.fromString(
                    (value.values[DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID] as StringValue)
                        .value
                ),
            extractedAt =
                Instant.ofEpochMilli(
                    (value.values[DestinationRecord.Meta.COLUMN_NAME_AB_EXTRACTED_AT]
                            as IntegerValue)
                        .value
                ),
            loadedAt = null,
            data = value.values[DestinationRecord.Meta.COLUMN_NAME_DATA] as ObjectValue,
            generationId =
                (value.values[DestinationRecord.Meta.COLUMN_NAME_AB_GENERATION_ID] as IntegerValue)
                    .value,
            airbyteMeta =
                OutputRecord.Meta(
                    syncId = (meta.values["sync_id"] as IntegerValue).value,
                    changes =
                        (meta.values["changes"] as ArrayValue).values.map {
                            DestinationRecord.Change(
                                field = ((it as ObjectValue).values["field"] as StringValue).value,
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
                )
        )
    }
}

fun AirbyteValue.toOutputRecord(): OutputRecord {
    return AirbyteValueWithMetaToOutputRecord().convert(this as ObjectValue)
}
