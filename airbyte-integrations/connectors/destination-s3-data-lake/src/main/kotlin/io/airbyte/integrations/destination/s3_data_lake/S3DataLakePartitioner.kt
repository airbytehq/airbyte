/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.pipeline.InputPartitioner
import jakarta.inject.Singleton
import kotlin.math.abs
import kotlin.random.Random

@Singleton
class S3DataLakePartitioner(catalog: DestinationCatalog) : InputPartitioner {
    private val streamToPrimaryKeyFieldNames =
        catalog.streams.associate { stream ->
            stream.descriptor to
                when (stream.importType) {
                    is Dedupe -> (stream.importType as Dedupe).primaryKey
                    else -> null
                }
        }
    private val random = Random(System.currentTimeMillis())

    override fun getPartition(record: DestinationRecordAirbyteValue, numParts: Int): Int {
        if (numParts == 1) {
            return 0
        }

        streamToPrimaryKeyFieldNames[record.stream]?.let { primaryKey ->
            val primaryKeyValues =
                primaryKey.map { it.map { key -> (record.data as ObjectValue).values[key] } }
            return abs(primaryKeyValues.hashCode()) % numParts
        }
            ?: run {
                return abs(random.nextInt()) % numParts
            }
    }
}
