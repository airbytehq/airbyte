/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.pipeline.InputPartitioner
import jakarta.inject.Singleton
import kotlin.random.Random

@Singleton
class S3DataLakePartitioner : InputPartitioner {
    private val random = Random(System.currentTimeMillis())

    override fun getPartition(record: DestinationRecordRaw, numParts: Int): Int {
        if (numParts == 1) {
            return 0
        }

        if (record.stream.importType !is Dedupe) {
            return random.nextInt(numParts)
        }

        val primaryKey = (record.stream.importType as Dedupe).primaryKey
        val jsonData = record.asRawJson()

        val primaryKeyValues =
            primaryKey.map { keys ->
                keys.map { key -> if (jsonData.has(key)) jsonData.get(key) else null }
            }
        return Math.floorMod(primaryKeyValues.hashCode(), numParts)
    }
}
