package io.airbyte.cdk.load.writer.batch

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.writer.DeclarativeBatchEntryAssembler
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategy
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategyFactory
import io.airbyte.cdk.util.Jsons


// TODO add tests
class JsonResponseBodyBuilder(batchSizeTypeStrategyFactory: BatchSizeStrategyFactory, private val entryAssembler: DeclarativeBatchEntryAssembler, batchField: List<String>):
    ResponseBodyBuilder {
    // Eventually add the ability to provide a template for the body too
    val requestBody: JsonNode
    val batch: ArrayNode
    val batchSizeStrategy: BatchSizeStrategy

    init {
        if (batchField.isEmpty()) {
            requestBody = Jsons.arrayNode()
            batch = requestBody
        } else {
            requestBody = Jsons.objectNode()
            val lastNode = batchField.dropLast(1)
                .fold(requestBody) { accumulator, element ->
                    accumulator.putObject(element)
                }
            batch = lastNode.putArray(batchField.last())
        }

        batchSizeStrategy = batchSizeTypeStrategyFactory.create(requestBody, batchField)
    }

    override fun accumulate(record: DestinationRecordRaw) {
        batch.add(entryAssembler.assemble(record))
    }

    override fun isEmpty(): Boolean {
        return batch.isEmpty
    }

    override fun isFull(): Boolean {
        return batchSizeStrategy.isFull()
    }

    override fun build(): ByteArray {
        return requestBody.serializeToJsonBytes()
    }

}
