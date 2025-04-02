/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

interface PipelineFlushStrategy {
    fun shouldFlush(
        inputCount: Long,
    ): Boolean
}
