/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.pipeline.ByPrimaryKeyInputPartitioner
import io.airbyte.cdk.load.pipeline.ByStreamInputPartitioner
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.pipeline.RandomInputPartitioner
import io.airbyte.cdk.load.write.db.InsertLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Factory
class InsertLoaderInputPartitionerFactory {
    @Singleton
    @Requires(bean = InsertLoader::class)
    fun insertLoaderInputPartitioner(insertLoader: InsertLoader<*>): InputPartitioner {
        return when (insertLoader.partitioningStrategy) {
            InsertLoader.PartitioningStrategy.ByStream -> ByStreamInputPartitioner()
            InsertLoader.PartitioningStrategy.ByPrimaryKey -> ByPrimaryKeyInputPartitioner()
            InsertLoader.PartitioningStrategy.Random -> RandomInputPartitioner()
        }
    }
}
