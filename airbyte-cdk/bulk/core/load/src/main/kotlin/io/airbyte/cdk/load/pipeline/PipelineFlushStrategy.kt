package io.airbyte.cdk.load.pipeline

interface PipelineFlushStrategy {
    fun shouldFlush(
        inputCount: Long,
    ): Boolean
}
