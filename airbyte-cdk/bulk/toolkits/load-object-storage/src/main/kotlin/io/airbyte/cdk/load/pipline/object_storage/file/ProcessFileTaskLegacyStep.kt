/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.Task
import jakarta.inject.Singleton

@Singleton
class ProcessFileTaskLegacyStep(private val processFileTaskLegacy: ProcessFileTaskLegacy) :
    LoadPipelineStep {
    override val numWorkers: Int = 1

    override fun taskForPartition(partition: Int): Task {
        return processFileTaskLegacy
    }
}
