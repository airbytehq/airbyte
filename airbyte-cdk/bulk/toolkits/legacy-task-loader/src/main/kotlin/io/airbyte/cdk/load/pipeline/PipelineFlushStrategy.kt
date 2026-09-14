/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

interface PipelineFlushStrategy {
    fun shouldFlush(
        inputCount: Long,
        dataAgeMs: Long,
    ): Boolean
}
