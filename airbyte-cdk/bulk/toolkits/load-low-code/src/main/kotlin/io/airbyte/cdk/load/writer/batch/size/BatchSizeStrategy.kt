package io.airbyte.cdk.load.writer.batch.size


interface BatchSizeStrategy{
    fun isFull(): Boolean
}
