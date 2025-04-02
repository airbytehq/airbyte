/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

class RecordCountFlushStrategy(private val recordCount: Long) : PipelineFlushStrategy {
    override fun shouldFlush(inputCount: Long): Boolean {
        return inputCount >= recordCount
    }
}
