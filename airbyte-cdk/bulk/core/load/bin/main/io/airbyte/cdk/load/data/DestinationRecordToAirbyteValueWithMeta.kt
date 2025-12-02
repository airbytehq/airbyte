/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.getEmittedAtMs
import java.util.*

/**
 * @param flatten whether to promote user-defined fields to the root level. If this is set to
 * `false`, fields defined in `stream.schema` will be left inside an `_airbyte_data` field.
 * @param extractedAtAsTimestampWithTimezone whether to return the `_airbyte_extracted_at` field as
 * an [IntegerValue] or as a [TimestampWithTimezoneValue].
 */
class DestinationRecordToAirbyteValueWithMeta(
    val stream: DestinationStream,
    private val flatten: Boolean,
    private val extractedAtAsTimestampWithTimezone: Boolean,
    private val airbyteRawId: UUID,
) {
    fun convert(
        data: AirbyteValue,
        emittedAtMs: Long,
        meta: Meta?,
    ): ObjectValue {
        val properties =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to StringValue(airbyteRawId.toString()),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    getEmittedAtMs(emittedAtMs, extractedAtAsTimestampWithTimezone),
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
    flatten: Boolean = false,
    extractedAtAsTimestampWithTimezone: Boolean = false,
    airbyteRawId: UUID,
) =
    DestinationRecordToAirbyteValueWithMeta(
            stream = stream,
            flatten = flatten,
            extractedAtAsTimestampWithTimezone = extractedAtAsTimestampWithTimezone,
            airbyteRawId = airbyteRawId,
        )
        .convert(
            first,
            emittedAtMs,
            Meta(second),
        )

fun DestinationRecordAirbyteValue.dataWithAirbyteMeta(
    stream: DestinationStream,
    flatten: Boolean = false,
    extractedAtAsTimestampWithTimezone: Boolean = false,
    airbyteRawId: UUID,
) =
    DestinationRecordToAirbyteValueWithMeta(
            stream = stream,
            flatten = flatten,
            extractedAtAsTimestampWithTimezone = extractedAtAsTimestampWithTimezone,
            airbyteRawId = airbyteRawId,
        )
        .convert(
            data,
            emittedAtMs,
            meta,
        )

fun Meta.Change.toAirbyteValue(): ObjectValue =
    ObjectValue(
        linkedMapOf(
            "field" to StringValue(field),
            "change" to StringValue(change.name),
            "reason" to StringValue(reason.name)
        )
    )

fun List<Meta.Change>.toAirbyteValues(): List<ObjectValue> = map { it.toAirbyteValue() }
