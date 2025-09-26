package io.airbyte.cdk.load.writer.batch.size.memory

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategy
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategyFactory


class RequestMemoryBatchSizeStrategyFactory(private val sizeInBytes: Int): BatchSizeStrategyFactory {
    override fun create(
        requestBody: JsonNode,
        batchField: List<String>
    ): BatchSizeStrategy {
        return RequestMemoryBatchSizeStrategy(requestBody, sizeInBytes)
    }
}


class RequestMemoryBatchSizeStrategy(private val response: JsonNode, private val sizeInBytes: Int): BatchSizeStrategy {
    /**
     * We currently serialize the response as a byte array every time we want to evaluate the size.
     * This is inefficient. We might want to implement some heuristic to approximate that while
     * avoiding the serialization costs.
     */
    override fun isFull(): Boolean {
        return response.serializeToString().toByteArray(Charsets.UTF_8).size > sizeInBytes
    }
}

