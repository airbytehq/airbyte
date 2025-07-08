/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.dlq.toDlqRecord
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.BatchEntryAssembler
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.PersonEventBatchEntryAssembler
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.PersonIdentifyBatchEntryAssembler
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.IllegalArgumentException

private val logger = KotlinLogging.logger {}

class CustomerIoState(
    private val httpClient: HttpClient,
    private val entryAssembler: BatchEntryAssembler
) : AutoCloseable {
    val decoder: JsonDecoder = JsonDecoder()
    val requestBody: ObjectNode = Jsons.objectNode()
    val batch: ArrayNode = requestBody.putArray("batch")
    // In order to populate the rejected records list, we need to have the list of records in order
    // of which they are sent to Customer IO as Customer IO flags the errors by index
    val orderedRecords: MutableList<DestinationRecordRaw> = mutableListOf()

    fun accumulate(record: DestinationRecordRaw) {
        orderedRecords.add(record)
        batch.add(entryAssembler.assemble(record))
    }

    fun isFull(): Boolean =
        requestBody.serializeToString().toByteArray(Charsets.UTF_8).size > 500_000

    fun flush(): List<DestinationRecordRaw>? {
        if (batch.isEmpty) {
            logger.info { "No records in batch hence the HTTP request will be performed" }
            return null
        }

        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    url = "https://track.customer.io/api/v2/batch",
                    headers = mapOf("Content-Type" to "application/json"),
                    body = requestBody.serializeToJsonBytes()
                )
            )

        response.use {
            return when (response.statusCode) {
                200 -> null
                207 ->
                    decoder.decode(response.getBodyOrEmpty()).get("errors").asIterable().map {
                        orderedRecords[it.get("batch_index").asInt()].toDlqRecord(
                            mapOf(
                                "rejected_reason" to it.get("reason").asText(),
                                "rejected_field" to it.get("field").asText(),
                                "rejected_message" to it.get("message").asText(),
                            )
                        )
                    }
                else ->
                    throw IllegalStateException(
                        "Invalid response with status code ${response.statusCode} while starting ingestion: ${response.getBodyOrEmpty().reader(Charsets.UTF_8).readText()}"
                    )
            }
        }
    }

    override fun close() {}
}

class CustomerIoLoader(
    private val httpClient: HttpClient,
    private val catalog: DestinationCatalog
) : DlqLoader<CustomerIoState> {
    override fun start(key: StreamKey, part: Int): CustomerIoState {
        logger.info { "CustomerIoLoader.start for ${key.serializeToString()} with part $part" }
        val stream =
            (catalog.streams.find { it.mappedDescriptor == key.stream }
                ?: throw IllegalStateException(
                    "Could not find stream ${key.stream} as part of the catalog."
                ))
        return CustomerIoState(httpClient, selectBatchEntryAssembler(stream))
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: CustomerIoState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: CustomerIoState): DlqLoader.Complete =
        DlqLoader.Complete(state.flush())

    override fun close() {}

    private fun selectBatchEntryAssembler(stream: DestinationStream): BatchEntryAssembler {
        return when (stream.destinationObjectName) {
            "person_event" -> PersonEventBatchEntryAssembler()
            "person_identify" -> PersonIdentifyBatchEntryAssembler()
            else ->
                throw IllegalArgumentException(
                    "Unknown destination object name ${stream.destinationObjectName}"
                )
        }
    }
}
