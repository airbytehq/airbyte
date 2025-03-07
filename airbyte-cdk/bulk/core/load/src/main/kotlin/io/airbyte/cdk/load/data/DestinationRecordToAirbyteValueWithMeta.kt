/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import java.util.*

class DestinationRecordToAirbyteValueWithMeta(
    val stream: DestinationStream,
    private val flatten: Boolean
) {
    fun convert(data: AirbyteValue, emittedAtMs: Long, meta: Meta?): ObjectValue {
        val properties =
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
            )
        if (flatten) {
            // Special case: if the top-level schema had no columns, do nothing.
            if (stream.schema !is ObjectTypeWithEmptySchema) {
                properties.putAll((data as ObjectValue).values)
            }
        } else {
            properties[Meta.COLUMN_NAME_DATA] = data
        }
        return ObjectValue(properties)
    }
}

fun Pair<AirbyteValue, List<Meta.Change>>.withAirbyteMeta(
    stream: DestinationStream,
    emittedAtMs: Long,
    flatten: Boolean = false
) =
    DestinationRecordToAirbyteValueWithMeta(stream, flatten)
        .convert(first, emittedAtMs, Meta(second))

fun DestinationRecordAirbyteValue.dataWithAirbyteMeta(
    stream: DestinationStream,
    flatten: Boolean = false
) = DestinationRecordToAirbyteValueWithMeta(stream, flatten).convert(data, emittedAtMs, meta)
