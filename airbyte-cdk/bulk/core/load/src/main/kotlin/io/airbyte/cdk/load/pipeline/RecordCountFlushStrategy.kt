package io.airbyte.cdk.load.pipeline

class RecordCountFlushStrategy(
    private val recordCount: Long
): PipelineFlushStrategy {
    override fun shouldFlush(inputCount: Long): Boolean {
        return inputCount >= recordCount
    }
}
