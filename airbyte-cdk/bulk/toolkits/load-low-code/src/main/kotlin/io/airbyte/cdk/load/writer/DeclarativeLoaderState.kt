package io.airbyte.cdk.load.writer

import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.InterpolableResponse
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.writer.batch.ResponseBodyBuilder
import io.airbyte.cdk.load.writer.rejected.RejectedRecordsBuilder
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}


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
