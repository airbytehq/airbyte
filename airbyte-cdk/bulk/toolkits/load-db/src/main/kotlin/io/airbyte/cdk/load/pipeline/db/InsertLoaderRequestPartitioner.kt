/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlin.random.Random

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestPartitioner<Q : InsertLoaderRequest>(
    val insertLoader: InsertLoader<Q>,
) :
    OutputPartitioner<
        StreamKey, DestinationRecordRaw, StreamKey, InsertLoaderRequestBuilderAccumulator.Result<Q>
    > {
    private val prng = Random(System.currentTimeMillis())

    override fun getOutputKey(
        inputKey: StreamKey,
        output: InsertLoaderRequestBuilderAccumulator.Result<Q>
    ): StreamKey {
        return inputKey
    }

    override fun getPart(outputKey: StreamKey, inputPart: Int, numParts: Int): Int {
        /**
         * If the partitioning strategy is not random, then by stream/primary key was already
         * applied upstream.
         */
        return when (insertLoader.partitioningStrategy) {
            InsertLoader.PartitioningStrategy.ByStream,
            InsertLoader.PartitioningStrategy.ByPrimaryKey -> inputPart
            InsertLoader.PartitioningStrategy.Random -> prng.nextInt(numParts)
        }
    }
}
