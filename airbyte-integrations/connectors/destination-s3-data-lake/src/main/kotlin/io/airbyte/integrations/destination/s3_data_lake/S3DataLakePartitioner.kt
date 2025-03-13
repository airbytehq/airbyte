/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordRaw
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

    override fun getPartition(record: DestinationRecordRaw, numParts: Int): Int {
        if (numParts == 1) {
            return 0
        }

        streamToPrimaryKeyFieldNames[record.stream]?.let { primaryKey ->
            val jsonData = record.asRawJson()

            val primaryKeyValues =
                primaryKey.map { keys ->
                    keys.map { key -> if (jsonData.has(key)) jsonData.get(key) else null }
                }
            val hash = primaryKeyValues.hashCode()
            /** abs(MIN_VALUE) == MIN_VALUE, so we need to handle this case separately */
            if (hash == Int.MIN_VALUE) {
                return 0
            }
            return abs(primaryKeyValues.hashCode()) % numParts
        }
            ?: run {
                return abs(random.nextInt()) % numParts
            }
    }
}
