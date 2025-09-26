package io.airbyte.cdk.load.writer

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.discoverer.operation.extractArray
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.InterpolableResponse
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.writer.rejected.RejectedRecordsBuilder
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

interface ResponseBodyBuilder {
    fun accumulate(record: DestinationRecordRaw)
    fun isEmpty(): Boolean
    fun isFull(): Boolean
    fun build(): ByteArray
}

interface BatchSizeStrategyFactory{
    fun create(requestBody: JsonNode, batchField: List<String>): BatchSizeStrategy
}

class RequestMemoryBatchSizeStrategyFactory(private val sizeInBytes: Int): BatchSizeStrategyFactory {
    override fun create(
        requestBody: JsonNode,
        batchField: List<String>
    ): BatchSizeStrategy {
        return RequestMemoryBatchSizeStrategy(requestBody, sizeInBytes)
    }
}

class JsonResponseBodyBuilder(batchSizeTypeStrategyFactory: BatchSizeStrategyFactory, private val entryAssembler: DeclarativeBatchEntryAssembler, batchField: List<String>): ResponseBodyBuilder {
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
        return batch.size() <= 0
    }

    override fun isFull(): Boolean {
        return batchSizeStrategy.isFull()
    }

    override fun build(): ByteArray {
        return requestBody.serializeToJsonBytes()
    }

}

interface BatchSizeStrategy{
    fun isFull(): Boolean
}


// TODO add unit tests
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


class RecordNumberBatchSizeStrategy(response: JsonNode, private val numberOfRecords: Int, batchField: List<String>): BatchSizeStrategy {
    val batch: ArrayNode = response.extractArray(batchField)

    override fun isFull(): Boolean {
        return batch.size() > numberOfRecords
    }
}

interface RejectedRecordStrategy

class BatchIndexRejectedRecordStrategy: RejectedRecordStrategy


class DeclarativeLoaderState(
    private val httpRequester: HttpRequester,
    private val responseBodyBuilder: ResponseBodyBuilder,
    private val rejectedRecordsBuilder: RejectedRecordsBuilder,
    private val responseDecoder: JsonDecoder = JsonDecoder()
) : AutoCloseable {

    // TODO notify RejectedRecordStrategy of a new record
    fun accumulate(record: DestinationRecordRaw) {
        responseBodyBuilder.accumulate(record)
        rejectedRecordsBuilder.accumulate(record)
    }

    fun isFull(): Boolean = responseBodyBuilder.isFull()

    fun flush(): List<DestinationRecordRaw>? {
        if (responseBodyBuilder.isEmpty()) {
            logger.info { "No records in batch hence the HTTP request will be performed" }
            return null
        }

        val response: Response = httpRequester.send(body = responseBodyBuilder.build())

        response.use {
            return rejectedRecordsBuilder.getRejectedRecords(toInterpolableResponse(response))
        }
    }

    override fun close() {}

    private fun toInterpolableResponse(response: Response): InterpolableResponse {
        return InterpolableResponse(
            response.statusCode,
            response.headers,
            responseDecoder.decode(response.getBodyOrEmpty()),
        )
    }
}
