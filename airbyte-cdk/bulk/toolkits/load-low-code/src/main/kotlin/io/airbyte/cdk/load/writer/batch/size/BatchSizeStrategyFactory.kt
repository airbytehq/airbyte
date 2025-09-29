package io.airbyte.cdk.load.writer.batch.size

import com.fasterxml.jackson.databind.JsonNode

interface BatchSizeStrategyFactory {
    fun create(requestBody: JsonNode, batchField: List<String>): BatchSizeStrategy
}
