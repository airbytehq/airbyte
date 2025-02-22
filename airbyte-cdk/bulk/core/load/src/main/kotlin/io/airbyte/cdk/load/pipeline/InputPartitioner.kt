/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlin.math.abs

/**
 * A dev interface for expressing how incoming data is partitioned. By default, data will be
 * partitioned by a hash of the stream name and namespace.
 */
interface InputPartitioner {
    fun getPartition(record: DestinationRecordAirbyteValue, numParts: Int): Int
}

@Singleton
@Secondary
class ByStreamInputPartitioner : InputPartitioner {
    override fun getPartition(record: DestinationRecordAirbyteValue, numParts: Int): Int {
        return abs(record.stream.hashCode()) % numParts
    }
}
