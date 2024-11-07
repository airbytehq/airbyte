/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecord.Meta
import java.util.*

class DestinationRecordToAirbyteValueWithMeta(val stream: DestinationStream) {
    fun convert(data: AirbyteValue, emittedAtMs: Long, meta: Meta?): ObjectValue {
        return ObjectValue(
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to StringValue(UUID.randomUUID().toString()),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(emittedAtMs),
                Meta.COLUMN_NAME_AB_META to
                    ObjectValue(
                        linkedMapOf(
                            "sync_id" to IntegerValue(stream.syncId),
                            "changes" to
                                ArrayValue(
                                    meta?.changes?.map {
                                        ObjectValue(
                                            linkedMapOf(
                                                "field" to StringValue(it.field),
                                                "change" to StringValue(it.change.name),
                                                "reason" to StringValue(it.reason.name)
                                            )
                                        )
                                    }
                                        ?: emptyList()
                                )
                        )
                    ),
                Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(stream.generationId),
                Meta.COLUMN_NAME_DATA to data
            )
        )
    }
}

fun Pair<AirbyteValue, List<DestinationRecord.Change>>.withAirbyteMeta(
    stream: DestinationStream,
    emittedAtMs: Long
) = DestinationRecordToAirbyteValueWithMeta(stream).convert(first, emittedAtMs, Meta(second))

fun DestinationRecord.dataWithAirbyteMeta(stream: DestinationStream) =
    DestinationRecordToAirbyteValueWithMeta(stream).convert(data, emittedAtMs, meta)
