/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecord.Meta
import java.util.*

fun AirbyteValue.withAirbyteMeta(stream: DestinationStream, record: DestinationRecord) =
    ObjectValue(
        linkedMapOf(
            Meta.COLUMN_NAME_AB_RAW_ID to StringValue(UUID.randomUUID().toString()),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(record.emittedAtMs),
            Meta.COLUMN_NAME_AB_META to
                ObjectValue(
                    linkedMapOf(
                        "sync_id" to IntegerValue(stream.syncId),
                        "changes" to
                            ArrayValue(
                                record.meta?.changes?.map {
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
            Meta.COLUMN_NAME_DATA to this
        )
    )
