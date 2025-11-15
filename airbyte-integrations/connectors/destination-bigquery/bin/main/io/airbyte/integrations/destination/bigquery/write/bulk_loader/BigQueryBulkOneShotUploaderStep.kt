/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.db.BulkLoaderTableLoader
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import java.io.OutputStream

class BigQueryBulkOneShotUploaderStep<K : WithStream, O : OutputStream>(
    private val bigQueryOneShotUploader: BigQueryBulkOneShotUploader<O>,
    private val taskFactory: LoadPipelineStepTaskFactory,
    override val numWorkers: Int
) : LoadPipelineStep {

    override fun taskForPartition(partition: Int): Task {
        return taskFactory.createFirstStep<
            BigQueryBulkOneShotUploader.BigQueryOneShotUploaderState<O>,
            StreamKey,
            BulkLoaderTableLoader.LoadResult
        >(
            bigQueryOneShotUploader,
            null, // No output partitioner needed - this is the final step
            null, // No output queue needed - this is the final step
            partition,
            numWorkers,
            null
        )
    }
}
