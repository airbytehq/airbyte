/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.pipeline.ByPrimaryKeyInputPartitioner
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class S3DataLakePartitionerFactory {

    @Singleton
    fun s3DataLakeInputPartitioner(): InputPartitioner {
        return ByPrimaryKeyInputPartitioner()
    }
}
